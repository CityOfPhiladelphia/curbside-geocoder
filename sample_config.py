CONFIG = {
	'file_gdb': 'curb_geocoder.gdb',
	
	'input': {
		'address_pt': 'ADDRESS_CURB_20141105',
		'address_fields': {
			'address_id': 'OBJECTID',
			'address_full': 'ADDRESS_ID',
			'poly_id': 'OBJECTID_1',
		},
		'streets_lin': 'STREETS_LIN',
		'streets_fields': {
			'street_name': 'STNAME',
			'left_from': 'L_F_ADD',
			'left_to': 'L_T_ADD',
			'right_from': 'R_F_ADD',
			'right_to': 'R_T_ADD',
		},
		'curbs_ply': 'CURBS_PLY',
	},
	
	'output': {
		'constr_lin': 'CONSTR_LIN',
		
		# Relative path for output files (non-GDB)
		'dir': 'output',
	},

	'logging': {
		'max_bytes': 5*1024*1024,
		'backup_count': 3,

		# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
		'console_level': 'CRITICAL',
		'file_level': 'DEBUG',
	},

	'debug': {
		'max_rows': 0,
		
		# Time every n runs
		'timed_row_interval': 50000,
	}
}