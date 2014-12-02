"""

Philadelphia Address Stanardizer

Author: Tom Swanson

Created: 8/25/2014
Last Updated: 10/10/2014
    
Version: 1.0

"""


import csv, sys, os, time, math, re
from datetime import datetime



'''
CLASS DEFINITIONS
'''


class suffix:
    def __init__(self, row):
        # 0 - not a suffix
        # 1 - standard suffix abbr
        # 2 - long suffix
        # 3 - common abbr
        self.full = row[0]
        self.common = row[1]
        self.correct = row[2]
        
        self.std = '3'
        #self.notes = row[4]

        if(self.common == self.full):
            self.std = '2'
        if(self.common == self.correct):
            self.std = '1'  


class addrnum:
    def __init__(self):
        self.addrnumlow =-1
        self.addrnumhigh = -1
        self.addrnumstrlow = ''
        self.addrnumstrhigh = ''
        self.oeb = ''
        self.isaddr = False
    

class addr:
    def __init__(self):
        self.parsetype = ''
        self.addr = addrnum()
        self.predir = ''
        self.streetname = ''
        self.suffix = ''
        self.postdir = ''
        self.unitdesignator = ''
        self.predir2 = ''
        self.streetname2 = ''
        self.suffix2 = ''
        self.postdir2 = ''
        self.unitdesignator2 = ''


class directional:
    def __init__(self, row):
        # 0 - not a dir
        # 1 - abbr dir N,E,S,W
        # 2 - long dir NORTH,EAST,SOUTH,WEST
        self.full = row[0]
        self.common = row[1]
        self.correct = row[2]
        self.std = '1'
        #self.notes = row[4]

        if(self.common == self.full):
            self.std = '2'


class addordinal:
    def __init__(self, row):
        self.ordigit = row[0]
        self.orsuffix = row[1]
     

class saint:
    def __init__(self, row): 
        self.saintName = row[0]
       

class namestd:
    def __init__(self, row):  
        self.correct = row[0]
        self.common = row[1]


class apt:
    def __init__(self, row): 
        self.correct = row[0]
        self.common = row[1]


class apte:
    def __init__(self, row):
        self.correct = row[0]
        self.common = row[1]




'''
SETUP FUNCTIONS
'''


def csv_path(file_name):
    return os.path.join(cwd, file_name + '.csv')
    
            
def createSuffixLookup():
    path = csv_path('suffix')
    f = open(path, 'r')
    lookup = {}
    try:
        reader = csv.reader(f)
        for row in reader: 
            r = suffix(row)
            lookup[r.common] = r
    except:
        print('Error opening ' + path, sys.exc_info()[0])
    f.close()
    return lookup


def createDirLookup():
    path = csv_path('directional')
    f = open(path, 'r')
    lookup = {}
    try:
        reader = csv.reader(f)
        for row in reader: 
            r = directional(row)
            lookup[r.common] = r
    except:
        print('Error opening ' + path, sys.exc_info()[0])
    f.close()
    return lookup


def createOrdinalLookup():
    lookup = {}
    r = addordinal(['1','ST'])
    lookup[r.ordigit] = r
    r = addordinal(['2','ND'])
    lookup[r.ordigit] = r
    r = addordinal(['3','RD'])
    lookup[r.ordigit] = r
    r = addordinal(['4','TH'])
    lookup[r.ordigit] = r
    r = addordinal(['5','TH'])
    lookup[r.ordigit] = r
    r = addordinal(['6','TH'])
    lookup[r.ordigit] = r
    r = addordinal(['7','TH'])
    lookup[r.ordigit] = r
    r = addordinal(['8','TH'])
    lookup[r.ordigit] = r
    r = addordinal(['9','TH'])
    lookup[r.ordigit] = r
    r = addordinal(['0','TH'])
    lookup[r.ordigit] = r
    return lookup


def createSaintLookup():
    path = csv_path('saint')
    f = open(path, 'r')
    lookup = {}
    try:
        reader = csv.reader(f)
        for row in reader: 
            r = saint(row)
            lookup[r.saintName] = r
    except:
        print('Error opening ' + path, sys.exc_info()[0])
    f.close()
    return lookup


def createNameStdLookup():
    path = csv_path('std')
    f = open(path, 'r')
    lookup = {}
    try:
        reader = csv.reader(f)
        for row in reader: 
            r = namestd(row)
            lookup[r.common] = r
    except:
        print('Error opening ' + path, sys.exc_info()[0])
    f.close()
    return lookup


def createAptLookup():
    path = csv_path('apt')
    f = open(path, 'r')
    lookup = {}
    try:
        reader = csv.reader(f)
        for row in reader: 
            r = apt(row)
            lookup[r.common] = r
    except:
        print('Error opening ' + path, sys.exc_info()[0])
    f.close() 
    return lookup


def createApteLookup():
    path = csv_path('apte')
    f = open(path, 'r')
    lookup = {}
    try:
        reader = csv.reader(f)
        for row in reader: 
            r = apte(row)
            lookup[r.common] = r
    except:
        print('Error opening ' + path, sys.exc_info()[0])
    f.close() 
    return lookup




'''
TYPE TESTS
'''


def isSuffix(test):
    # 0 - not a suffix
    # 1 - standard suffix abbr
    # 2 - long suffix
    # 3 - common abbr
    
    try:
        suf = suffixLookup[test]
    except KeyError:
        row = [' ', test, ' ']
        suf = suffix(row)
        suf.std = '0'
    return suf


def isDir(test):
    # 0 - not a dir
    # 1 - abbr dir N,E,S,W
    # 2 - long dir NORTH,EAST,SOUTH,WEST
   
    try:
        dir = dirLookup[test]
    except KeyError:
        row = [' ', test, ' ']
        dir = directional(row)
        dir.std = '0'
    
    return dir


def isSaint(test):
    ret = True
    try:
        snt = saintLookup[test]
    except KeyError:
        ret = False
    
    return ret


def isNameStd(test):
    try:
        nstd = nameStdLookup[test]
    except KeyError:
        row = ['', test]
        nstd = namestd(row)
        
    return nstd


def isApt(test):
    try:
        apttemp = aptLookup[test]
    except KeyError:
        row = ['',test]
        apttemp = apt(row)
        
    return apttemp


def isApte(test):
    try:
        aptetemp = apteLookup[test]
    except KeyError:
        row = ['',test]
        aptetemp = apte(row)
        
    
    return aptetemp


# Standardize names
def nameStd(tokens):
    i = len(tokens)
    j = 0
    while (i>0):
        j = 0
        while (j+i<=len(tokens)):
            
            nstd = isNameStd(' '.join(tokens[j:j+i]))
            if(nstd.correct!=''):
              tokens[j] = nstd.correct
              k = j+1
              while(k<j+i):
                  tokens[k] = ''
                  k += 1
            j += 1
        i -= 1 
    temp = " ".join(tokens).split()
    if(len(temp)>0 and temp[0].isdigit()):
        temp = addOrdinal(temp)
    return temp




'''
TYPE HANDLERS
'''


def handleSt(tokens):
    i=0
    while(i<len(tokens)-1):
        if(tokens[i]== 'ST' and isSaint(tokens[i+1])):
            tokens[i] = 'SAINT'
        elif(tokens[i]== 'ST' and tokens[i+1][len(tokens[i+1])-1] == 'S'):
            test = tokens[i+1]
            testlen = len(test)
            if(isSaint(test[0:testlen-1])):
                tokens[i] = 'SAINT'
        i +=1
    return tokens


def handleApt(tokens):
    tlen = len(tokens)
    i = 0
    while(i<tlen-1):
      if(isOrdinal(tokens[i]) == True and (tokens[i+1] in aptfloor)):
         return [i,tokens[i]+' FL']
      addrn = isAddr(tokens[i+1], 2)
      apt = isApt(tokens[i])
      if(addrn.isaddr == True and apt.correct != ''):
          return [i,' '.join(tokens[i:])]
      i += 1
          
    if(tlen>2):
      addrn = isAddr(tokens[tlen-1], 2)
      apt = isApt(tokens[tlen - 2])
      #tempDir1 = isDir(tokens[tlen-2],dirLookup)
      #tempSuffix1 = isSuffix(tokens[tlen-2],suffixLookup)
           
      if(addrn.isaddr == True and apt.correct != ''):
          return [tlen-2,apt.correct+' '+addrn.addrnumstrlow]
      elif(addrn.isaddr == True):
          return [tlen-1,addrn.addrnumstrlow]

    return [-1, '']


def handleMt(tokens):
    i = 0
    while i < len(tokens) - 1:
        if tokens[i] == 'MT':
            tokens[i] = 'MOUNT'
        i += 1
    return tokens


def handleDirSpaces(tokens):
    return tokens


def isOrdinal(token):
    tlen= len(token)
    if(tlen>2):
        test = token[tlen-3:]
        if test in ordinal:
            return True
    return False


def addOrdinal(str):
    lastchar = str[0][-1:]
    ord=addOrdinalLookup[lastchar]
    str[0] = str[0]+ord.orsuffix
    return str
    

def isAddr(test, ver):
    #type:
    # 0 = standard
    # 1 = unit designator (need to allow single Char)
    #break between alpha,num,_,-,/

    half = False

    if len(test) > 2 and test[-3:] == '1/2':
        half = True
        test = test[:-3]
    if test == 'ONE':
        test = '1'
    
    tokens = re.findall(r"[^\W\d_-]+|\d+|-|#|/", test)
    tokenLen = len(tokens)
    if tokenLen > 1 and tokens[-1].isalnum() == False:
        tokens.pop()
        tokenLen = len(tokens)
        
    addr_ret = addrnum()


    #9367-75
    #925R-35
    #Handle Address Ranges from DOR
    if((tokenLen == 3 or tokenLen == 4) and tokens[0].isdigit() and tokens[tokenLen-2] == '-' and len(tokens[tokenLen-1]) <= 2 and tokens[tokenLen-1].isdigit()):
        
        alowst = tokens[0][-2:]
        ahighst = tokens[tokenLen-1][-2:]
        if(int(alowst) % 2 == 0):
            alowoeb = 'E'
        else:
            alowoeb = 'O'
        if(int(ahighst) % 2 == 0):
            ahighoeb = 'E'
        else:
            ahighoeb = 'O'
        if(ahighoeb != alowoeb):
            ahighoeb == 'B'
            alowoeb == 'B'
            
        ilow = int(alowst)
        ihigh = int(ahighst)
        if ilow > ihigh:
           ahighoeb == 'U'
           alowoeb == 'U'
           
        if len(tokens[0]) > 2:
            hundred = (int(tokens[0][0:-2]))*100
            ilow = hundred+ilow
            ihigh = hundred+ihigh
        
        if tokenLen == 3:
            addr_ret.addrnumlow =ilow
            addr_ret.addrnumhigh = ihigh
            addr_ret.addrnumstrlow = str(ilow)
            addr_ret.addrnumstrhigh = str(ihigh)
            addr_ret.oeb = ahighoeb
            addr_ret.isaddr = True
        else:
            addr_ret.addrnumlow = ilow
            addr_ret.addrnumhigh = ihigh
            addr_ret.addrnumstrlow = str(ilow)+tokens[1]
            addr_ret.addrnumstrhigh = str(ihigh)+tokens[1]
            addr_ret.oeb = ahighoeb
            addr_ret.isaddr = True
        return addr_ret

    #2201 1/2-03
    #Handle Address Ranges from DOR
    if tokenLen == 6  and \
       tokens[0].isdigit() and \
       tokens[1] == '1' and \
       tokens[2] == '/' and \
       tokens[3] == '2' and \
       tokens[4] == '-' and \
       tokens[5].isdigit():
        
        alowst = tokens[0][-2:]
        ahighst = tokens[5][-2:]
        if int(alowst) % 2 == 0:
            alowoeb = 'E'
        else:
            alowoeb = 'O'
        if int(ahighst) % 2 == 0:
            ahighoeb = 'E'
        else:
            ahighoeb = 'O'
        if ahighoeb != alowoeb:
            ahighoeb == 'B'
            alowoeb == 'B'
            
        ilow = int(alowst)
        ihigh = int(ahighst)
        if(ilow> ihigh):
           ahighoeb == 'U'
           alowoeb == 'U'
           
        if len(tokens[0]) > 2:
            hundred = int(tokens[0][:-2]) * 100
            ilow = hundred + ilow
            ihigh = hundred + ihigh
        
        
        addr_ret.addrnumlow =ilow 
        addr_ret.addrnumhigh = ihigh
        addr_ret.addrnumstrlow = str(ilow)+ ' 1/2'
        addr_ret.addrnumstrhigh = str(ihigh)+ ' 1/2'
        addr_ret.oeb = ahighoeb
        addr_ret.isaddr = True
        
        return addr_ret
    
    if tokenLen == 1 and tokens[0].isdigit():
        if(int(tokens[0]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        # and addess number of zero, return as true but blank it out
        if(tokens[0] == '0' or tokens[0] == '00'):
            addr_ret.addrnumlow =-1
            addr_ret.addrnumhigh = -1
            addr_ret.oeb = 'U'
            addr_ret.addrnumstrlow = ''
            addr_ret.addrnumstrhigh = ''
            addr_ret.isaddr = True
        else:
            addr_ret.addrnumlow = int(tokens[0])
            addr_ret.addrnumhigh = int(tokens[0])
            addr_ret.addrnumstrlow = ''.join(tokens)
            addr_ret.addrnumstrhigh = ''.join(tokens)
            addr_ret.isaddr = True
        return addr_ret
    
    #A
    if(ver == 2 and tokenLen == 1 and len(tokens[0]) == 1 and tokens[0].isalpha()):
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.oeb = 'U'
        addr_ret.addrnumlow = 0
        addr_ret.addrnumhigh = 0
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
        return addr_ret
    
    #NNAA
    if(tokenLen == 2 and tokens[0].isdigit()):
        # numeric street
        if(tokens[1] == 'ST' or tokens[1] == 'ND' or tokens[1] == 'RD'  or tokens[1] == 'TH'):
            addr_ret.isaddr = False
        else:
            if(half == True):
                tokens.append(' 1/2')
            if(int(tokens[0]) % 2 == 0):
                addr_ret.oeb = 'E'
            else:
                addr_ret.oeb = 'O'
            addr_ret.addrnumlow = int(tokens[0])
            addr_ret.addrnumhigh = int(tokens[0])
            addr_ret.addrnumstrlow = ''.join(tokens)
            addr_ret.addrnumstrhigh = ''.join(tokens)
            addr_ret.isaddr = True
    #AANN
    if(tokenLen == 2 and tokens[1].isdigit()):
        if(int(tokens[1]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[1])
        addr_ret.addrnumhigh = int(tokens[1])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
    #UU-NN
    if(tokenLen > 2 and tokens[tokenLen-2]== '-' and tokens[tokenLen-1].isdigit()):
        if(int(tokens[tokenLen-1]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[tokenLen-1])
        addr_ret.addrnumhigh = int(tokens[tokenLen-1])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
    #NN-UU
    if(tokenLen > 2 and tokens[tokenLen-2]== '-' and tokens[tokenLen-1].isalpha() and tokens[0].isdigit()):
        if(int(tokens[0]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[0])
        addr_ret.addrnumhigh = int(tokens[0])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
    #AANNAA
    if(tokenLen == 3 and tokens[1].isdigit()):
        if(int(tokens[1]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[1])
        addr_ret.addrnumhigh = int(tokens[1])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
    #NNAANN - this is a bit unusual
    if(tokenLen == 3 and tokens[0].isdigit() and tokens[2].isdigit()):
        if(int(tokens[2]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[2])
        addr_ret.addrnumhigh = int(tokens[2])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True


    #AANNAANN
    if(tokenLen == 4 and tokens[1].isdigit() and tokens[3].isdigit()):
        if(int(tokens[3]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[3])
        addr_ret.addrnumhigh = int(tokens[3])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
    #NNAANNAA
    if(tokenLen == 4 and tokens[0].isdigit() and tokens[2].isdigit()):
        if(int(tokens[2]) % 2 == 0):
            addr_ret.oeb = 'E'
        else:
            addr_ret.oeb = 'O'
        if(half == True):
            tokens.append(' 1/2')
        addr_ret.addrnumlow = int(tokens[2])
        addr_ret.addrnumhigh = int(tokens[2])
        addr_ret.addrnumstrlow = ''.join(tokens)
        addr_ret.addrnumstrhigh = ''.join(tokens)
        addr_ret.isaddr = True
    return addr_ret

    
def parseAddr(item):
    address = addr()
    tempDir = {}
    tempSuffix = {}

    # Handle special characters
    item = (
        item.replace('.', ' ')
        # .replace('')
        .replace(',',' ')
        .upper()
        .replace('#', ' ')
        .replace('\'', '')
    )
    item = ' '.join(item.split())

    # TODO: this might break something
    if item == '':
        return
    
    conjunctions = [' {} '.format(x) for x in ['AND', '@', 'AT', '&']]
    if any(x in item for x in conjunctions) or ('/' in item and '1/' not in item):
        if ' AND ' in item:
            tokens = item.split(" AND ")
        elif ' AT ' in item:
            tokens = item.split(" AT ")
        elif ' & ' in item:
            tokens = item.split(" & ")
        elif ' @ ' in item:
            tokens = item.split(" @ ")
        elif '/' in item:
            tokens = item.split('/')

        addr1 = parseAddr(tokens[0])

    tokens = item.split()
    tokenLen = len(tokens)
    addrn = isAddr(tokens[0], 0)
    
    if tokenLen > 1 and addrn.isaddr == True and len(tokens[1]) >= 3 and tokens[1][1] == '/':
        addrn = isAddr(tokens[0] + ' ' + tokens[1], 0)
        #addrn.addrnumstrlow = addrn.addrnumstrlow+' '+tokens[1]
        #addrn.addrnumstrhigh = addrn.addrnumstrhigh+' '+tokens[1]
        #address.addr = addrn
        tokens = tokens[2:tokenLen]
    
    elif addrn.isaddr == True and tokenLen > 1:
        address.addr = addrn
        tokens = tokens[1:]

    tokenLen = len(tokens)
    apt = handleApt(tokens)
    address.unitdesignator = ''
    
    if apt[0] != -1:
        address.unitdesignator = apt[1]
        tokens = tokens[0:apt[0]]
    tokenLen = len(tokens)
    
    if tokenLen == 1:
       address.streetname = ' '.join(nameStd(tokens))
       address.parsetype = 'A1'
       return address

    # TODO: ?
    tokens = handleSt(tokens)
    tokens = handleMt(tokens)
      
    if tokenLen == 2:
        tempSuffix1 = isSuffix(tokens[-1])
      
        if tempSuffix1.std != '0':
            address.addr = addrn
            address.predir = ''
            address.streetname = ' '.join(nameStd(tokens[:-1]))
            address.suffix = tempSuffix1.correct
            address.postdir = ''
            address.parsetype = '2NS'
            return address

        tempDir1 = isDir(tokens[0])
        if tempDir1.std != '0':
            address.addr = addrn
            address.predir = tempDir1.correct
            address.streetname = ''.join(nameStd(tokens[1:]))
            address.suffix = ''
            address.postdir = ''
            #address.unitdesignator = ''
            address.parsetype = '2APN'
            return address

        if tempDir1.std != '0':
            address.addr = addrn
            address.predir = ''
            address.streetname = ' '.join(nameStd(tokens[:-1]))
            address.suffix = ''
            address.postdir = tempDir1.correct
            #address.unitdesignator = ''
            address.parsetype = '2ANP'
            return address 

        else:
            address.addr = addrn
            address.predir = ''
            address.streetname = ' '.join(nameStd(tokens))
            address.suffix = ''
            address.postdir = ''
            #address.unitdesignator = ''
            address.parsetype = '2ANN'
            return address 
          
    if tokenLen >= 3 and tokenLen < 7:
       tempDir1 = isDir(tokens[0])
       tempDir2 = isDir(tokens[tokenLen-1])
       tempSuffix1 = isSuffix(tokens[tokenLen-1])
       tempSuffix2 = isSuffix(tokens[tokenLen-2])
       
       ## Pattern addrnum dir name suffix
       if tempDir1.std != '0' and tempSuffix1.std != '0':
            address.addr = addrn
            address.predir = tempDir1.correct
            address.streetname = ' '.join(nameStd(tokens[1:-1]))
            address.suffix = tempSuffix1.correct
            address.postdir = ''
            address.parsetype = 'ADNS'
            return address

       ## Pattern addrnum name suffix dir
       if tempDir2.std != '0' and tempSuffix2.std != '0':
            address.addr = addrn
            address.predir = ''
            address.streetname = ' '.join(nameStd(tokens[:-2]))
            address.suffix = tempSuffix2.correct
            address.postdir = tempDir2.correct
            address.parsetype = 'ANSD'
            return address

       ## Pattern addrnum dir name suffix junk
       if tempDir1.std == '1' and tempSuffix2.std == '1' and tempSuffix1.std != '0':
            address.addr = addrn
            address.predir = tempDir1.correct
            address.streetname = ' '.join(nameStd(tokens[1:-2]))
            address.suffix = tempSuffix2.correct
            address.postdir = ''
            address.parsetype = 'ADNSx'
            return address

       ## Name and Suffix
       if tempDir1.std == '0' and tempDir2.std == '0' and tempSuffix1.std != '0':
            address.addr = addrn
            address.predir = ''
            address.streetname = ' '.join(nameStd(tokens[:-1]))
            address.suffix = tempSuffix1.correct
            address.postdir = ''
            address.parsetype = 'ANS'
            return address
    
    #There's junk
    if tokenLen >= 4:
        tempDir1 = isDir(tokens[0])
        tempDir2 = isDir(tokens[3])
        tempSuffix1 = isSuffix(tokens[2])
        tempSuffix2 = isSuffix(tokens[3])
       
       # predir name suffix junk
        if tempDir1.std != '0' and tempSuffix1.std == '1':
            address.addr = addrn
            address.predir = tempDir1.correct
            address.streetname = ' '.join(nameStd(tokens[1:2]))
            address.suffix = tempSuffix1.correct
            address.postdir = ''
            address.parsetype = '4ADNSx'
            return address
       
       # predir name name suffix
        if tempDir1.std != '0' and tempSuffix2.std != '0':
            address.addr = addrn
            address.predir = tempDir1.correct
            address.streetname = ' '.join(nameStd(tokens[1:3]))
            address.suffix = tempSuffix2.correct
            address.postdir = ''
            address.parsetype = '4APNNSx'
            return address
    
    if tokenLen == 3:
        tempDir1 = isDir(tokens[0])
        tempDir2 = isDir(tokens[2])
        tempSuffix1 = isSuffix(tokens[1])
        tempSuffix2 = isSuffix(tokens[2])
        
        #predir name name suffix
        if tempDir1.std == '0' and tempSuffix1.std == '0' and tempDir2.std == '0' and tempSuffix2.std == '0':
            address.addr = addrn
            address.predir = ''
            address.streetname = ' '.join(nameStd(tokens[0:3]))
            address.suffix = ''
            address.postdir = ''
            address.parsetype = '3NNN'
            return address

        if tempDir1.std != '0' and tempSuffix1.std == '0' and tempDir2.std == '0' and tempSuffix2.std == '0':
            address.addr = addrn
            address.predir = tempDir1.correct
            address.streetname = ' '.join(nameStd(tokens[1:3]))
            address.suffix = ''
            address.postdir = ''
            address.parsetype = '3DNN'
            return address
        
    address.parsetype = 'TODO'
    address.streetname = ' '.join(nameStd(tokens))
    
    return address


'''
RUN
'''

cwd = os.path.dirname(__file__)

# Get config
# config_path = os.path.join(cwd, 'config.py')
# return_dict = True if CONFIG['return_dict'] else False

ordinal = ['1ST','2ND','3RD','4TH','5TH','6TH','7TH','8TH','9TH','0TH']
aptfloor = ['FL','FLR','FLOOR']
header = 'parse,input,oeb,alow,ahigh,astrlow,astrhigh,predir,streetname,suffix,postdir,unit,predir2,streetname2,suffix2,postdir2,unit2\n'

suffixLookup = createSuffixLookup()
dirLookup = createDirLookup()
saintLookup = createSaintLookup()
nameStdLookup = createNameStdLookup()
aptLookup = createAptLookup()
apteLookup = createApteLookup()
addOrdinalLookup = createOrdinalLookup()


class Parser():
    def __init__(self, return_dict=False):
        self.return_dict = return_dict

    def parse(self, addr_str):
        parsed = parseAddr(addr_str)
        if self.return_dict:
            # Hack to make nested addrnum a dict as well
            parsed.addr = parsed.addr.__dict__
            return parsed.__dict__
        return parsed
        
        
# TEST
# if __name__ == '__main__':
#     parser = Parser(return_dict=True)
#     parsed = parser.parse('1718 N. Bailey Street')
#     print(parsed)