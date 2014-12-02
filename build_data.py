import sys
import os
import time
from datetime import datetime
import logging
import logging.handlers
from operator import itemgetter
from config import CONFIG
import arcpy
from pprint import pprint
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from addrparse.addrparse import Parser


'''
CONFIG
'''

FILE_GDB = CONFIG['file_gdb']
debug_cfg = CONFIG['debug']
TIMED_ROW_INTERVAL = debug_cfg['timed_row_interval']
MAX_ROWS = debug_cfg['max_rows']

# Input
input_cfg = CONFIG['input']
ADDRESS_PT = '{}/{}'.format(FILE_GDB, input_cfg['address_pt'])
STREETS_LIN = '{}/{}'.format(FILE_GDB, input_cfg['streets_lin'])
STREETS_FIELDS = input_cfg['streets_fields']
CURBS_PLY = '{}/{}'.format(FILE_GDB, input_cfg['curbs_ply'])

# Output
output_cfg = CONFIG['output']
OUTPUT_DIR = output_cfg['dir']
CONSTR_LIN_NAME = '{}_{}'.format(output_cfg['constr_lin'], int(time.time()))
CONSTR_LIN = '{}/{}'.format(FILE_GDB, CONSTR_LIN_NAME)
# STREETSIDE_PT = '{}/{}'.format(FILE_GDB, output_cfg['curb_pt'])

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
	os.makedirs(OUTPUT_DIR)


'''
LOGGING
'''

logging_cfg = CONFIG['logging']
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

LOG_FILE = '{}/error.log'.format(OUTPUT_DIR)
MAX_BYTES = logging_cfg['max_bytes']
BACKUP_COUNT = logging_cfg['backup_count']
FILE_LOG_LEVEL = logging_cfg['file_level']
fh = logging.handlers.RotatingFileHandler(LOG_FILE, 'a', MAX_BYTES, BACKUP_COUNT)
fh.setLevel(getattr(logging, FILE_LOG_LEVEL))
fh.setFormatter(formatter)
logger.addHandler(fh)

CONSOLE_LOG_LEVEL = logging_cfg['console_level']
ch = logging.StreamHandler()
ch.setLevel(getattr(logging, CONSOLE_LOG_LEVEL))
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Starting script...')


'''
UTILITY FUNCTIONS
'''

def point_to_shapely(geom):
	addr_pt = geom.getPart()
	return Point((addr_pt.X, addr_pt.Y,))

def parity(num):
	if num % 2 == 0:
		return 'E'
	return 'O'

def parity_for_range(low, high):
	# Handle null ranges
	if high == 0:
		return 'U'
	parity_low = parity(low)
	if parity_low == parity(high):
		return parity_low
	return 'B'


'''
ADDRESS PARSER
'''

# Create address parser
parser = Parser(return_dict=True)

# This takes a dict of address components and reforms the full street name
# ex. 123 Addison Street => ADDISON ST
def street_full_from_comps(addr):
	addr_concat = ''
	if addr['predir']: addr_concat += '{} '.format(addr['predir'])
	addr_concat += '{}'.format(addr['streetname'])
	if addr['suffix']: addr_concat += ' {}'.format(addr['suffix'])
	if addr['postdir']: addr_concat += ' {}'.format(addr['postdir'])

	return addr_concat


'''
CREATE DATA LAYERS
'''

logger.info('Creating data layers...')
timestamp = int(time.time())

streetside_file_path = '{}/curb_pt_{}.csv'.format(OUTPUT_DIR, timestamp)
streetside_file = open(streetside_file_path, 'w')
streetside_file.write('ADDRESS_ID,X,Y,PRIMARY_NUM_STD,PREDIR_STD,STREET_NAME_STD,SUFFIX_STD,POSTDIR_STD\n')

# Construction lines
# if arcpy.Exists(CONSTR_LIN):
# 	arcpy.Delete_management(CONSTR_LIN)
arcpy.CreateFeatureclass_management(FILE_GDB, CONSTR_LIN_NAME, 'POLYLINE', '', '', '', ADDRESS_PT)
arcpy.AddField_management(CONSTR_LIN, 'ADDRESS_ID', 'LONG')
arcpy.AddField_management(CONSTR_LIN, 'EXACT_MATCH', 'SHORT')


'''
READ CENTERLINES

Read all centerlines into memory to reduce I/O latency.
'''

logging.info("Reading street centerlines...")

# BUILD MASTER
cl_master = []
cl_fields = ['OID@', 'SHAPE@']
# Append user-specified field names
street_name_field = input_cfg['streets_fields']['street_name']
cl_fields_cfg = ['left_from', 'left_to', 'right_from', 'right_to',]
cl_fields += [street_name_field] + [input_cfg['streets_fields'][x] for x in cl_fields_cfg]
cl_master_rows = arcpy.da.SearchCursor(STREETS_LIN, cl_fields)

# Loop over centerlines
for cl_master_row in cl_master_rows:
	new_row = dict(zip(cl_fields, cl_master_row))
	
	# Get address comps
	street_name = new_row[street_name_field]
	street_name_comps = parser.parse(street_name)

	# Standardize and include address comps
	new_row['PREDIR_STD'] = street_name_comps['predir']
	new_row['STREET_NAME_STD'] = street_name_comps['streetname']
	new_row['SUFFIX_STD'] = street_name_comps['suffix']
	new_row['POSTDIR_STD'] = street_name_comps['postdir']

	street_full_std = street_full_from_comps(street_name_comps)
	new_row['STREET_FULL_STD'] = street_full_std

	# Find parity of left, right
	new_row['PARITY_LEFT'] = parity_for_range(new_row['L_F_ADD'], new_row['L_T_ADD'])
	new_row['PARITY_RIGHT'] = parity_for_range(new_row['R_F_ADD'], new_row['R_T_ADD'])

	# Add
	cl_master.append(new_row)

# Build street lookup object
# street_full_std => [object_ids]

cl_name_objects = {}

for cl in cl_master:
	street_full_std = cl['STREET_FULL_STD']
	if not street_full_std in cl_name_objects:
		cl_name_objects[street_full_std] = []

	cl_name_objects[street_full_std].append(cl['OID@'])

def centerlines_for_name(name):
	'''
	Get centerlines dicts for a standardized street name.
	'''

	try:
		oids = cl_name_objects[name]
		return [x for x in cl_master if x['OID@'] in oids]
	except:

		return None

'''
READ CURBS
'''

logger.info("Reading curbs...")

curb_rows = arcpy.da.SearchCursor(CURBS_PLY, ('OID@', 'SHAPE@',))
curbs = {x[0]: x[1] for x in curb_rows}


'''
WRITE BUFFERS

These store data objects until they're ready to be written out in bulk.
'''

constr_buffer = []


'''
STATS
'''

addr_row_count = 1
log_stats_start = None
log_stats = False


'''
ADDRESS POINTS
'''

logger.info("Reading master address layer...")

addr_fields = ['SHAPE@']
addr_fields_cfg = ['address_id', 'address_full', 'poly_id']
addr_fields += [input_cfg['address_fields'][x] for x in addr_fields_cfg]
addr_rows_cursor = arcpy.da.SearchCursor(ADDRESS_PT, addr_fields)
addr_rows = [list(x) for x in addr_rows_cursor]

# Add standardized street string
for addr_row in addr_rows:
	addr_full = addr_row[2]
	comps = parser.parse(addr_full)
	street_full_std = street_full_from_comps(comps)
	addr_row += [street_full_std, comps]

# Sort
addr_rows = sorted(addr_rows, key=itemgetter(4))

last_addr_street_full = None
cl_rows = None

logger.info("Processing addresses...")

# Loop over master address rows
for addr_row in addr_rows:
	try:
		# Use function timers
		# timed_run = True if addr_row_count % TIMED_RUN_INTERVAL == 0 else False
		
		# Write row count and duration (this happens at the end)
		if addr_row_count % TIMED_ROW_INTERVAL == 0:
			log_stats = True
			log_stats_start = time.clock()

		if MAX_ROWS > 0 and addr_row_count == MAX_ROWS:
			break

		# Read address row data
		addr_geom = addr_row[0]
		addr_id = addr_row[1]
		addr_str = addr_row[2]
		poly_id = addr_row[3]

		# Parse address string and reconcatenate
		addr_street_full = addr_row[4]
		addr_std_comps = addr_row[5]
		addr_num = addr_std_comps['addr']['addrnumlow']

		if addr_num == 0:
			raise Exception('Addr num 0')

		# Make Shapely address point
		addr_pt_sh = point_to_shapely(addr_geom)

		# Check if addr point was not joined to a polygon
		if not poly_id:
			raise Exception('No poly ID')


		'''
		FIND MATCHING CENTERLINE
		'''
		
		# Get CL objects
		if last_addr_street_full != addr_street_full:
			cl_rows = centerlines_for_name(addr_street_full)
			last_addr_street_full = addr_street_full

		# If no matches
		if not cl_rows or len(cl_rows) == 0:
			raise Exception("No street named {}".format(addr_street_full))

		# Loop through CLs to find matching range
		parity_num = parity(addr_num)
		closest_cl_row = None
		min_nonexact_offset = None
		found_exact_cl = False
		multiple_exact_cl = False
		match_side = None

		for cl_row in cl_rows:
			# Check parity of left and right
			cl_row_l_f = cl_row['L_F_ADD']
			cl_row_r_f = cl_row['R_F_ADD']
			cl_row_l_t = cl_row['L_T_ADD']
			cl_row_r_t = cl_row['R_T_ADD']

			parity_left = parity_for_range(cl_row_l_f, cl_row_l_t)
			parity_right = parity_for_range(cl_row_r_f, cl_row_r_t)

			# Get ranged based on parity of address vs street
			left_parity_matches = parity_left in [parity_num, 'B']
			right_parity_matches = parity_right in [parity_num, 'B']

			cl_row_f = None
			cl_row_t = None

			if left_parity_matches:
				cl_row_f = cl_row_l_f
				cl_row_t = cl_row_l_t
			elif right_parity_matches:
				cl_row_f = cl_row_r_f
				cl_row_t = cl_row_r_t
			else:
				continue

			# Exact
			if cl_row_f <= addr_num <= cl_row_t:
				# Already found an exact match
				if found_exact_cl:
					# Set multiple flag
					multiple_exact_cl = True
					break

				# This is the first exact match
				found_exact_cl = True
				closest_cl_row = cl_row
				match_side = 'left' if left_parity_matches else 'right'
				continue

			# Out of range
			else:
				# If there's already an exact
				if found_exact_cl:
					# Carry on
					continue

				# We don't have an exact match yet
				offset = min(abs(addr_num - cl_row_l_f), abs(addr_num - cl_row_l_t))

				# This is the first out of range candidate
				if not min_nonexact_offset:
					min_nonexact_offset = offset
					closest_cl_row = cl_row
					match_side = 'left' if left_parity_matches else 'right'
					continue

				# New winner
				if offset < min_nonexact_offset:
					closest_cl_row = cl_row
					min_nonexact_offset = offset
					match_side = 'left' if left_parity_matches else 'right'

		# Handle CL issues
		if multiple_exact_cl:
			raise Exception("Multiple exact street matches")

		elif not closest_cl_row:
			raise Exception("Out of range")


		'''
		CONSTRUCTION LINE
		'''

		# Make Shapely line
		cl_geom_pts = [(pt.X, pt.Y,) for pt in closest_cl_row['SHAPE@'].getPart(0)]
		cl_lin_sh = LineString(cl_geom_pts)

		# Get distance along centerline to point closest to address point
		dist = cl_lin_sh.project(addr_pt_sh)

		# Get point on centerline at that distance
		closest_pt = cl_lin_sh.interpolate(dist)

		# Make constr line, store in buffer
		constr_pts = [addr_pt_sh, closest_pt]
		constr_lin_sh = LineString(constr_pts)
		constr_arr = arcpy.Array([arcpy.Point(addr_pt_sh.x, addr_pt_sh.y), arcpy.Point(closest_pt.x, closest_pt.y)])
		constr_lin = arcpy.Polyline(constr_arr)
		constr_exact = 1 if found_exact_cl else 0
		constr_buffer.append((addr_id, constr_exact, constr_lin,))

		# Get intersecting curb poly
		the_curb = curbs.get(poly_id)
		if not the_curb:
			raise Exception("No poly with ID {}".format(poly_id))
		curb_geom = the_curb.getPart(0)   # This gets an array of points

		# Make Shapely poly
		curb_geom_pts = []
		test = 0
		for curb_geom_pt in curb_geom:
			try:
				curb_geom_pts.append((curb_geom_pt.X, curb_geom_pt.Y,))
			except Exception as e:
				msg = "Poly {} has a null vertex".format(poly_id)
				logger.warn(msg)
		curb_ply_sh = Polygon(curb_geom_pts)

		# Find intersection of constr line and polygon
		intersect_lin = curb_ply_sh.intersection(constr_lin_sh)
		curb_pt = None
		
		# Line string
		if isinstance(intersect_lin, LineString):
			curb_pt = intersect_lin.coords[1]

		# Multi-part line string
		elif isinstance(intersect_lin, MultiLineString):
			curb_pt = intersect_lin[-1:][0].coords[1]

		# Write out
		new_streetside_row = (
			addr_id,
			# arcpy.Point(curb_pt[0], curb_pt[1]),
			curb_pt[0],
			curb_pt[1],
			addr_num,
			addr_std_comps['predir'],
			addr_std_comps['streetname'],
			addr_std_comps['suffix'],
			addr_std_comps['postdir'],
		)
		# streetside_buffer.append(new_streetside_row)
		streetside_file.write(','.join([str(x) for x in new_streetside_row]) + '\n')

	except Exception as e:
		# import traceback
		# print traceback.format_exc()
		logger.warning('{}: {}'.format(addr_id, e))

	finally:
		if log_stats:
			duration = round(time.clock() - log_stats_start, 4)
			logger.critical("Processed row {} in {} sec)".format(addr_row_count, duration))
			log_stats = False

		addr_row_count += 1


'''
WRITE FROM BUFFER
'''

logger.info("Writing construction line layer...")

# Construction line
constr_rows = arcpy.da.InsertCursor(CONSTR_LIN, ['ADDRESS_ID', 'EXACT_MATCH', 'SHAPE@'])
for row in constr_buffer:
	constr_rows.insertRow(row)
del constr_rows

# Close CSV
streetside_file.close()


# Final stats
# duration = datetime.now() - start
# seconds = duration.total_seconds()
# print("{} rows in {} seconds ({} seconds per row)".format(addr_row_count, seconds, seconds / addr_row_count))