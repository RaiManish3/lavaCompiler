#!/usr/bin/env python

import sys
sys.path.extend(['..','.'])

from includes import utility
from enum import Enum
import argparse

class stat(Enum):
    LIVE = 1
    DEAD = 2

class SymbolClass(object):
    def __init__(self, typ, status):
        self.typ = typ
        self.status = status

def setLocation(var, location):
    addressDescriptor[var] = location

def getLocation(var):
    return addressDescriptor[var]

def setReg(reg, value):
    registers[reg]=value

def getReg(var, lineno):
    ## if 'var' is present in some register return that register name
    hasEmptyReg = (False,None)
    for regname, value in registers.items():
        if value == var:
            return regname
        elif value == None:
            hasEmptyReg = (True, regname)

    ## else if any register is empty return that register name
    if hasEmptyReg[0]:
        return hasEmptyReg[1]

    ## otherwise we steal other var's register (farthest use in block) and push it to memory
    varNextUse = nextUseTable[lineno]
    farthestNextUse = [varlist[0], varNextUse[varlist[0]]]  ## [ variable name, nextuse ]

    for k,v in varNextUse.items():
        if v > farthestNextUse[1]:
            farthestNextUse[0] = k

    for regname, value in registers.items():
        if value == farthestNextUse[0]:
            ## push to memory
            ## TODO :: confirm with x86 architecture
            assemblyCode += "mov " + var + ", " + regname + "\n"
            return regname


def nextUse(var, lineno):
    return nextUseTable[lineno][var]

def populateNextUseTable():
    for ldr, block in blocks.items():

        for b in block[::-1]:
            nextUseTable[b[0]] = {var:symTable[var] for var in varlist}
            optr = b[1]

            # INSTRUCTION NUMBER NEEDED
            if optr == '=':
                symTable[b[2]].status = stat.DEAD
                if b[3] in varlist: 
                    symTable[b[3]].status = stat.LIVE

            elif optr in arithOp:
                symTable[b[2]].status = stat.DEAD
                if b[3] in varlist:
                    symTable[b[3]].status = stat.LIVE
                if b[4] in varlist:
                    symTable[b[4]].status = stat.LIVE

            elif optr == 'ifgoto':
                if b[3] in varlist:
                    symTable[b[3]].status = stat.LIVE
                if b[4] in varlist:
                    symTable[b[4]].status = stat.LIVE
            # TODO
            # print missing
            # add other if else statements also
            
    
def genInitialSymbolTable():
    for v in varlist:
        symTable[v] = SymbolClass(int, stat.LIVE, None)
        addressDescriptor[v]='mem'  ## initially no variable is loaded onto the registers

def makeVarList():
    ## assuming only global variables
    global varlist
    localVarList = set()
    for ir in irlist:
        if ir[1] in ['ifgoto', 'call', 'ret', 'label']:
            pass
        else:
            ## statements of the form :: lineno, operator, { var | literal ,}
            for i in range(2,len(ir)):
                if not utility.isnumber(ir[i]):
                    localVarList.add(ir[i])
    varlist = list(localVarList)[:]

def genBlocks():
    tIRList = len(irlist)

    for i in range(len(leaders)):
        instr1 = leaders[i]
        instr2 = leaders[i+1]-1 if i+1<len(leaders) else tIRList
        blocks[instr1] = irlist[instr1-1:instr2]

def findLeaders():
    global leaders
    for ir in irlist:
        # TODO function is skipped till doubt is cleared
        if ir[1] in ['ifgoto', 'goto']:
            leaders.append(ir[0]+1)
            if ir[1] == 'ifgoto':
                leaders.append(int(ir[5]))
            else:
                leaders.append(int(ir[2]))

        elif ir[1] == 'label':
            leaders.append(ir[0]+1) ## doubt here

    leaders = list(set(leaders))
    leaders.sort()

def populateIR(filename):
    try:
        with open(filename, 'r') as infile:
            for line in infile:
                splitLine =line.strip().split(', ')
                splitLine[0] = int(splitLine[0])
                irlist.append(splitLine)
    except FileNotFoundError:
        print("Cannot find the file. Make sure the path is right!")
        exit(1)

def getFilename():
    argParser = argparse.ArgumentParser(description='Provide the IR code filename')
    argParser.add_argument('filename', type=str, help="./codegen filename.ir")
    args = argParser.parse_args()
    return args.filename

def main():
    filename = getFilename()
    populateIR(filename)

    ## find the block leaders
    findLeaders()
    genBlocks()
    makeVarList()
    genInitialSymbolTable()
    populateNextUseTable()

    ## TEST
    codeTester()

def codeTester():
    for k,v in symTable.items():
        print("{} : {}, {}".format(k, v.typ, v.status))



if __name__ == "__main__":

    """
        Structures
    """

    reglist = ['%eax', '%ebx','%ecx','%edx']
    registers = { i:None for i in reglist}

    arithOp = ['+','-','%','/','*'] 

    addressDescriptor = {}
    nextUseTable = {}

    irlist =[]

    varlist = []
    leaders = [1,]
    ## blocks == leader : instr block
    blocks = {}

    symTable = {}
    nodes = []

    assemblyCode = ""

    main()
