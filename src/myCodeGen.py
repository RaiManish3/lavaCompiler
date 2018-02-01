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
class SymbolClass(object):
    def __init__(self, name, typ, scope):
        self.name = name
        self.value = value
        self.typ = typ
        self.scope = scope

def populateBlock():


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

def populateNextUseTable():
    for index,block in blocks.items():
        block = block.reverse()
        for b in block:
            
    

def makeVarList():


def main():

    ##input ## 
    ##
    irlist =[]
    leaders = [1]
    for ir in irlist:
        #function is skipped till doubt is cleared

        ir = ir.split(', ')
        if ir[1] is 'ifgoto' or 'goto':
            leaders.append(ir[0]+1)
            if ir[1] is 'ifgoto':
                leaders.append(ir[5])
            else:

                leaders.append(ir[2])
        elif ir[1] is 'label':
            pass
            # this portion is skipped
            leaders.append(ir[0]+1)

    blocks = { l:irlist[l-1:&&&next] for l in leaders }

    
    #lets make variable list and populate addess descriptor
    


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
