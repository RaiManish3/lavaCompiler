## TODO 
"""
    1. Symbol table
    2. Address descriptor
    3. Register info list
    4. nextUseTable
"""
def setLocation():
    pass

def getLocation():
    pass

def setReg():
    pass

def getReg():
    pass

def nextUse():
    pass

## Read the input IR file
def getFilename():
    pass

def populateIR():
    pass


"""
    Structures
"""

reglist = ['%eax', '%ebx','%ecx','%edx']
registers = {}

addressDescriptor = {}
nextUseTable = [] 

instructionList = []
leaders = []

nodes = []
