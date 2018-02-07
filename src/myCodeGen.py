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
from decimal import Decimal


def setLocation(var, location):
    addressDescriptor[var] = location

def getLocation(var):
    return addressDescriptor[var]

def setReg(reg, value):
    registerDesc[reg]=value

def OptimizeForYandZ(lineno,reg,X,Y,Z):

    global assemblyCode
    if Y in symlist and addressDescriptor[Y] == "mem":
        isYinReg =False
    else:
        isYinReg =True

    if Z in symlist and addressDescriptor[Z] == "mem":
        isZinReg =False
    else:
        isZinReg =True


    a=None
    b=None
    if isZinReg == True and isYinReg == True:
        return
    elif isZinReg == False and isYinReg == True:
        a=Z
    elif isZinReg == True and isYinReg == False:
        a=Y
    elif nextUseTable[lineno][Y][1]<nextUseTable[lineno][Z][1]:
        a=Y
        b=Z

    if a!=X:
        isainReg = False
        farthestNextUse = 0
        farthestNextUseSymb = None
        for regname, value in registerDesc.items():
            if regname == reg:
                continue
            if value == None:
                assemblyCode += "mov " + regname + ", "+ a.name +"\n"
                addressDescriptor[a]=regname
                registerDesc[regname]=a
                isainReg = True
                break
            elif nextUseTable[lineno][value][1] > farthestNextUse:
                farthestNextUseSymb = value
                farthestNextUse = nextUseTable[lineno][value][1]

        if isainReg == False:
            if nextUseTable[lineno][a][1] >= farthestNextUse:
                return
            for regname, value in registerDesc.items():
                if value == farthestNextUseSymb:
                    ## push to memory
                    ## TODO :: confirm with x86 architecture
                    ## THERE IS A BIG PROBLEM HERE ----
                    ## FOR NOW WE SUPPOSE THAT SYMBOL TABLE CONTAINS THE VARIABLE NAME
                    ## WHICH IS NECESSARY FOR THIS CODE GENERATION
                    if value.scope == 'Global':
                        assemblyCode += "mov " + value.name + ", " + regname + "\n"
                        addressDescriptor[value] = "mem"
                    else:
                        assemblyCode +=" Case for local --"
                        ## TODO :: Its a local variable, then use $ebp + offset
                    assemblyCode += "mov " + regname + ", "+ a.name +"\n"
                    addressDescriptor[a]=regname
                    registerDesc[regname]=a
                    isainReg = True
                    break

    if b==None or b==a:
        return

    if b!=X:
        isbinReg = False
        farthestNextUse = 0
        farthestNextUseSymb = None
        for regname, value in registerDesc.items():
            if regname == reg or regname == addressDescriptor[a]:
                continue
            if value == None:
                assemblyCode += "mov " + regname + ", "+ b.name +"\n"
                addressDescriptor[b]=regname
                registerDesc[regname]=b
                isbinReg = True
                break
            elif nextUseTable[lineno][value][1] > farthestNextUse:
                farthestNextUseSymb = value
                farthestNextUse = nextUseTable[lineno][value][1]

        if isbinReg == False:
            if nextUseTable[lineno][b][1] >= farthestNextUse:
                return
            for regname, value in registerDesc.items():
                if value == farthestNextUseSymb:
                    ## push to memory
                    ## TODO :: confirm with x86 architecture
                    ## THERE IS A BIG PROBLEM HERE ----
                    ## FOR NOW WE SUPPOSE THAT SYMBOL TABLE CONTAINS THE VARIABLE NAME
                    ## WHICH IS NECESSARY FOR THIS CODE GENERATION
                    if value.scope == 'Global':
                        assemblyCode += "mov " + value.name + ", " + regname + "\n"
                        addressDescriptor[value] = "mem"
                    else:
                        assemblyCode +=" Case for local --"
                        ## TODO :: Its a local variable, then use $ebp + offset
                    assemblyCode += "mov " + regname + ", "+ b.name +"\n"
                    addressDescriptor[b]=regname
                    registerDesc[regname]=b
                    isbinReg = True
                    break



def translate(ir):
    global assemblyCode,flag_isMoveYtoX

    assem = ""
    lineno = int(ir[0])
    op = ir[1]

    # FOR TEST PUPOSE ONLY, NOTE COMMENT OUT, DON'T REMOVE
    for s in symlist:
        if nextUseTable[lineno][s][0] is utility.stat.DEAD and addressDescriptor[s]!="mem":
            print("WARNING: {} was dead and in register {} ".format(s.name,addressDescriptor[s]))

    if op in arithOp:
        Y = ir[3]
        Z = ir[4]
        X = ir[2]

        # TODO NOTE DON'T FORGET ARRRAYS
        if op == '+':
            reg = getReg(X,Y,Z,lineno,None)
            print(reg)

            #check if x is already in reg or not

            isXinMem = True
            if reg is None:
                reg = X.name
            else:
                isXinMem = False
                OptimizeForYandZ(lineno,reg,X,Y,Z)

            if flag_isMoveYtoX is False:
                flag_isMoveYtoX = True
            elif Y not in symlist:
                 #That means Y is a constant
                 assem += "mov " + reg + ", " + Y + "\n"
            elif addressDescriptor[Y]!="mem":
                 assem += "mov " + reg + ", " + addressDescriptor[Y] + "\n"
            elif Y.scope == 'Global':
                 assem += "mov " + reg + ", " + Y.name + "\n"

            ## TODO: MAKE CHANGES FOR LOCAL VARIABLE

            if Z not in symlist:
                assem += "add " + reg + ", " + Z +"\n"
            elif addressDescriptor[Z]!="mem":
                assem += "add " + reg + ", " + addressDescriptor[Z] +"\n"
            elif Z.scope == 'Global':
                assem += "add " + reg + ", " + Z.name + "\n"

            ## TODO: MAKE CHANGES FOR LOCAL VARIABLE

            #ASSUMPTION -- Same variable cannot be in multiple registers at same time
            for regk in reglist:
                if registerDesc[regk] == X:
                    registerDesc[regk] = None


            #else: WRITE HERE if reg value returned by getReg can be memory location, which is currently not the case


            if isXinMem == False:
                registerDesc[reg] = X
                addressDescriptor[X] = reg
            else:
                addressDescriptor[X] ="mem"

            if Z in symlist and addressDescriptor[Z]!="mem" and nextUseTable[lineno][Z][0]==utility.stat.DEAD:
                if Z.scope == 'Global':
                    assem += "mov " + Z.name + ", " + addressDescriptor[Z] + "\n"
                #TODO: MAKE CHANGES FOR LOCAL VARIABLE
                registerDesc[addressDescriptor[Z]] = None
                addressDescriptor[Z]="mem"



    #DEBUG
    for k,v in registerDesc.items():
        if v is not None:
            print({k:v.name})
        else:
            print({k:v})
    for k,v in addressDescriptor.items():
            if k is not None:
                print({k.name:v})
            else:
                print({k:v})
    print("\/ \/ \/")
    print(assem)

    assemblyCode+=assem




def getReg(X,Y,Z, lineno,isLocal):
    # NOTE, THIS FUNCTION
    # NOTE   DOES NOT UPDATES THE VALUE OF
    # NOTE Register Descriptor variables
    #-----------------------------------------
    # isLocal is none when the var is a global variable
    # Otherwise it should contain offset, such that variable is stored at $ebp + offset
    # var is a symbol table enrtry
    # x =y op z, then var is y
    # this function returns the register for x
    ## if 'var' is present in some register return that register name
    # TODO FULLY OPTIMIZE IT
    # None means, X should use memory

    global flag_isMoveYtoX,assemblyCode
    flag_isMoveYtoX = True


    if nextUseTable[lineno][X][0] == utility.stat.DEAD:
        if Y in symlist and addressDescriptor[Y] == "mem":
            pass
        elif Z is not None and Z in symlist and addressDescriptor[Z] == "mem":
            pass
        else:
            pass

    #ASSUMPTION -- Same variable cannot be in multiple registers at same time

    #if y is same as x, then check if y or x is in memory, and if z is also in memory,
    #o/w
    if Y is X:
        flag_isMoveYtoX = False;
        if addressDescriptor[X]!="mem":
            return addressDescriptor[X]

    if X != Z and addressDescriptor[X]!="mem":
        return addressDescriptor[X]


    #If y is dead and in memory, then we can't put x in same memory location, it must be
    # put in reg. Check for empty reg, if not then chase for a victim
    # we can't put x in memory as we needs 'mov x,y'
    #
    #If y is dead and in register, update the current value of y in memory, update registerDesc and
    # addressDescriptor accorginly return the reg of Y as register of X, set a global flag indicating
    # that we don't need to move Y's value to res, the register in which the value of assembly INSTRUCTION
    # add will be store
    #
    #if y is live or is a constant, then try to get register for x, if there is empty, or steal the register of victim's
    # if victim has farthestNextUse <= those of x, then store it in memory if z is NOT in memory,
    # But if z is in memory take the victim's register even thought its farthestNextUse <= those of x
    # if its farthestNextUse > x then take the victim's reg

    if Y in symlist and nextUseTable[lineno][Y][0] == utility.stat.DEAD:
        if addressDescriptor[Y] == "mem":
            pass;
        if addressDescriptor[Y] != "mem":
            assemblyCode += "mov " + Y.name +", " + addressDescriptor[Y] +"\n"
            reg = addressDescriptor[Y]
            addressDescriptor[Y] ="mem"
            flag_isMoveYtoX = False
            return reg


    farthestNextUse = 0
    farthestNextUseSymb = None
    for regname, value in registerDesc.items():
        if value == None:
            return regname
        elif nextUseTable[lineno][value][1] > farthestNextUse:
            farthestNextUseSymb = value
            farthestNextUse = nextUseTable[lineno][value][1]

    if farthestNextUse <= nextUseTable[lineno][X][1]:
        if Y in symlist and addressDescriptor[Y] == "mem":
            pass
        elif Z is not None and Z in symlist and addressDescriptor[Z] == "mem":
            pass
        else:
            pass
            #return None

    for regname, value in registerDesc.items():
        if value == farthestNextUseSymb:
            ## push to memory
            ## TODO :: confirm with x86 architecture
            ## THERE IS A BIG PROBLEM HERE ----
            ## FOR NOW WE SUPPOSE THAT SYMBOL TABLE CONTAINS THE VARIABLE NAME
            ## WHICH IS NECESSARY FOR THIS CODE GENERATION
            if value.scope == 'Global':
                assemblyCode += "mov " + value.name + ", " + regname + "\n"
                addressDescriptor[value] = "mem"
            else:
                assemblyCode +=" CHANGE HERE --"
                ## TODO :: Its a local variable, then use $ebp + offset
            return regname

def nextUse(var, lineno):
    return nextUseTable[lineno][var]

def populateNextUseTable():
    print(blocks);
    for ldr, block in blocks.items():
        """for var in varlist:
            symTable[var].status = stat.DEAD
            symTable[var].instr = None
        """
        tple = {}
        for s in symlist:
            tple[s]=(utility.stat.DEAD,Decimal('inf'))


        for b in block[::-1]:
            nextUseTable[b[0]] = {s:copy.deepcopy(tple[s]) for s in symlist}
            optr = b[1]
            instr = b[0]

            # INSTRUCTION NUMBER NEEDED
            if optr == '=':
                tple[b[2]] = (utility.stat.DEAD,Decimal('inf'))
                if b[3] in symlist:
                    tple[b[3]] = (utility.stat.LIVE,instr)

            elif optr in arithOp:
                tple[b[2]] = (utility.stat.DEAD,Decimal('inf'))
                if b[3] in symlist:
                    tple[b[3]] = (utility.stat.LIVE,instr)
                if b[4] in symlist:
                    tple[b[4]] = (utility.stat.LIVE,instr)

            elif optr == 'ifgoto':
                if b[3] in symlist:
                    tple[b[3]] = (utility.stat.LIVE,instr)
                if b[4] in symlist:
                    tple[b[4]] = (utility.stat.LIVE,instr)

            elif optr == 'print':
                if b[2] in symlist:
                    tple[b[2]] = (utility.stat.LIVE,instr)

            """IT SHOULD ALSO BE ALIVE FOR PARAM,
            1ST UPDATE THE UTILITY. PY FOR PARAM, AND OTHER IR statements
            THEN UPDATE HERE"""
            # TODO
            # add other if else statements also

"""
def genInitialSymbolTable():
    for v in varlist:
        symTable[v] = SymbolClass(int, stat.LIVE, None)
        addressDescriptor[v]='mem'  ## initially no variable is loaded onto the registers
"""

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

"""
def populateSymWithGlobal():
    global symTable
    for v in varlist:
        ## ASSUMPTION, program list has 1st class Main
        program['Main'].globalSymTable[v] = SymbolClass('int', stat.DEAD, None);
        addressDescriptor[v]='mem'  ## initially no variable is loaded onto the registers
    symTable = program['Main'].globalSymTable
"""


def main():
    global varlist,symTable,symlist,assemblyCode
    filename = getFilename()
    populateIR(filename)

    symClasses.makeSymStructure(program)
    utility.makeVarList(irlist,program['Main'].globalSymTable,varlist,symlist)

    symTable = program['Main'].globalSymTable

    for s in symlist:
        addressDescriptor[s]='mem'  ## initially no variable is loaded onto the registers

    ## find the block leaders

    findLeaders()
    genBlocks()
    populateNextUseTable()

    ## TEST
    codeTester()

    data_section = ".section .data\n"
    for var in varlist:
    	data_section = data_section + var + ":\n" + ".int 0\n"
    data_section = data_section + "str:\n.ascii \"%d\\n\\0\"\n"

    bss_section = ".section .bss\n"
    text_section = ".section .text\n" + ".globl main\n" + "main:\n"

    print(blocks)
    for lead,block in blocks.items():
    	text_section = text_section + "L" + str(lead) + ":\n"
    	for v in block:
    		translate(v)

    text_section = assemblyCode

    #--------------------------------------------------------------------------------------------------

    # Priniting the final output
    # print("Assembly Code (x86) for: [" + filename + "]")
    # print("--------------------------------------------------------------------")
    x86c = data_section + bss_section + text_section
    print(x86c)

def codeTester():
    for k,v in nextUseTable.items():
        print("::::::  Line No. {} ::::::".format(k))
        for k1,v1 in v.items():
            print("{} --> {}, {}".format(k1.name,v1[0],v1[1]));



if __name__ == "__main__":

    """
        Structures
    """

    program = {}

    reglist = ['%eax', '%ebx','%ecx','%edx']
    registerDesc = { i:None for i in reglist}
    #Register Descriptor maps from regname to symbol table entry of that
    #variable

    arithOp = ['+','-','%','/','*']

    addressDescriptor = {}
    nextUseTable = {}

    flag_isMoveYtoX = True

    irlist =[]

    symlist = []
    varlist = []
    leaders = [1,]
    ## blocks == leader : instr block
    blocks = {}

    symTable = {}
    nodes = []

    assemblyCode = ""

    main()
