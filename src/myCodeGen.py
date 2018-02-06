#!/usr/bin/env python


"""
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

from includes import utility, symClasses
import copy
from enum import Enum
import argparse

class stat(Enum):
    LIVE = 1
    DEAD = 2

class SymbolClass(object):
    def __init__(self, typ, status,instr):
        self.typ = typ
        self.status = status
        self.instr=instr 

def setLocation(var, location):
    addressDescriptor[var] = location

def getLocation(var):
    return addressDescriptor[var]

def setReg(reg, value):
    registers[reg]=value

def getReg(var, lineno):
    # var is a symbol table enrtry
    # x =y op z, then var is x
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
            farthestNextUse = [k ,v]

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
        for var in varlist:
            symTable[var].status = stat.DEAD
            symTable[var].instr = None

        for b in block[::-1]:
            nextUseTable[b[0]] = {var:copy.deepcopy(symTable[var]) for var in varlist}
            optr = b[1]
            instr = b[0]

            # INSTRUCTION NUMBER NEEDED
            if optr == '=':
                symTable[b[2]].status = stat.DEAD
                symTable[b[2]].instr = instr
                if b[3] in varlist:
                    symTable[b[3]].status = stat.LIVE
                    symTable[b[3]].instr = instr

            elif optr in arithOp:
                symTable[b[2]].status = stat.DEAD
                symTable[b[2]].instr = instr
                if b[3] in varlist:
                    symTable[b[3]].status = stat.LIVE
                    symTable[b[3]].instr = instr
                if b[4] in varlist:
                    symTable[b[4]].status = stat.LIVE
                    symTable[b[4]].instr = instr

            elif optr == 'ifgoto':
                if b[3] in varlist:
                    print(b[3])
                    symTable[b[3]].status = stat.LIVE
                    symTable[b[3]].instr = instr
                if b[4] in varlist:
                    symTable[b[4]].status = stat.LIVE

            elif optr == 'print':
                if b[2] in varlist:
                    symTable[b[2]].status = stat.LIVE
                    symTable[b[2]].instr = instr
            # TODO
            # add other if else statements also


def genInitialSymbolTable():
    for v in varlist:
        symTable[v] = SymbolClass(int, stat.LIVE, None)
        addressDescriptor[v]='mem'  ## initially no variable is loaded onto the registers

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
            elif ir[1] == 'goto':
                leaders.append(int(ir[2]))

        # Each file should correspond to a separate function, with filename
        # same as function name
        elif ir[1] == 'label':
            leaders.append(ir[0]) ## doubt here

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


def populateSymWithGlobal():
    global symTable    
    for v in varlist:
        ## ASSUMPTION, program list has 1st class Main
        program['Main'].globalSymTable[v] = SymbolClass('int', stat.DEAD, None); 
        addressDescriptor[v]='mem'  ## initially no variable is loaded onto the registers
    symTable = program['Main'].globalSymTable

def main():
    global varlist
    filename = getFilename()
    populateIR(filename)

    symClasses.makeSymStructure(program)
    varlist = utility.makeVarList(irlist)
    ## find the block leaders
    findLeaders()
    genBlocks()
    populateSymWithGlobal();
    populateNextUseTable()

    ## TEST
    codeTester()

def codeTester():
    #  for k,v in symTable.items():
        #  print("{} : {}, {}".format(k, v.typ, v.status))
    #  print(" ");
    for k,v in nextUseTable.items():
        print("::::::  Line No. {} ::::::".format(k))
        for k1,v1 in v.items():
            print("{} --> {}, {}, {}".format(k1,v1.typ,v1.status,v1.instr));



if __name__ == "__main__":

    """
        Structures
    """

    program = {} 

    reglist = ['%eax', '%ebx','%ecx','%edx']
    registers = { i:None for i in reglist}
    #Register Descriptor maps from regname to symbol table entry of that
    #variable

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
