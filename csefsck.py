"""
HW1: csefsck 
Au: bw1307 Baochen Wang
P.S. It is really hard for me..:( Anyway, I tried my best!:)
"""

import json
import time
import math

#step 1:check the DeviceID 
def checkDeviceID():
    print "Step 1: Checking the DeviceID..."
    blFile = open("FS/fusedata.0","r")
    read = blFile.read()
    devID = json.loads(read)['devId']
    blFile.close()
    if devID == 20:
        print "\tThe DeviceID is correct!\n"
        return True
    else:
        print "\tError! The DeviceID is wrong!\n"
        return False

#step 2:check times
#check superblock times
def checksbTimes():
    print "Step 2: Checking the times..."
    ntime = time.time()
    #creationtime in superblock
    blFile = open("FS/fusedata.0","r")
    read = blFile.read()
    blFile.close()
    crTime = json.loads(read)['creationTime']
    global root, freeStart, freeEnd, maxblocks
    root = json.loads(read)['root']
    freeStart = json.loads(read)['freeStart']
    freeEnd = json.loads(read)['freeEnd']
    maxblocks = json.loads(read)['maxBlocks']
    if(crTime < ntime):
        print "\tThe creationTime in superblock is valid!"
    else:
        print "\tError!CreationTime in the superblock is in the future!"
        #??crTime = crTime.replace(crTime, ntime)
        print "\tCorrect the error. The creationTime is current time:", ntime

#check atime, ctime, mtime
def checktimes(NUM):
    ntime = time.time()
    blFiles = open("FS/fusedata."+NUM,"r")
    #find the type
    lines = []
    for line in blFiles:
        lines.append(line.strip())
    string = "".join(lines)
    blFiles.close()
    js = json.loads(string)
    k = 0
    for i in range(999):
        try:
            js.get('filename_to_inode_dict')[i].get('type')
            js.get('filename_to_inode_dict')[i].get('name')
            k = k+1
        except:
            break       
    atime = js.get('atime')
    ctime = js.get('ctime')
    mtime = js.get('mtime')
    if(atime < ntime):
        print "\tThe atime is valid("+NUM+")!"
    else:
        print "\tError!The atime is in the future("+NUM+")!"
    if(ctime < ntime):
        print "\tThe ctime is valid("+NUM+")!"
    else:
        print "\tError!The ctime is in the future("+NUM+")!"
    if(mtime < ntime):
        print "\tThe mtime is valid("+NUM+")!"
    else:
        print "\tError!The mtime is in the future("+NUM+")!"

    #recursively call if "d"
    for i in range(k):
        if (js.get('filename_to_inode_dict')[i].get('type') == 'd' and
            js.get('filename_to_inode_dict')[i].get('name') != '.' and
            js.get('filename_to_inode_dict')[i].get('name') != '..'):
            location = js.get('filename_to_inode_dict')[i].get('location')
            NUM = str(location)
            checktimes(NUM)
            
#step 3:check free block list
usedBlocks = set()
freeBlocks = set()

def readBlocks(NUM):
    blockfile = open("FS/fusedata."+NUM,"r")
    fileContent = blockfile.read()
    blockfile.close()
    content = json.loads(fileContent)
    addusedBlocks(NUM)
    return content

def getFreeBlocks():
    blockList = []
    for i in xrange(freeStart,freeEnd+1):
        LIST = readBlocks(str(i))
        content = (",".join(repr(e) for e in LIST))
        temp = map(int,content.strip().split(","))
        blockList = blockList + temp
    global freeBlocks
    for block in blockList:
        freeBlocks.add(block)

def addusedBlocks(NUM):
    global usedBlocks
    usedBlocks.add(int(NUM))    

def checkBlocks():
    print "\nStep 3: Validating the free block list..."
    isError = False
    try:
        commonBlocks = freeBlocks.intersection(usedBlocks)
        if len(commonBlocks) > 0:
            print "\tError!Overlapping free and used blocks: " 
            for block in commonBlocks:
                print "\t%s" %(block)
            isError = True
    except Exception, e:
        print "\tError in blocks list!"
        isError = True
    if  len(freeBlocks | usedBlocks) != maxblocks:
        print "\tNot all free blocks are on the list.Total number of blocks found:"+str(len(freeBlocks | usedBlocks))+".The total should be "+str(maxblocks)+"."
        isError = True
    if isError == False:
        print "\tNo errors found in blocks list!"

#step 4:check directory and block numbers
def checkDir(NUM):
    blFiles = open("FS/fusedata."+NUM,"r")
    #find the type
    lines = []
    for line in blFiles:
        lines.append(line.strip())
    string = "".join(lines)
    blFiles.close()
    js = json.loads(string)
    k = 0
    flagdot = False
    for i in range(999):
        try:
            js.get('filename_to_inode_dict')[i].get('type')
            js.get('filename_to_inode_dict')[i].get('name')
            k = k+1
        except:
            break
    #check . and ..
    for i in range(k):
        if(js.get('filename_to_inode_dict')[i].get('name') == '.'):
            for j in range(k):
                if(js.get('filename_to_inode_dict')[j].get('name') == '..'):
                    flagdot = True
    if(flagdot):
        print "\tThis directory("+NUM+")contains . and ..!"
    else:
        print "\tError!There is no . or .. for this directory("+NUM+"(!"
    #check block numbers
    for i in range(k):
        if(js.get('filename_to_inode_dict')[i].get('name') == '.'):
            currentloc = js.get('filename_to_inode_dict')[i].get('location')
        if(js.get('filename_to_inode_dict')[i].get('name') == '..'):
            parentloc = js.get('filename_to_inode_dict')[i].get('location')
    if(NUM == str(root)):
        if(currentloc == root and parentloc == root):
            print "\tTheir block numbers are correct for root directory!"
        else:
            print "\tError!Their block numbers are wrong for root directory!"
    for i in range(k):
        if (js.get('filename_to_inode_dict')[i].get('type') == 'd' and
            js.get('filename_to_inode_dict')[i].get('name') != '.' and
            js.get('filename_to_inode_dict')[i].get('name') != '..'):
            location = js.get('filename_to_inode_dict')[i].get('location')
            name = js.get('filename_to_inode_dict')[i].get('name')
            parent = NUM
            NUM = str(location)
            fl = open("FS/fusedata."+NUM,"r")
            li = []
            for lin in fl:
                li.append(lin.strip())
            strin = "".join(li)
            fl.close()
            j = json.loads(strin)
            for z in range(999):
                try:
                    if(j.get('filename_to_inode_dict')[z].get('type') == 'd' and
                       j.get('filename_to_inode_dict')[z].get('name') == '.'):
                        subloc = j.get('filename_to_inode_dict')[z].get('location')
                except:
                    break
            if(str(subloc) == NUM and str(parentloc) == parent):
                print "\tTheir block numbers are correct for " + str(name) +" directory!"
            else:
                print "\tError!Their block numbers are wrong for " + str(name) +" directory!"
            checkDir(NUM)

#step 5:check whether the data is array if indirect is 1
def isArray(NUM):
    fl1 = open("FS/fusedata."+NUM,"r")
    content1 = fl1.read()
    fl1.close()
    location = json.loads(content1)['location']
    blNum = str(location)
    fl2 = open("FS/fusedata."+blNum,"r")
    content2 = fl2.read()
    fl2.close()
    try:
        LIST = json.loads(content2)
        content = (",".join(repr(e) for e in LIST))
        testdata = content.split(',')
        is_array = True
        for i in testdata:
            i = i.strip()
            if(not i.isdigit()):
                is_array = False
                break
    except:
        is_array = False        
    return is_array
    
def checkArray(NUM):
    print "\nStep 5: Validating the data is an array..."
    blFiles = open("FS/fusedata."+NUM,"r")
    #find the type
    lines = []
    for line in blFiles:
        lines.append(line.strip())
    string = "".join(lines)
    blFiles.close()
    js = json.loads(string)
    k = 0
    for i in range(999):
        try:
            js.get('filename_to_inode_dict')[i].get('type')
            js.get('filename_to_inode_dict')[i].get('name')
            k = k+1
        except:
            break
    for i in range(k):
        if (js.get('filename_to_inode_dict')[i].get('type') == 'f' and
            js.get('filename_to_inode_dict')[i].get('name') != '.' and
            js.get('filename_to_inode_dict')[i].get('name') != '..'):
            location = js.get('filename_to_inode_dict')[i].get('location')
            NUM = str(location)
            fl = open("FS/fusedata."+NUM,"r")
            content = fl.read()
            fl.close()
            indirect = json.loads(content)['indirect']
            if(indirect == 1):
                if(isArray(NUM)):
                    print "\tThe data is an array!"
                else:
                    print "\tError!The data is not an array!"

#step 6:check the size is valid for the number of block pointers in the location array
def checkSize(NUM):
    print "\nStep 6: Checking the size whether is valid..."
    blFiles = open("FS/fusedata."+NUM,"r")
    #find the type
    lines = []
    for line in blFiles:
        lines.append(line.strip())
    string = "".join(lines)
    blFiles.close()
    js = json.loads(string)
    k = 0
    blocksize = 4096
    for i in range(999):
        try:
            js.get('filename_to_inode_dict')[i].get('type')
            js.get('filename_to_inode_dict')[i].get('name')
            k = k+1
        except:
            break
    for i in range(k):
        if (js.get('filename_to_inode_dict')[i].get('type') == 'f' and
            js.get('filename_to_inode_dict')[i].get('name') != '.' and
            js.get('filename_to_inode_dict')[i].get('name') != '..'):
            location = js.get('filename_to_inode_dict')[i].get('location')
            NUM = str(location)
            fl = open("FS/fusedata."+NUM,"r")
            content = fl.read()
            fl.close()
            indirect = json.loads(content)['indirect']
            size = json.loads(content)['size']
            length = math.ceil(size/float(4096))
            if(indirect == 0):
                if(size < blocksize and size > 0):
                    print "\tThe size is valid!"
                else:
                    print "\tError!The size is invalid!"
            if(indirect != 0):
                if(size < (blocksize * length) or size > (blocksize * (length-1))):
                    print "\tThe size is valid!"
                else:
                    print "\tError!The size is invalid!"

def main():
    print "**************File System Checker**************\n"
    if(checkDeviceID()):
        checksbTimes()
        NUM = str(root)
        checktimes(NUM)
        global usedBlocks
        usedBlocks.add(0)
        getFreeBlocks()
        checkBlocks()
        print "\nStep 4: Checking the directory and block numbers..." #since there is recursion
        checkDir(NUM)
        checkArray(NUM)
        checkSize(NUM)
        
if __name__ == "__main__":
    main()
