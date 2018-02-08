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

def OptimizeForYandZ(lineno,regk,X,Y,Z):
    global assemblyCode

    if Y in symlist and addressDescriptor[Y] == "mem":
        isYinReg =False
    else:
        isYinReg =True

    if Z in symlist and addressDescriptor[Z] == "mem":
        isZinReg =False
    else:
        isZinReg =True

    if Y in symlist and nextUseTable[lineno][Y][0]==utility.stat.DEAD:
        isYinReg = True
    if Z in symlist and nextUseTable[lineno][Z][0]==utility.stat.DEAD:
        isZinReg = True


    a,b = None, None
    if isZinReg == True and isYinReg == True:
        return
    elif isZinReg == False and isYinReg == True:
        a=Z
    elif isZinReg == True and isYinReg == False:
        a=Y
    elif nextUseTable[lineno][Y][1]<nextUseTable[lineno][Z][1]:
        a,b=Y,Z
    else:
        a,b=Z,Y

    if a!=X:
        print(a,X);
        reg =getRegWithContraints(nextUseTable[lineno][a][1]+1,regk,None,lineno)
        if reg == None:
            return
        else:
            assemblyCode +="mov "+reg +" "+ a.name +"\n"
            print("mov "+reg +" "+ a.name +"\n")
            addressDescriptor[a]=reg
            registerDesc[reg]=a

    if b!=None and b!=a and b!=X:
        reg =getRegWithContraints(nextUseTable[lineno][b][1]+1,regk,reg,lineno)
        if reg == None:
            return
        else:
            assemblyCode +="mov "+reg +" "+ b.name +"\n"
            print("mov "+reg +" "+ b.name +"\n")
            addressDescriptor[b]=reg
            registerDesc[reg]=b

def translateArithmetic(opInstr, X, Y, Z, lineno):
    global flag_isMoveYtoX
    assem = ""

    reg = getReg(X,Y,Z,lineno,None)
    print(reg)

    #check if x is already in reg or not
    isXinMem = True
    if reg == None:
        reg = X.name
    else:
        isXinMem = False
        OptimizeForYandZ(lineno, reg, X, Y, Z)

    if flag_isMoveYtoX == False:
        flag_isMoveYtoX = True
    elif Y not in symlist:
         #That means Y is a constant
         assem += "mov " + reg + ", " + Y + "\n"
    elif addressDescriptor[Y]!="mem":
         assem += "kmov " + reg + ", " + addressDescriptor[Y] + "\n"
    elif Y.scope == 'Global':
         assem += "mov " + reg + ", " + Y.name + "\n"

    ## TODO: MAKE CHANGES FOR LOCAL VARIABLE

    if Z not in symlist:
        assem += opInstr + reg + ", " + Z +"\n"
    elif addressDescriptor[Z]!="mem":
        assem += opInstr + reg + ", " + addressDescriptor[Z] +"\n"
    elif Z.scope == 'Global':
        assem += opInstr + reg + ", " + Z.name + "\n"

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

    return assem


def translate(ir):
    print('------------------------------------')
    global assemblyCode,flag_isMoveYtoX

    assem = ""
    lineno = ir[0]
    op = ir[1]

    # DEBUG -------------------------------
    for s in symlist:
        if nextUseTable[lineno][s][0] == utility.stat.DEAD and addressDescriptor[s]!="mem":
            print("WARNING: {} was dead and in register {} ".format(s.name,addressDescriptor[s]))
    # DEBUG -------------------------------

    if op in arithOp:
        X, Y, Z = ir[2:5]

        # TODO ARRRAYS
        if op == '+':
            # NOTE :: add dest, source == dest = dest + source
            assem = translateArithmetic('add ', X, Y, Z, lineno)
        elif op == '-':
            # NOTE :: sub dest, source == dest = dest - source
            assem = translateArithmetic('sub ', X, Y, Z, lineno)
        elif op == '*':
            # NOTE :: multiplication is done in a different manner in x86
            pass
        elif op == '/':
            # NOTE :: same as above
            pass
        elif op == '%':
            # NOTE :: lookup the guide
            pass


    if lineno+1 in leaders or lineno+1==len(irlist):
        for reg in reglist:
            if registerDesc[reg] !=None:
                 assem += "mov " + registerDesc[reg].name + ", " + reg + "\n";
                 addressDescriptor[registerDesc[reg]] ="mem"
                 registerDesc[reg] = None;


    # DEBUG -------------------------------
    for k,v in registerDesc.items():
        if v != None:
            print({k:v.name})
        else:
            print({k:v})
    for k,v in addressDescriptor.items():
        if k != None:
            print({k.name:v})
        else:
            print({k:v})
    print("\/ \/ \/")
    print(assem)
    # DEBUG -------------------------------

    assemblyCode+=assem


def getRegWithContraints(afterNextUse,reg1,reg2,lineno):
    farthestNextUse = 0
    farthestNextUseSymb = None
    for regname, value in registerDesc.items():
        if reg1 !=None:
            if reg1==regname:
                continue
        if reg2 !=None:
            if reg2==regname:
                continue
        if value == None:
            return regname
        elif nextUseTable[lineno][value][1] > farthestNextUse:
            farthestNextUseSymb = value
            farthestNextUse = nextUseTable[lineno][value][1]

    if farthestNextUse > afterNextUse:
        return None

    for regname, value in registerDesc.items():
        if value == farthestNextUseSymb:
            if value.scope == 'Global':
                assemblyCode += "mov " + value.name + ", " + regname + "\n"
                print("mov " + value.name + ", " + regname + "\n")
                addressDescriptor[value] = "mem"
            else:
                ## TODO :: Case of a local variable, then use [ ebp + offset ]
                assemblyCode +=""
            return regname



# this function returns the register for X
def getReg(X,Y,Z, lineno,isLocal):
    # -----------------------------------------
    # | NOTE, THIS FUNCTION
    # | NOTE   DOES NOT UPDATES THE VALUE OF
    # | NOTE Register Descriptor variables
    # -----------------------------------------
    # X = Y op Z, then each of them is a symbol table entry
    # isLocal is none when the var is a global variable
    # Otherwise it should contain offset, such that variable is stored at $ebp + offset
    # TODO FULLY OPTIMIZE IT
    # None means, X should use memory

    global flag_isMoveYtoX, assemblyCode
    flag_isMoveYtoX = True


    #ASSUMPTION -- Same variable cannot be in multiple registers at same time

    #if y is same as x, then check if y or x is in memory, and if z is also in memory,
    #o/w
    if Y is X and addressDescriptor[X]!="mem":
            flag_isMoveYtoX = False;
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

    if Y in symlist and addressDescriptor[Y] != "mem" and nextUseTable[lineno][Y][0] == utility.stat.DEAD:
            assemblyCode += "mov " + Y.name +", " + addressDescriptor[Y] +"\n"
            print("mov " + Y.name +", " + addressDescriptor[Y] +"\n")
            reg = addressDescriptor[Y]
            addressDescriptor[Y] ="mem"
            flag_isMoveYtoX = False
            return reg

    return getRegWithContraints(0,None,None,lineno)

def nextUse(var, lineno):
    return nextUseTable[lineno][var]

def populateNextUseTable():

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
    global varlist, symTable, symlist

    filename = getFilename()
    populateIR(filename)

    symClasses.makeSymStructure(program)
    utility.makeVarList(irlist, program['Main'].globalSymTable, varlist, symlist)

    symTable = program['Main'].globalSymTable

    for s in symlist:
        addressDescriptor[s]='mem'  ## initially no variable is loaded onto the registers

    ## find the block leaders
    findLeaders()
    genBlocks()
    populateNextUseTable()

    ## TEST
    #  codeTester()

    ## FIXME :: this assembly is not consistent with x86 nasm for linux with C library support
    data_section = "section .data\n"
    for var in varlist:
    	data_section = data_section + var + ":\n" + ".int 0\n"
    data_section = data_section + "str:\n.ascii \"%d\\n\\0\"\n"

    bss_section = "segment .bss\n"
    text_section = "segment .text\n" + ".globl main\n" + "main:\n"

    for lead,block in blocks.items():
            #  text_section = text_section + "L" + str(lead) + ":\n"
    	for v in block:
    		translate(v)

    text_section += assemblyCode

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

    reglist = ['eax', 'ebx','ecx','edx']
    registerDesc = { i:None for i in reglist}
    # registerDesc :: Register Descriptor maps from regname to
    #                 symbol table entry of that variable

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

    assemblyCode = ""

    main()
