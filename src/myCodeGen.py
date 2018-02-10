#!/usr/bin/env python

import sys
sys.path.extend(['..','.'])

from includes import utility, symClasses
import copy
from enum import Enum
import argparse
from decimal import Decimal


def OptimizeForYandZ(lineno,regk,X,Y,Z):
    global assemblyCode

    if Y!=None and Y in symlist and addressDescriptor[Y] == "mem":
        isYinReg =False
    else:
        isYinReg =True

    if Z!=None and Z in symlist and addressDescriptor[Z] == "mem":
        isZinReg =False
    else:
        isZinReg =True

    if Y!=None and Y in symlist and nextUseTable[lineno][Y][0] == utility.stat.DEAD:
        isYinReg = True
    if Z!=None and Z in symlist and nextUseTable[lineno][Z][0] == utility.stat.DEAD:
        isZinReg = True


    a,b = None, None
    if isZinReg == True and isYinReg == True:
        return
    elif isZinReg == False and isYinReg == True:
        a=Z
    elif isZinReg == True and isYinReg == False:
        a=Y
    elif nextUseTable[lineno][Y][1]<nextUseTable[lineno][Z][1]:
        a, b = Y, Z
    else:
        a, b = Z, Y

    if X==None or a!=X:
        reg =getRegWithContraints(nextUseTable[lineno][a][1]+1,regk,None,lineno)
        if reg == None:
            return
        else:
            assemblyCode += "  mov "+reg +", dword ["+ a.name +"]\n"
            addressDescriptor[a]=reg
            registerDesc[reg]=a

    if b != None and b != a and (X == None or b != X):
        reg =getRegWithContraints(nextUseTable[lineno][b][1]+1,regk,reg,lineno)
        if reg == None:
            return
        else:
            assemblyCode += "  mov "+reg +", dword ["+ b.name +"]\n"
            addressDescriptor[b]=reg
            registerDesc[reg]=b


def translate3OpStmt(opInstr, X, Y, Z, lineno):
    global flag_isMoveYtoX
    assem = ""

    reg = getReg(X,Y,Z,lineno,None)

    isXinMem = True
    if reg == None:
        reg = X.name
    else:
        isXinMem = False
        OptimizeForYandZ(lineno, reg, X, Y, Z)


    if opInstr in relOp:

        if addressDescriptor[Y] == "mem" and addressDescriptor[Z] == "mem":
            regy = getRegWithContraints(0,None,None,lineno)
            associate(Y,regy)

        assem += "  xor " + reg + ", " + reg + "\n"
        assem += "  cmp " + name(Y) +", " + name(Z) + "\n"

        if opInstr == "==":
            assem += "  sete "+reg[1]+'l\n'
        elif opInstr == "<=":
            assem += "  setle "+reg[1]+'l\n'
        elif opInstr == ">=":
            assem += "  setge "+reg[1]+'l\n'
        elif opInstr == "<":
            assem += "  setl "+reg[1]+'l\n'
        elif opInstr == ">":
            assem += "  setg "+reg[1]+'l\n'
        elif opInstr == "~=":
            assem += "  setne "+reg[1]+'l\n'



    else:
        if flag_isMoveYtoX == False:
            flag_isMoveYtoX = True
        assem += "  mov " + reg + ", " + name(Y) + "\n"

        #if Y.scope == 'Local':
            ## TODO: MAKE CHANGES FOR LOCAL VARIABLE
        #    pass

        assem += opInstr + reg + ", " + name(Z) + "\n"
        #if Z.scope == 'Local':
            ## TODO: MAKE CHANGES FOR LOCAL VARIABLE
        #    pass

    remReg(X)

    if isXinMem == False:
        registerDesc[reg] = X
        addressDescriptor[X] = reg
    else:
        addressDescriptor[X] ="mem"


    if Z in symlist and addressDescriptor[Z]!="mem" and nextUseTable[lineno][Z][0]==utility.stat.DEAD:
        if Z.scope == 'Global':
            assem += "  mov " + name(Z) + ", " + addressDescriptor[Z] + "\n"
        #TODO: MAKE CHANGES FOR LOCAL VARIABLE
        registerDesc[addressDescriptor[Z]] = None
        addressDescriptor[Z]="mem"

    return assem

def associate(X,reg):
    registerDesc[reg] = X
    addressDescriptor[X] = reg

def remReg(X):
    for reg in reglist:
        if registerDesc[reg] == X:
            addressDescriptor[X]=None;
            registerDesc[reg]=None

def name(X):
    if X not in symlist:
        return X
    if addressDescriptor[X]!="mem":
        return addressDescriptor[X]
    return "dword ["+X.name+"]"

def dumpAllRegToMem():
    assem=""
    for reg in reglist:
        if registerDesc[reg] != None:
             assem += "  mov dword [" + registerDesc[reg].name + "], " + reg + "\n";
             addressDescriptor[registerDesc[reg]] = "mem"
             registerDesc[reg] = None
    return assem

def translateMulDiv(op,X,Y,Z,lineno):
    assem = ""
    reg1 = getRegWithContraints(0,None,None,lineno)
    reg2 = getRegWithContraints(0,reg1,None,lineno)
    regs = ['eax','ebx']

    if reg1 in regs:
        if reg1 =="eax":
            assem += "  mov " + reg2 + ", ebx\n"
            if registerDesc['ebx']!=None:
                associate(registerDesc['ebx'],reg2)
                registerDesc['ebx']=None
        else:
            assem += "  mov " + reg2 + ", eax\n"
            if registerDesc['eax']!=None:
                associate(registerDesc['eax'],reg2)
                registerDesc['eax']=None

    elif reg2 in regs:
        if reg2 == "eax":
            assem += "  mov " + reg1 + ", ebx\n"
            if registerDesc['ebx']!=None:
                associate(registerDesc['ebx'],reg1)
                registerDesc['ebx']=None
        else:
            assem += "  mov " + reg1 + ", eax\n"
            if registerDesc['eax']!=None:
                associate(registerDesc['eax'],reg1)
                registerDesc['eax']=None
    else:
        assem += "  mov " + reg1 + ", eax\n"
        assem += "  mov " + reg2 + ", ebx\n"
        associate(registerDesc['eax'], reg1)
        registerDesc['eax']=None
        associate(registerDesc['ebx'],reg2)
        registerDesc['ebx']=None

    if op =="\\" or op =="%":
        assem += "  cdq\n"
        assem += "  mov eax, " + name(Y) + "\n"
        remReg(Y)
        associate(Y,'eax')

        if addressDescriptor[Z]=="mem":
            assem += "  idiv " + name(Z) + "\n"
        else:
            assem += "  idiv " + addressDescriptor[Z] + "\n"

        remReg(X)

        if op=="\\":
            associate(X,'eax')
        if op=="%":
            associate(X,'edx')

    elif op=="*":
        assem += "  mov eax, " + name(Y) + "\n"
        if addressDescriptor[Z]=="mem":
            assem += "  imul " + name(Z) + "\n"
        else:
            assem += "  imul " + addressDescriptor[Z] + "\n"
        remReg(X)
        associate(X,'eax')

    return assem


def translate(ir):
    print('------------------------------------')
    global assemblyCode,flag_isMoveYtoX, translatingMainFlag

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
            assem = translate3OpStmt('  add ', X, Y, Z, lineno)
        elif op == '-':
            assem = translate3OpStmt('  sub ', X, Y, Z, lineno)
        else:
            assem = translateMulDiv(op, X, Y, Z, lineno)

    if op == "label":
        assem += ir[2] + ":\n";

    if op == "param":
        #THIS CAN BE OPTIMIZE
        assem += "  push " + name(ir[2]) + "\n"

    if op == "=":
        src=ir[3]
        dest=ir[2]
        OptimizeForYandZ(lineno,None,None,src,dest)
        if src in symlist and dest in symlist and addressDescriptor[src]=="mem" and addressDescriptor[dest]=="mem":
            reg=getRegWithContraints(0,None,None,lineno)
            if nextUseTable[lineno][src] <= nextUseTable[lineno][dest]:
                assem += "  mov " + reg + ", " + name(src) +"\n"
                addressDescriptor[src]=reg;
                registerDesc[reg]=src;
            else:
                assem += "  mov " + reg + ", " + name(dest) +"\n"
                addressDescriptor[dest]=reg;
                registerDesc[dest]=src;
        else:
                assem += "  mov " + name(dest) + ", " + name(src) + "\n"

    if op == "function":
        assem += ir[2] +":\n"
        assem += "  push ebp\n"
        assem += "  mov ebp, esp\n"

    if op == "arg":
        #NOT TO BE USED NOW, SINCE ALL VARIABLES ARE GLOBAL
        pass

    if op == "pop":
        #NOT TO BE USED NOW, SINCE ALL VARIABLES ARE GLOBAL
        pass

    if op in bitOp:
        X, Y, Z = ir[2:5]

        if op == '&':
            assem = translate3OpStmt('  and ', X, Y, Z, lineno)
        elif op == '|':
            assem = translate3OpStmt('  or ', X, Y, Z, lineno)
        elif op == '^':
            assem = translate3OpStmt('  xor ', X, Y, Z, lineno)

    if op in shiftOp:
        X, Y, Z = ir[2:5]

        if op == '>>':
            assem = translate3OpStmt('  shr ', X, Y, Z, lineno)
        elif op == '<<':
            assem = translate3OpStmt('  shl ', X, Y, Z, lineno)


    if lineno+1 in leaders or lineno+1 == len(irlist):
        assem += dumpAllRegToMem()

    if op == "ifgoto":
        relop, X, Y, Label = ir[2:6]

        if X in symlist and Y in symlist and addressDescriptor[X]=="mem" and addressDescriptor[Y]=="mem":
            assem += dumpAllRegToMem()
            reg = getRegWithContraints(0,None,None,lineno)
            assem += "  mov " + reg + ", " + name(X) + "\n"
            assem += "  cmp " + reg + ", " + name(Y) + "\n"
        else:
            assem += "  cmp " + name(X) + ", " + name(Y) + "\n"

        #if utility.isnumber(Label):
        label = "L" + Label
        if relop == "<=":
                assem += "  jle " + label + "\n"
        elif relop == ">=":
                assem += "  jge " + label + "\n"
        elif relop == "==":
                assem += "  je " + label + "\n"
        elif relop == "<":
                assem += "  jl " + label + "\n"
        elif relop == ">":
                assem += "  jg " + label + "\n"
        elif relop == "!=":
                assem += "  jne " + label + "\n"

    if op == "goto":
        label = ir[2]
        assem += "  jmp L" + label + "\n"

    if op == "call":
        assem += "  call "+ir[2]+"\n"

    # Generating assembly code if the tac is a return statement
    if op == "exit":
        assem += "  call exit\n"

    if op == "print":
        X = ir[2] ## assuming only int literals or int variables
        assem += "  push " + name(X) +"\n"
        assem += "  push debug\n"
        assem += "  call printf\n"

    if op == "return":
        if registerDesc['eax'] != None:
            assem += "  mov " + name(registerDesc['eax']) + ", eax\n"
            addressDescriptor[registerDesc['eax']] = None
            registerDesc['eax'] = None

        # NOTE NOTE NOTE DO NOT UPDATE REGISTER or ADDRESS DESCRIPTOR HERE
        if len(ir) > 2:
            assem += "  mov eax, " + name(ir[2]) + "\n"

        if translatingMainFlag:
            assem += "  mov eax, 0\n"
        assem += "  mov esp, ebp\n"
        assem += "  pop ebp\n"
        assem += "  ret\n"


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
                assemblyCode += "  mov dword [" + value.name + "], " + regname + "\n"
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
    # isLocal is None when the var is a global variable
    # Otherwise it should contain offset, such that variable is stored at $ebp + offset
    # TODO FULLY OPTIMIZE IT
    # None means, X should use memory

    global flag_isMoveYtoX, assemblyCode
    flag_isMoveYtoX = True


    #ASSUMPTION -- Same variable cannot be in multiple register s at same time

    #if y is same as x, then check if y or x is in memory, and if z is also in memory,
    #o/w
    if Y is X and addressDescriptor[X]!="mem":
            flag_isMoveYtoX = False;
            return addressDescriptor[X]

    if Z!=None and X != Z and addressDescriptor[X]!="mem":
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
            assemblyCode += "  mov dword [" + Y.name +"], " + addressDescriptor[Y] +"\n"
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
        elif ir[1] in ['label','function']:
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

def main():
    global varlist, symTable, symlist, assemblyCode, translatingMainFlag

    filename = getFilename()
    populateIR(filename)

    symClasses.makeSymStructure(program)
    utility.makeVarList(irlist, program['Main'].globalSymTable, varlist, symlist)

    symTable = program['Main'].globalSymTable

    for s in symlist:
        addressDescriptor[s]='mem'  ## initially no variable is loaded onto the register s

    ## find the block leaders
    findLeaders()
    genBlocks()
    populateNextUseTable()

    ## TEST
    #  codeTester()

    top_section = "global main\nextern printf\n\n"
    data_section = "segment .data\n\n" + "debug dd `Testing :: %i\\n`\n"
    for var in varlist:
        data_section += var + "  dd  " + "0\n"

    bss_section = "\n"
    text_section = "segment .text\n\n"

    ## just for now , FIXME later when 'function' code is complete
    #  text_section += "main:\npush ebp\nmov ebp, esp\n"

    for lead,block in blocks.items():
        if block[0][1] == 'function':
            translatingMainFlag = False
            if block[0][2] == "main":
                translatingMainFlag = True
        else:
            text_section += "L" + str(lead) + ":\n"
        for v in block:
            translate(v)
        text_section += assemblyCode
        assemblyCode=""

    ## just for now , FIXME later when 'function' code is complete
    #  text_section += "mov eax, 0\nmov esp, ebp\npop ebp\nret\n"

    x86c = top_section + data_section + bss_section + text_section
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
    bitOp = ['&','|','^']
    shiftOp = ['>>', '<<']
    relOp = ['==', '~=', '>', '<', '>=', '<=']

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
    translatingMainFlag = False

    main()
