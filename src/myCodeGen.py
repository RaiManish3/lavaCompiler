## TODO 
"""
    1. Symbol table
    2. Address descriptor
    3. Register info list
    4. nextUseTable
    
    1, =, a, 2
    2, =, b, 7
    3, +, a, a, b
    4, ifgoto, leq, a, 50, 2
    5, call, foo
    6, ret
    7, label, foo
    8, print, a
    9, ret
    
"""
import sys
sys.path.extend(['..','.'])

from include import utility
from enum import Enum

class stat(Enum):
    LIVE = 1
    DEAD = 2

class SymbolClass(object):
    def __init__(self, typ, status, something):
        self.typ = typ
        self.status = status
        self.something = something

def populateBlock():
    pass

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

def populateNextUseTable():
    pass

def genInitialSymbolTable():
    for v in varlist:
        symTable[v] = SymbolClass(int, stat.LIVE, None)

def makeVarList():
    ## assuming only global variables
    for ir in irlist:
        if ir[1] in ['ifgoto', 'call', 'ret', 'label']:
            pass
        else:
            if len(ir) == 4:
                varlist.add(ir[2])
                varlist.add(ir[3])
            elif len(ir) == 5:
                varlist.add(ir[2])
                varlist.add(ir[3])
                varlist.add(ir[4])
    

def populateIR(filename):
    with open(filename, 'r') as infile:
        for line in infile:
            splitLine =line.strip().split(', ')
            irlist.append(splitLine)

def getFilename():
    argParser = argparse.ArgumentParser(description='Provide the IR code filename')
    argParser.add_argument('filename', type=str, help="./codegen filename.ir")
    args = argParser.parse_args()
    return args.filename

def main():
    filename = getFilename()
    populateIR(filename)

    for ir in irlist:
        #function is skipped till doubt is cleared
        if ir[1] in ['ifgoto', 'goto']:
            leaders.append(ir[0]+1)
            if ir[1] == 'ifgoto':
                leaders.append(ir[5])
            else:
                leaders.append(ir[2])

        elif ir[1] == 'label':
            leaders.append(ir[0]+1) ## doubt here

    tIRList = len(irlist)
    ## blocks == leader : instr block
    blocks = { x:irlist[x:y] for (x,y) in zip(leaders, leaders[1:]+[tIRList]) }


"""
    Structures
"""

if __name__ == "__main__":
    reglist = ['%eax', '%ebx','%ecx','%edx']
    registers = {}

    addressDescriptor = {}
    nextUseTable = [] 

    instrList = []
    irlist =[]

    leaders = [1,]
    varlist = set()

    symTable = {}
    nodes = []

    main()
