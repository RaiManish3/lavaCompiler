import re
from includes import symClasses
from enum import Enum


class SymbolClass(object):
    def __init__(self,name, typ, scope):
        self.name = name
        self.typ = typ
        self.scope = scope

class stat(Enum):
    LIVE = 1
    DEAD = 2


def isnumber(num):
    return re.match('-?\d+', num) != None


## this function extracts variables, converts them into pointer to symbols in symTableDict and also stores them in symlist
def makeVarList(irlist, symTableDict, varlist, symlist):
    ## symlist is a mapping from "symbols" in IRcode to the variable it is pointing to
    tmp_varlist = set()

    for ir in irlist:
        if ir[1] in ['call', 'ret', 'label']:
            pass
        elif ir[1] == "ifgoto":
            for i in range(3,5):
                if not isnumber(ir[i]):
                    tmp_varlist.add(ir[i])
        elif ir[1] == "print":
            if not isnumber(ir[2]):
                tmp_varlist.add(ir[2])
        else:
            ## statements of the form :: lineno, operator, { var | literal ,}
            for i in range(2,len(ir)):
                if not isnumber(ir[i]):
                    tmp_varlist.add(ir[i])

    for i in tmp_varlist:
        varlist.append(i)

    for v in varlist:
        ## ASSUMPTION, program list has 1st class Main
        symTableDict[v] = SymbolClass(v,'int','Global')
        symlist.append(symTableDict[v])


    ## irlist contains statements of the form :: lineno, operator, { var | literal ,}
    ## make "var" a pointer to symTableDict entry
    for ir in irlist:
        if ir[1] in ['call', 'ret', 'label']:
            pass
        elif ir[1] == "ifgoto":
            for i in range(3,5):
                if not isnumber(ir[i]):
                    ir[i] = symTableDict[ir[i]]
        elif ir[1] == "print":
            if not isnumber(ir[2]):
                ir[2] = symTableDict[ir[2]]
        else:
            for i in range(2,len(ir)):
                if not isnumber(ir[i]):
                    ir[i] = symTableDict[ir[i]]
