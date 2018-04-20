#!/usr/bin/env python

import sys
import os
sys.path.extend(['..','.'])

from includes import utility, SymTab
import copy
from enum import Enum
import argparse
from decimal import Decimal

## GLOBALS=============================================================
"""
    Structures
"""
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
flag_isMoveZfromMem = True
irlist =[]

dirtybit ={}
floatOp={'+': 'add', '-':'sub', '*':'mul', '/':'div'
         , '<': '0000000100000000B', '>': '0000000000000000B', '==':'0100000000000000B'}
floatOp['<='] = floatOp['>']
floatOp['>='] = floatOp['<']
floatOp['~='] = floatOp['==']
labelCount = 0
paramOffset = 16 ## 4 bytes for ret_address and 4 bytes for pushing the ebp in the callee

symlist = []
varlist = []
leaders = [1,]
blocks = {}
strdeclnum=0

Ylenglobal=None
Zlenglobal=None

assemblyCode = ""
floatGlobalDataCode = ""
floatLiteralCount = 0
translatingMainFlag = False
strassemblyCode=""
arraylist=[]

DEBUG_FLAG = False
## GLOBALS=============================================================

def getNewLabel():
    global labelCount
    x = "@L" + str(labelCount)
    labelCount += 1
    return x

def addFloatToGlobal(val):
    global floatGlobalDataCode, floatLiteralCount
    x = "@ft_" + str(floatLiteralCount)
    if "." not in val:
        val += ".0"
    floatGlobalDataCode += x + " dq " + val + "\n"
    floatLiteralCount += 1
    return "qword [" + x + "]"

def resolveType(M):
    if isinstance(M, SymTab.VarType):
        typeM = M.type
    else:
        if utility.isFloat(M):
            typeM = 'real'
        if utility.isInt(M):
            typeM = 'int'
        else:
            typeM = 'String'
    return typeM

def handleIntToFloat(x):
    global assemblyCode
    if x in symlist:
        if addressDescriptor[x] != "mem" and dirtybit[x] == True:
            assemblyCode += "  mov dword [" + x.name  + "], " + name(x) + "\n"
            dirtybit[x] = False
        assemblyCode += "  fild dword [" + x.name + "]\n"
    else:
        assert (False), "Code not Implemented"

def OptimizeForYandZ(lineno,regk,X,Y,Z):
    global assemblyCode
    is_MoveAfromMem=True
    is_MoveBfromMem=True

    isYinReg,isZinReg=True,True
    if Y!=None and Y in symlist and addressDescriptor[Y] == "mem":
        isYinReg =False
    if Z!=None and Z in symlist and addressDescriptor[Z] == "mem":
        isZinReg =False
    if Y!=None and Y in symlist:
        if nextUseTable[lineno][Y][0] == utility.stat.DEAD or nextUseTable[lineno][Y][1]==Decimal('inf'):
            isYinReg = True
    if Z!=None and Z in symlist:
        if nextUseTable[lineno][Z][0] == utility.stat.DEAD or nextUseTable[lineno][Z][1]==Decimal('inf'):
            isZinReg = True


    a,b = None, None
    if isZinReg == True and isYinReg == True:
        return
    elif isZinReg == False and isYinReg == True:
        a=Z
        is_MoveAfromMem=flag_isMoveZfromMem
    elif isZinReg == True and isYinReg == False:
        a=Y
    elif Y in symlist and Z in symlist:
        if nextUseTable[lineno][Y][1]<nextUseTable[lineno][Z][1]:
            a, b = Y, Z
            is_MoveBfromMem=flag_isMoveZfromMem
        else:
            a, b = Z, Y
            is_MoveAfromMem = flag_isMoveZfromMem

    reg = None
    if X==None or a!=X:
        reg =getRegWithContraints(nextUseTable[lineno][a][1]+1,regk,None,lineno)
        if reg == None:
            return
        else:
            if is_MoveAfromMem:
                assemblyCode += "  mov "+reg +", dword ["+ a.name +"]\n"
            associate(a,reg)

    if b != None and b != a and (X == None or b != X):
        reg =getRegWithContraints(nextUseTable[lineno][b][1]+1,regk,reg,lineno)
        if reg == None:
            return
        else:
            if is_MoveBfromMem:
                assemblyCode += "  mov "+reg +", dword ["+ b.name +"]\n"
            associate(b, reg)


def translate3OpStmt(opInstr, X, Y, Z, lineno):
    global flag_isMoveYtoX,assemblyCode

    reg = getReg(X,Y,Z,lineno,None)

    isXinMem = True
    if reg == None:
        reg = getRegWithContraints(0, None, None, lineno)
        assemblyCode += "  mov " + reg + ", dword [" + X.name +"]\n"
    else:
        isXinMem = False
        OptimizeForYandZ(lineno, reg, X, Y, Z)


    # NOTE CHECK WHETHER IN THIS IF, THERE SHOULD BE USE OF flag_isMoveYtoX OR NOT
    if opInstr in relOp:
        if Y not in symlist:
            regy = getRegWithContraints(0, reg, None, lineno)
            assemblyCode+="  mov "+regy+", "+Y+"\n"
        elif addressDescriptor[Y] == "mem" and Z not in symlist:
            regy=getRegWithContraints(nextUseTable[lineno][Y][1]+1,reg,None,lineno)
            if regy==None:
                regy= "dword ["+Y.name+"]"
            else:
                assemblyCode +="  mov "+regy+", "+name(Y)+"\n"
                associate(Y, regy)
        elif addressDescriptor[Y] == "mem" and addressDescriptor[Z] == "mem":
            regy = getRegWithContraints(0,reg,None,lineno)
            assemblyCode+="  mov "+regy+", dword ["+Y.name+"]\n"
            associate(Y, regy)
        elif addressDescriptor[Y]=="mem":
            regy=name(Y)
        else:
            regy=addressDescriptor[Y]

        if Y in symlist and Z in symlist and Y.type=="String" and Z.type=="String":
            assert(False)
            if Y.stringlen!=Z.stringlen:
                assemblyCode += "  mov "+reg+", 0\n"
            else:
                if registerDesc["ecx"]!=None:
                    if dirtybit[registerDesc['ecx']]==True:
                        assemblyCode += '  mov dword ['+registerDesc['ecx'].name+'], ecx\n'
                    associate(registerDesc['ecx'],'mem')
                eqlabel=stManager.newLabel()
                afterlabel=stManager.newLabel()
                assemblyCode += "  mov esi, "+name(Y)+"\n"
                assemblyCode += "  mov edi, "+name(Z)+"\n"
                assemblyCode += "  mov ecx, "+str(Y.stringlen)+"\n"
                assemblyCode += "  cld\n"
                assemblyCode += "  repe cmpsb\n"
                assemblyCode += "  jecxz "+eqlabel+"\n"
                assemblyCode += "  mov "+reg+", 0\n"
                assemblyCode += "  jmp "+afterlabel+"\n"
                assemblyCode += eqlabel+":\n"
                assemblyCode += "  mov "+reg+", 1\n"
                assemblyCode += afterlabel+":\n"



        else:
            assemblyCode += "  xor " + reg + ", " + reg + "\n"
            assemblyCode += "  cmp " + regy +", " + name(Z) + "\n"

            if opInstr == "==":
                assemblyCode += "  sete "+reg[1]+'l\n'
            elif opInstr == "<=":
                assemblyCode += "  setle "+reg[1]+'l\n'
            elif opInstr == ">=":
                assemblyCode += "  setge "+reg[1]+'l\n'
            elif opInstr == "<":
                assemblyCode += "  setl "+reg[1]+'l\n'
            elif opInstr == ">":
                assemblyCode += "  setg "+reg[1]+'l\n'
            elif opInstr == "~=":
                assemblyCode += "  setne "+reg[1]+'l\n'
            else:
                assert(False)

        dirtybit[X]=True


    else:
        if flag_isMoveYtoX == False:
            flag_isMoveYtoX = True
        else:
            assemblyCode += "  mov " + reg + ", " + name(Y) + "\n"

        #if Y.scope == 'Local':
            ## TODO: MAKE CHANGES FOR LOCAL VARIABLE
        #    pass

        if not (Y in symlist and Z in symlist and Y.type=="String" and Z.type=="String"):
            assemblyCode += opInstr + reg + ", " + name(Z) + "\n"
        else:
            # assert(False  )

            #STRINGLEN
            if Y==Zlenglobal or Y==Ylenglobal or Z==Zlenglobal or Z==Ylenglobal:
                assert(False)
            assemblyCode+="\n\n"
            assemblyCode+="  mov edi, dword ["+Y.name+"]\n"
            if registerDesc['ecx']!=None:
                assemblyCode+="  mov dword ["+registerDesc['ecx'].name+"], ecx\n"
                associate(registerDesc['ecx'].name,"mem")
            if registerDesc['eax']!=None:
                assemblyCode+="  mov dword ["+registerDesc['eax'].name+"], eax\n"
                associate(registerDesc['eax'].name,"mem")
            assemblyCode+="  sub ecx, ecx\n"
            assemblyCode+="  sub al, al\n"
            assemblyCode+="  not ecx\n"
            assemblyCode+="  cld\n"
            assemblyCode+="  repne scasb\n"
            assemblyCode+="  not	ecx\n"
            assemblyCode+="  dec ecx\n"
            assemblyCode+="  mov dword ["+Ylenglobal.name+"], ecx\n"

            # assemblyCode+="  mov edi, dword ["+Z.name+"]\n"
            # assemblyCode+="  sub ecx, ecx\n"
            # assemblyCode+="  sub al, al\n"
            # assemblyCode+="  not ecx\n"
            # assemblyCode+="  cld\n"
            # assemblyCode+="  repne scasb\n"
            # assemblyCode+="  not	ecx\n"
            # assemblyCode+="  dec ecx\n"
            # assemblyCode+="  mov dword ["+Zlenglobal.name+"], ecx\n"



#     sub	ecx, ecx
# 	sub	al, al
# 	not	ecx
# 	cld
# repne	scasb
# 	not	ecx
# 	dec	ecx
            assemblyCode+="  push dword ["+Ylenglobal.name+"]\n"
            assemblyCode+="  push debug_d\n"
            assemblyCode+="  call printf\n"
            assemblyCode+="  push dword ["+str(Z.name)+"]\n"
            assemblyCode+="  push debug_s\n"
            assemblyCode+="  call printf\n"
            # assemblyCode+="  push dword ["+Ylenglobal.name+"]\n"
            # assemblyCode+="  push debug_d\n"
            # assemblyCode+="  call printf\n"

            assemblyCode += "  mov esp, ebp\n"
            assemblyCode += "  pop ebp\n"
            assemblyCode += "  ret\n"

            assemblyCode+="  mov "+reg+", dword ["+Ylenglobal.name+"]\n"
            assemblyCode+="  add "+reg+", dword ["+Zlenglobal.name+"]\n"
            assemblyCode+="  inc "+reg+"\n"
            assemblyCode += "  sub esp, "+reg+"\n"
            assemblyCode += "  mov "+reg+", esp\n"
            assemblyCode+="\n\n"



            assemblyCode += "  mov dword ["+X.name+"],"+reg+"\n"
            if registerDesc["ecx"]!=None:
                if dirtybit[registerDesc['ecx']]==True:
                    assemblyCode += '  mov dword ['+registerDesc['ecx'].name+'], ecx\n'
                associate(registerDesc['ecx'],'mem')
            assemblyCode += "  mov esi, dword ["+Y.name+"]\n"
            assemblyCode += "  mov edi, "+reg+"\n"
            assemblyCode += "  mov ecx, dword ["+Ylenglobal.name+"]\n"
            assemblyCode += "  cld\n"
            assemblyCode += "  rep movsb\n"
            # dumpAllRegToMem()
            #if registerDesc[reg]!=None and dirtybit[registerDesc[reg]]==True:
            #    assemblyCode += "  mov dword ["+ registerDesc[reg].name+"], "+reg+"\n"
            #    dirtybit[registerDesc[reg]]=False
            #    associate(registerDesc[reg],"mem")

            assemblyCode += "  mov "+reg+", dword ["+X.name+"]\n"
            assemblyCode += "  add "+reg+", dword ["+Ylenglobal.name+"]\n"
            assemblyCode += "  mov esi, dword ["+Z.name+"]\n"
            assemblyCode += "  mov edi, "+reg+"\n"
            assemblyCode += "  mov ecx, dword ["+Zlenglobal.name+"]\n"
            assemblyCode += "  inc ecx\n"
            assemblyCode += "  cld\n"
            assemblyCode += "  rep movsb\n"
            assemblyCode += "  sub "+reg+", dword ["+Ylenglobal.name+"]\n"
            assemblyCode+="\n\n"



        #if Z.scope == 'Local':
            ## TODO: MAKE CHANGES FOR LOCAL VARIABLE
        #    pass

    remReg(X)

    if isXinMem == False:
        registerDesc[reg] = X
        addressDescriptor[X] = reg
        dirtybit[X]=True
    else:
        addressDescriptor[X] ="mem"



    if Z in symlist and addressDescriptor[Z]!="mem":
        if nextUseTable[lineno][Z][0]==utility.stat.LIVE and nextUseTable[lineno][Z][1]==Decimal('inf'):
            if True:#Z.scope == 'Global':
                if dirtybit[Z]:
                    dirtybit[Z]=False
                    assemblyCode += "  mov dword [" + Z.name + "], " + addressDescriptor[Z] + "\n"
            #TODO: MAKE CHANGES FOR LOCAL VARIABLE
            registerDesc[addressDescriptor[Z]] = None
            addressDescriptor[Z]="mem"


def associate(X,reg):
    if reg=="mem":
        assert(addressDescriptor[X]!="mem")
        registerDesc[addressDescriptor[X]]=None
        addressDescriptor[X]="mem"
        return
    registerDesc[reg] = X
    addressDescriptor[X] = reg

def remReg(X):
    count=0
    for reg in reglist:
        if registerDesc[reg] == X:
            addressDescriptor[X] = "mem";
            registerDesc[reg]=None
            count=count+1

######################################################################
######################################################################

    #NOTE NOTE NOTE NOTE NOTE REMOVE THIS ASSERT BEFORE SUBMISSION
    if DEBUG_FLAG:
        assert(count<=1)

def name(X):
    if X not in symlist:
        return str(X)
    if addressDescriptor[X]!="mem":
        return addressDescriptor[X]
    if X.type != 'real':
        return "dword ["+X.name+"]"
    else:
        return "qword ["+X.name+"]"

def dumpAllRegToMem():
    global assemblyCode
    for reg in reglist:
        if registerDesc[reg] != None:
             if dirtybit[registerDesc[reg]]:
                 dirtybit[registerDesc[reg]]=False
                 assemblyCode += "  mov dword [" + registerDesc[reg].name + "], " + reg + "\n";
             addressDescriptor[registerDesc[reg]] = "mem"
             registerDesc[reg] = None

def translateMulDiv(op,X,Y,Z,lineno):
    global assemblyCode

    regy=None
    if Y not in symlist or addressDescriptor[Y]=="mem":
        regy=getRegWithContraints(0,None,None,lineno)
        assemblyCode+="  mov "+regy+", "+name(Y)+"\n"
        if Y in symlist:
            associate(Y,regy)
    if regy=='eax' or (Y in symlist and addressDescriptor[Y]=="eax"):
        pass;
    elif registerDesc['eax']==None:
        assemblyCode+="  mov eax, "+name(Y)+"\n"
        if Y in symlist:
            registerDesc[addressDescriptor[Y]]=None
            associate(Y,'eax')
    elif dirtybit[registerDesc['eax']]==False:
        associate(registerDesc['eax'],"mem")
        assemblyCode+="  mov eax, "+name(Y)+"\n"
        if Y in symlist:
            registerDesc[addressDescriptor[Y]]=None
            associate(Y,'eax')
    else:
        dirtybit[registerDesc['eax']]=False
        assemblyCode+="  mov dword ["+registerDesc['eax'].name+"], eax\n"
        associate(registerDesc['eax'],"mem")
        assemblyCode+="mov eax, "+name(Y)+"\n"
        if Y in symlist:
            registerDesc[addressDescriptor[Y]]=None
            associate(Y,'eax')

    if Y in symlist:
        regytemp=getRegWithContraints(nextUseTable[lineno][Y][1]+1,'eax','edx',lineno)
        if regytemp==None and dirtybit[Y]:
            dirtybit[Y]=False
            assemblyCode+="  mov dword ["+Y.name+"], eax\n"
            associate(Y,'mem')
        elif regytemp==None:
            associate(Y,'mem')
        else:
            assemblyCode+="  mov "+regytemp+", eax\n"
            associate(Y,regytemp)

    registerDesc['eax']=None
    if registerDesc['edx']==None:
        pass
    elif dirtybit[registerDesc['edx']]==False:
        associate(registerDesc['edx'],"mem")
    else:
        dirtybit[registerDesc['edx']]=False
        assemblyCode+="  mov dword ["+registerDesc['edx'].name+"], edx\n"
        associate(registerDesc['edx'],"mem")

    if op =="/" or op =="%":
        assemblyCode += "  cdq\n"

        if Z not in symlist or addressDescriptor[Z]=="mem":
            regz=getRegWithContraints(0,'eax','edx',lineno)
            if regz!=None:
                assemblyCode+="  mov "+regz+", "+name(Z)+"\n"
                if Z in symlist:
                    associate(Z,regz)
            assemblyCode += "  idiv " + regz + "\n"
        else:
            assemblyCode += "  idiv " + addressDescriptor[Z] + "\n"

        remReg(X)

        if op=="/":
            if addressDescriptor[X]!="mem":
                registerDesc[addressDescriptor[X]]=None
            associate(X,'eax')
        if op=="%":
            if addressDescriptor[X]!="mem":
                registerDesc[addressDescriptor[X]]=None
            associate(X,'edx')
        dirtybit[X]=True

    elif op=="*":
        if Z not in symlist or addressDescriptor[Z]=="mem":
            regz=getRegWithContraints(0,'eax','edx',lineno)
            if regz!=None:
                assemblyCode+="  mov "+regz+", "+name(Z)+"\n"
                if Z in symlist:
                    associate(Z,regz)
            assemblyCode += "  imul " + regz + "\n"
        else:
            assemblyCode += "  imul " + addressDescriptor[Z] + "\n"
        remReg(X)
        if addressDescriptor[X]!="mem":
            registerDesc[addressDescriptor[X]]=None
        associate(X,'eax')
    dirtybit[X]=True


## FLOATS ========================================================================
def compareFloats(op, X, Y, Z, lineno):
    ## this function is supposed to be called only by translateFloatRelOpStmt
    global assemblyCode
    regx = getReg(X, Y, Z, lineno, None)
    associate(X, regx)
    l1 = getNewLabel()
    l2 = getNewLabel()

    assemblyCode += "  fcom st0, st1\n"
    assemblyCode += "  fstsw " + regx[1:] + "\n"
    assemblyCode += "  and " + regx + ", 0100011100000000B\n"
    assemblyCode += "  cmp " + regx + ", " + floatOp[op] + "\n"
    assemblyCode += "  je " + l1 + "\n"
    if op in ['<','>','==']:
        assemblyCode += "  mov " + regx + ", 0\n"
        assemblyCode += "  jmp " + l2 + "\n"
        assemblyCode += l1 + ":\n"
        assemblyCode += "  mov " + regx + ", 1\n"
        assemblyCode += l2 + ":\n"
    else:
        assemblyCode += "  mov " + regx + ", 1\n"
        assemblyCode += "  jmp " + l2 + "\n"
        assemblyCode += l1 + ":\n"
        assemblyCode += "  mov " + regx + ", 0\n"
        assemblyCode += l2 + ":\n"


def getFPUOrder(op, Y, Z):
    if op in ['<', '>', '==']:
        return (Z, Y)
    return (Y, Z)

def writeFPUinstr(X):
    global assemblyCode
    if X in symlist:
        if X.type == 'real':
            assemblyCode += "  fld " + name(X) + "\n"
        elif X.type == 'int':
            handleIntToFloat(X)
        else:
            assert (False), "Code not implemented"
    else:
        assemblyCode += "  fld " + addFloatToGlobal(X) + "\n"


def translateFloatRelOpStmt(op, X, Y, Z, lineno):
    M, N = getFPUOrder(op, Y, Z)
    writeFPUinstr(M)
    writeFPUinstr(N)
    compareFloats(op, X, Y, Z, lineno)

def translateFloatArithOpStmt(op, X, Y, Z):
    global assemblyCode
    op = floatOp[op]
    writeFPUinstr(Y)
    writeFPUinstr(Z)
    assemblyCode += "  f" + op + "\n"
    assemblyCode += "  fstp " + name(X) + "\n"

## FLOATS ========================================================================

def translate(ir):
    global assemblyCode, flag_isMoveYtoX, \
        translatingMainFlag, strassemblyCode, \
        strdeclnum, paramOffset, Ylenglobal, Zlenglobal
    lineno = ir[0]
    op = ir[1]

    # DEBUG -------------------------------
    if DEBUG_FLAG:
        print('------------------------------------')
        for s in symlist:
            if nextUseTable[lineno][s][0] == utility.stat.DEAD and addressDescriptor[s]!="mem":
                print("WARNING: {} was dead and in register {} ".format(s.name,addressDescriptor[s]))
    # DEBUG -------------------------------

    if op in relOp:
        X, Y, Z = ir[2:5]
        typeY = resolveType(Y)
        typeZ = resolveType(Z)
        if typeY in ['int', 'boolean'] and typeZ in ['int', 'boolean']:
            translate3OpStmt(op,X,Y,Z,lineno)
        elif typeY == 'real' or typeZ == 'real':
            translateFloatRelOpStmt(op, X, Y, Z, lineno)
        else:
            assert False, "Code not implemented"

    if op in arithOp:
        X, Y, Z = ir[2:5]

        if X.type == 'int':
            # TODO ARRRAYS
            if op == '+':
                translate3OpStmt('  add ', X, Y, Z, lineno)
            elif op == '-':
                translate3OpStmt('  sub ', X, Y, Z, lineno)
            else:
                translateMulDiv(op, X, Y, Z, lineno)

        elif X.type == 'real':
            translateFloatArithOpStmt(op, X, Y, Z)
        elif X.type == 'String':
            Ylenglobal=ir[5]
            Zlenglobal=ir[6]
            translate3OpStmt('  add ', X, Y, Z, lineno)
        else:
            # print(ir)
            assert False, "Code not implemented"

    if op == "label":
        assemblyCode += ir[2] + ":\n";

    if op == "subesp":
        assemblyCode+= "  sub esp, "+str(ir[2])+"\n"

    if op =="malloc":
        assemblyCode+="  sub esp, "+name(ir[3])+"\n"
        assemblyCode+="  mov "+ name(ir[2])+", esp\n"

    if op=="moveit":
        assemblyCode+="  mov "+ir[2]+"\n"

    if op=="moveobj":
        reggg=getRegWithContraints(0,None,None,lineno)
        assemblyCode+="  mov "+reggg+", dword ["+ir[2].name+"]\n"
        assemblyCode+="  mov dword [esp-12], "+reggg+"\n"


    if op == "param":
        X = ir[2]
        xSize = 0
        if X in symlist:
            xSize = X.size
        elif utility.isFloat(X):
            xSize = 8
        elif utility.isInt(X):
            xSize = 4
        else:
            xSize = 4
        paramOffset += xSize
        if xSize == 4:
            if name(X).startswith('dword'):
                regX = getRegWithContraints(0,None,None,lineno)
                assemblyCode += "  mov " + regX + ", " + name(X) + "\n"
                associate(X, regX)
                assemblyCode += "  mov " + "dword [esp-" + str(paramOffset) + "], " + regX + "\n"
            else:
                assemblyCode += "  mov " + "dword [esp-" + str(paramOffset) + "], " + name(X) + "\n"
        elif xSize == 8:
            assemblyCode += "  fld " + addFloatToGlobal(X) + "\n"
            assemblyCode += "  fstp " + "qword [esp-" + str(paramOffset) + "]\n"

    if op == "=" or op=="not":
        src=ir[3]
        dest=ir[2]
        if src != dest:

            if dest.type == 'real':
                if src in symlist:
                    if src.type == "real":
                        assemblyCode += "  fld " + name(src) + "\n"
                    elif src.type == "int":
                        handleIntToFloat(src)
                    else:
                        assert (False), "TypeError"
                else:
                    assemblyCode += "  fld " + addFloatToGlobal(src) + "\n"
                assemblyCode += "  fstp " + name(dest) + "\n"

            else:
                global flag_isMoveZfromMem
                flag_isMoveZfromMem=False
                OptimizeForYandZ(lineno,None,None,src,dest)
                flag_isMoveZfromMem=True
                if src in symlist and addressDescriptor[src]=="mem" and addressDescriptor[dest]=="mem":
                    reg=getRegWithContraints(0,None,None,lineno)
                    if nextUseTable[lineno][src][1] <= nextUseTable[lineno][dest][1]:
                        assemblyCode += "  mov " + reg + ", " + name(src) +"\n"
                        addressDescriptor[src]=reg;
                        registerDesc[reg]=src;
                    else:
                        # DESTINATION WILL BE INTIIALIZED, NO NEED TO DO THIS
                        assemblyCode += "  mov " + reg + ", " + name(dest) +"\n"
                        addressDescriptor[dest]=reg;
                        registerDesc[dest]=src;
                assemblyCode += "  mov " + name(dest) + ", " + name(src) + "\n"

                if addressDescriptor[dest]!="mem":
                    dirtybit[dest]=True

        if op =="not":
            assemblyCode+="  xor " + name(dest) + ", 1\n"
            if addressDescriptor[dest]!="mem":
                dirtybit[dest] = True

    if op == "function":
        assemblyCode += ir[2] +":\n"
        assemblyCode += "  push ebp\n"
        assemblyCode += "  mov ebp, esp\n"
        assemblyCode += "  finit\n"

    if op == "arg":
        #NOT TO BE USED NOW, SINCE ALL VARIABLES ARE GLOBAL
        pass

    if op == "pop":
        #NOT TO BE USED NOW, SINCE ALL VARIABLES ARE GLOBAL
        pass

    if op in bitOp:
        X, Y, Z = ir[2:5]

        if op == '&':
            translate3OpStmt('  and ', X, Y, Z, lineno)
        elif op == '|':
            translate3OpStmt('  or ', X, Y, Z, lineno)
        elif op == '^':
            translate3OpStmt('  xor ', X, Y, Z, lineno)

    if op in shiftOp:
        X, Y, Z = ir[2:5]

        if op == '>>':
            translate3OpStmt('  shr ', X, Y, Z, lineno)
        elif op == '<<':
            translate3OpStmt('  shl ', X, Y, Z, lineno)


    if op == "swrite":
        strin=ir[3]
        strle=ir[4]
        strassemblyCode=strassemblyCode+"$str_"+str(strdeclnum)+" dd `"+strin+"`, 0\n"
        assemblyCode+="  mov "+name(ir[2])+", $str_"+str(strdeclnum)+"\n"
        strdeclnum+=1



    if op == "ifgoto":
        relop, X, Y, label = ir[2:6]
        #OptimizeForYandZ(lineno,None,None,X,Y)

        dumpAllRegToMem()
        if X in symlist and Y in symlist and addressDescriptor[X]=="mem" and addressDescriptor[Y]=="mem":
            reg = getRegWithContraints(0,None,None,lineno)
            assemblyCode += "  mov " + reg + ", " + name(X) + "\n"
            assemblyCode += "  cmp " + reg + ", " + name(Y) + "\n"
        else:
            assemblyCode += "  cmp " + name(X) + ", " + name(Y) + "\n"


        if relop == "<=":
                assemblyCode += "  jle " + label + "\n"
        elif relop == ">=":
                assemblyCode += "  jge " + label + "\n"
        elif relop == "==":
                assemblyCode += "  je " + label + "\n"
        elif relop == "<":
                assemblyCode += "  jl " + label + "\n"
        elif relop == ">":
                assemblyCode += "  jg " + label + "\n"
        elif relop == "!=":
                assemblyCode += "  jne " + label + "\n"
        else:
            assert(False)

    if op == 'readarray' or op =="writearray":
        arr=ir[2]
        offset = ir[3]
        dest = ir[4]
        # handle constant
        if ir[3] not in symlist:
            if 'real[]' == arr.type:
                offset=str(8*int(offset)) #every interger if 4 byte
            else:
                offset=str(4*int(offset)) #every interger if 4 byte
            regtemp=getRegWithContraints(0,None,None,lineno)
            assemblyCode+="  mov "+regtemp+", "+offset+"\n"
        else:
            OptimizeForYandZ(lineno,None,None,ir[3],None)
            if addressDescriptor[ir[3]]=="mem":
                regtemp=getRegWithContraints(0,None,None,lineno)
            else:
                regtemp=getRegWithContraints(0,addressDescriptor[ir[3]],None,lineno)
            assemblyCode+="  mov "+regtemp+", "+name(ir[3])+"\n"
            if 'real[]' == arr.type:
                assemblyCode+="  shl "+regtemp +", 3\n"
            else:
                assemblyCode+="  shl "+regtemp +", 2\n"
        assemblyCode+="  add "+regtemp+", "+name(arr)+"\n"

        if op =="readarray":
            if 'real[]' != arr.type:
                assemblyCode+="  mov "+regtemp+", dword [" +regtemp +"]\n"
                if addressDescriptor[ir[4]]!="mem":
                    registerDesc[addressDescriptor[ir[4]]] = None
                associate(ir[4],regtemp)
                dirtybit[ir[4]]=True
            else:
                ## case for real arrays
                assemblyCode+="  fld qword ["+ regtemp +"]\n"
                assemblyCode+="  fstp qword ["+dest.name+"]\n"
        elif op =="writearray":
            if 'real[]' != arr.type:
                OptimizeForYandZ(lineno,None,None,ir[4],None)
                if ir[4] not in symlist or addressDescriptor[ir[4]]!="mem":
                    assemblyCode+="  mov dword ["+regtemp+"], " +name(ir[4]) +"\n"
                else:
                    regtemp2=getRegWithContraints(0,regtemp,None,lineno)
                    assemblyCode+="  mov dword "+regtemp2+", "+name(ir[4])+"\n"
                    assemblyCode+="  mov dword ["+regtemp+"], "+ regtemp2+"\n"
            else:
                ## case for real arrays
                if dest in symlist:
                    assemblyCode+="  fld "+ name(dest) + "\n"
                    assemblyCode+="  fstp qword ["+ regtemp +"]\n"
                else:
                    assemblyCode+="  fld "+ addFloatToGlobal(dest) + "\n"
                    assemblyCode+="  fstp qword ["+ regtemp +"]\n"

    if lineno+1 in leaders or lineno== len(irlist):
        dumpAllRegToMem()

    if op == "goto":
        label = ir[2]
        assemblyCode += "  jmp " + label + "\n"

    if op == "call":
        paramOffset = 16
        dumpAllRegToMem()
        if len(ir)>3:
            if ir[3].type in ['int', 'boolean']:
                associate(ir[3],'eax')
                dirtybit[ir[3]]=True
            assemblyCode += "  sub esp, 8\n"
        assemblyCode += "  call " + ir[2] + "\n"
        if len(ir)>3:
            #  if ir[3].type in ['int', 'boolean']:
                #  regX = getRegWithContraints(0,None,None, lineno)
                #  assemblyCode += "  mov " + regX +", dword [esp]\n"
                #  assemblyCode += "  mov " + name(ir[3]) + ", " + regX + "\n"
            if ir[3].type == 'real':
                assemblyCode += "  fld qword [esp]\n"
                assemblyCode += "  fstp " + name(ir[3]) + "\n"
            assemblyCode += "  add esp, 8\n"

    # Generating assembly code if the tac is a return statement
    if op == "exit":
        assemblyCode += "  call exit\n"

    if op == "print":
        X = ir[2] ## assuming only int literals or int variables
        if "qword" in name(X):
            assemblyCode += "  push dword [" + X.name[:3] + str(int(X.name[3:])+4) +"]\n"
            assemblyCode += "  push dword [" + X.name +"]\n"
        dumpAllRegToMem()
        if isinstance(X, SymTab.VarType):
            if X.type=="String":
                assemblyCode += "  push " + name(X) +"\n"
                assemblyCode += "  push debug_s\n"
            elif X.type=="int":
                assemblyCode += "  push " + name(X) +"\n"
                assemblyCode += "  push debug_d\n"
            elif X.type=="real":
                assemblyCode += "  push debug_f\n"
            elif X.type=="boolean":
                l1 = getNewLabel()
                l2 = getNewLabel()
                assemblyCode += "  cmp " + name(X) + ", 0\n"
                assemblyCode += "  je " + l1 +"\n"
                assemblyCode += "  push @true\n"
                assemblyCode += "  jmp " + l2 + "\n"
                assemblyCode += l1 + ":\n"
                assemblyCode += "  push @false\n"
                assemblyCode += l2 + ":\n"
                assemblyCode += "  push debug_s\n"
        else:
            if utility.isFloat(X):
                assemblyCode += "  push debug_f\n"
            elif utility.isInt(X):
                assemblyCode += "  push " + name(X) +"\n"
                assemblyCode += "  push debug_d\n"
            else:
                assemblyCode += "  push " + name(X) +"\n"
                assemblyCode += "  push debug_s\n"
        assemblyCode += "  call printf\n"

    if op == "readInt":
        X = ir[2] ## assuming only int literals or int variables
        dumpAllRegToMem()
        # temp=stManager.newTemp(X.type)
        reg=getRegWithContraints(0,None,None,lineno)
        assemblyCode += "  lea "+reg+", ["+X.name+"]\n"
        assemblyCode += "  push " + reg +"\n"
        assemblyCode += "  push readInt\n"
        assemblyCode += "  call scanf\n"

    if op == "readFloat":
        X = ir[2] ## assuming only int literals or int variables
        dumpAllRegToMem()
        # temp=stManager.newTemp(X.type)
        reg=getRegWithContraints(0,None,None,lineno)
        assemblyCode += "  lea "+reg+", ["+X.name+"]\n"
        assemblyCode += "  push " + reg +"\n"
        assemblyCode += "  push readFloat\n"
        assemblyCode += "  call scanf\n"

    if op == "readString":
        X = ir[2] ## assuming only int literals or int variables
        dumpAllRegToMem()
        # temp=stManager.newTemp(X.type)self.fail('message')
        reg=getRegWithContraints(0,None,None,lineno)
        # associate(reg,)
        #assemblyCode += "  lea "+reg+", ["+X.name+"]\n"
        # assemblyCode += "  mov esp, 2"
        assemblyCode += "  sub esp, 208\n"
        assemblyCode += "  lea "+reg+", [esp]\n"
        assemblyCode += "  mov dword ["+X.name+"], "+reg+"\n"
        assemblyCode += "  push " + reg +"\n"
        assemblyCode += "  push readString\n"
        assemblyCode += "  call scanf\n"
        assemblyCode += "  mov dword [esp+196], 0\n"


    if op == "return":
        if len(ir) > 2:
            if ir[2] not in symlist:
                if utility.isFloat(ir[2]):
                    assemblyCode +="  fld "+addFloatToGlobal(ir[2])+"\n"
                    assemblyCode +="  fstp qword [ebp+8]\n"
                elif utility.isInt(ir[2]):
                    assemblyCode+="  mov eax, " + str(ir[2]) + "\n"
            elif addressDescriptor[ir[2]]=="mem":
                if ir[2].type =='real':
                    assemblyCode +="  fld "+ name(ir[2]) + "\n"
                    assemblyCode +="  fstp qword [ebp+8]\n"
                else:
                    assemblyCode+="  mov eax, " + name(ir[2]) + "\n"
            else:
                if ir[2].type=='real':
                    assemblyCode +="  fld dword["+ir[2].name+"]\n"
                    assemblyCode +="  fstp qword [ebp+8]"
                elif ir[2].type in ['int','boolean']:
                    assemblyCode +=" mov dword [ebp+4], "+addressDescriptor[ir[2]]+"\n"
                else:
                    assert(False)

        dumpAllRegToMem()

        if translatingMainFlag:
            assemblyCode += "  mov eax, 0\n"
        assemblyCode += "  mov esp, ebp\n"
        assemblyCode += "  pop ebp\n"
        assemblyCode += "  ret\n"


    # DEBUG -------------------------------
    if DEBUG_FLAG:
        print(assemblyCode+"\/ \/ \/")
        for k,v in registerDesc.items():
            if v != None:
                print({k:v.name})
            else:
                print({k:v})
        print("xxxxxxxxxxxxxxx")
        for k,v in addressDescriptor.items():
            if k != None:
                print({k.name:v})
            else:
                print({k:v})
    # DEBUG -------------------------------


def liveInf(X,lineno):
    #ASSUMPTIONS
    assert(X in symlist and addressDescriptor[X]!="mem")
    assert(nextUseTable[lineno][X][0]==utility.stat.LIVE and nextUseTable[lineno][X][1]==Decimal('inf'))
    global assemblyCode
    # DUMP REG TO MEMORY IF DIRTY BIT IS SET AS IT IS NOT USED ANYMORE
    if dirtybit[X]:
        dirtybit[X]=False
        assemblyCode+="  mov "+"dword ["+X.name+"], "+addressDescriptor[X]+"\n"
    associate(X,"mem")

def getRegWithContraints(afterNextUse,reg1,reg2,lineno):
    #NOTE NOTE NOTE, this function does'nt care about other registers
    global assemblyCode
    farthestNextUseDead = 0
    farthestNextUseSymbDead = None
    farthestNextUseLive=0
    farthestNextUseSymbLive=None

    for regname, value in registerDesc.items():
        if reg1 !=None:
            if reg1==regname:
                continue
        if reg2 !=None:
            if reg2==regname:
                continue
        if value == None:
            return regname
        elif nextUseTable[lineno][value][0]==utility.stat.DEAD:
            if nextUseTable[lineno][value][1] > farthestNextUseDead:
                farthestNextUseSymbDead = value
                farthestNextUseDead = nextUseTable[lineno][value][1]
        elif nextUseTable[lineno][value][0]==utility.stat.LIVE:
            # NOTE NOTE NOTE THESE ARE DOUTFULL
            if nextUseTable[lineno][value][1]==Decimal('inf'):
                liveInf(value,lineno)
                return regname
            if nextUseTable[lineno][value][1] > farthestNextUseLive:
                farthestNextUseSymbLive = value
                farthestNextUseLive = nextUseTable[lineno][value][1]

    if farthestNextUseDead==0 and farthestNextUseLive < afterNextUse:
        return None

    if farthestNextUseDead!=0:
        regtemp = addressDescriptor[farthestNextUseSymbDead]
        assert(regtemp!="mem")
        # NOTE DON'T PUSH TO MEMORY IF REG IS DEAD
        # assemblyCode+="  mov "+farthestNextUseSymbDead.name+", "+regtemp+"\n"
        associate(farthestNextUseSymbDead,"mem")
        return regtemp

    if farthestNextUseLive!=0:
        regtemp = addressDescriptor[farthestNextUseSymbLive]
        assert(regtemp!="mem")
        if dirtybit[farthestNextUseSymbLive]:
            dirtybit[farthestNextUseSymbLive]=False
            assemblyCode+="  mov dword ["+farthestNextUseSymbLive.name+"], "+regtemp+"\n"
        associate(farthestNextUseSymbLive,"mem")
        return regtemp


    assert(False)

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

    condition = Y in symlist and addressDescriptor[Y] != "mem" and nextUseTable[lineno][Y][0] == utility.stat.LIVE and nextUseTable[lineno][Y][1]==Decimal('inf')
    #condition = condition
    if condition:
        reg = addressDescriptor[Y]
        if dirtybit[Y]:
            dirtybit[Y]=False
            assemblyCode += "  mov dword [" + Y.name +"], " + addressDescriptor[Y] +"\n"
        associate(Y,"mem")
        flag_isMoveYtoX = False
        return reg

    #NOTE NOTE NOTE, THE BELOW CODE IS JUST FOR HIT AND TRIAL TESTING, IT MAY NOT BE WORKING
    # if X is Y:
    #     assert(addressDescriptor[X]=="mem")
    # OptimizeForYandZ(X,Y)
    # if addressDescriptor[X] !="mem":
    #     return addressDescriptor[X]
    # elif addressDescriptor[Y]!="mem":
    #     assemblyCode+=" mov "
    #HANDLE ALL CASES BEFORE THIS RETURN, THAT WHETER IN OPTIMAL CASE, X CAN GET REISTER OUT OF Y OR Z
    #if Y in symlist and addressDescriptor[Y]!="mem" and addressDescriptor[X]=="mem" and nextUseTable[]

    regy,regz=None,None
    if Y in symlist and addressDescriptor[Y]!="mem":
        regy=addressDescriptor[Y]
    if Z in symlist and addressDescriptor[Z]!="mem":
        regz=addressDescriptor[Z]
    return getRegWithContraints(0,regy,regz,lineno)

def nextUse(var, lineno):
    return nextUseTable[lineno][var][1]

def populateNextUseTable():

    for ldr, block in blocks.items():
        tple = {}

        for s in symlist:
            tple[s]=(utility.stat.LIVE,Decimal('inf'))


        for b in block[::-1]:
            nextUseTable[b[0]] = {s:copy.deepcopy(tple[s]) for s in symlist}
            optr = b[1]
            instr = b[0]

            if optr == '=' or optr == 'not':
                tple[b[2]] = (utility.stat.DEAD,Decimal('inf'))
                if b[3] in symlist:
                    tple[b[3]] = (utility.stat.LIVE,instr)

            elif optr in arithOp or optr in relOp or optr in shiftOp or optr in bitOp:
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

            elif optr == 'print' or optr == 'readInt':
                if b[2] in symlist:
                    tple[b[2]] = (utility.stat.LIVE,instr)

            """
                IT SHOULD ALSO BE ALIVE FOR PARAM,
                1ST UPDATE THE utility.py FOR PARAM, AND OTHER IR statements
                THEN UPDATE HERE
            """
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
    labelToLineMap = {}

    for ir in irlist:
        if ir[1] in ['ifgoto', 'goto']:
            leaders.append(ir[0]+1)
            if ir[1] == 'ifgoto':
                leaders.append(ir[5])
            elif ir[1] == 'goto':
                leaders.append(ir[2])

        elif ir[1] == 'label':
            leaders.append(ir[0]) ## doubt here
            labelToLineMap[ir[2]] = ir[0]

        elif ir[1] == 'function':
            leaders.append(ir[0]) ## doubt here

    leaders = list(set(leaders))
    ## remove custom label form the leaders by line no
    for i in range(len(leaders)):
        if not type(leaders[i]) is int:
            try:
                leaders[i] = labelToLineMap[leaders[i]]
            except KeyError:
                print("IR has inconsistent labels")
                exit(1)
    leaders.sort()

def populateIR(filename):
    try:
        with open(filename, 'r') as infile:
            for i, line in enumerate(infile):
                splitLine =line.strip().split(', ')
                irlist.append([i+1] + splitLine)
    except FileNotFoundError:
        print("Cannot find the file. Make sure the path is right!")
        exit(1)

def populateIR2(data):
    i=1
    for d in data:
        irlist.append([i]+d)
        i+=1

def getFilename():
    argParser = argparse.ArgumentParser(description='Provide the IR code filename')
    argParser.add_argument('filename', type=str, help="./codegen filename.ir")
    args = argParser.parse_args()
    return args.filename

def main(filename=None, irCode=None, stM=None):
    global varlist, symlist, assemblyCode, translatingMainFlag, dirtybit, stManager, arraylist

    stManager=stM

    if irCode:
        populateIR2(irCode)
    else:
        filename = getFilename()
        populateIR(filename)

    utility.makeVarList(irlist, varlist, symlist,arraylist)

    for s in symlist:
        addressDescriptor[s]='mem'  ## initially no variable is loaded in any register

    findLeaders()
    genBlocks()
    populateNextUseTable()

    top_section = "global main\nextern printf\nextern scanf\n\n"
    data_section = "segment .data\n\n" + \
        "debug_d dd `Output :: %d\\n`,0\n" + \
        "debug_f dd `Output :: %f\\n`,0\n" + \
        "debug_s dd `Output :: %s\\n`,0\n" + \
        "readInt dd `%d`,0\n" + "@true dd `true`,0\n" + \
        "@false dd `false`,0\n"

    data_section +=  "readFloat dd `%f`,0\n" + "readString dd `%s`,0\n"
    data_section += "tooLongStringException dd `You gave a continous string of length > 200 without containing whitespace, which is not allowed`,0\n"

    bss_section = "\n"
    text_section = "segment .text\n\n"
    text_section +="main:\n"
    text_section +="  push ebp\n"
    text_section +="  mov ebp, esp\n"
    ofs=stManager.mainTable['Main'].offset;
    text_section +="  sub esp, "+str(ofs)+"\n"
    # text_section +="  pussh esp\n"
    text_section +="  mov [esp-12], esp\n"
    text_section +="  call auto___Zn3_$c$_Main\n"
    text_section +="  mov [esp-12], esp\n"
    text_section +="  call ___Zn3_$c$_Main_$n$_main\n"
    text_section +="  mov eax, 0\n"
    text_section +="  mov esp, ebp\n"
    text_section +="  pop ebp\n"
    text_section +="  ret\n\n"

    for lead,block in blocks.items():
        if block[0][1] == 'function':
            text_section += '\n'
            translatingMainFlag = False
            if block[0][2] == "main":
                translatingMainFlag = True
        else:
            # case of label
            pass

        for s in symlist:
            dirtybit[s]=False

        for v in block:
            translate(v)

        if DEBUG_FLAG:
            for s in symlist:
                print(s.name,dirtybit[s])
                assert(dirtybit[s]==False)

        text_section += assemblyCode
        assemblyCode=""

    data_section+=strassemblyCode
    x86c = top_section + data_section + floatGlobalDataCode+ bss_section + text_section

    ## saving to file
    try:
        directory="asm/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + filename[5:-4]+".s",'w') as f:
            f.write(x86c)
    except:
        print("Cannot write to file!")
        exit(1)

    return x86c


if __name__ == "__main__":
    main()
