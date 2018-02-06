import re

def isnumber(num):
    return re.match('-?\d+', num) != None


"""
   This program takes a ircode and writes all global variables into a file.
"""
def makeVarList(irlist):
    localVarList = set()
    for ir in irlist:
        if ir[1] in ['ifgoto', 'call', 'ret', 'label']:
            pass
        else:
            ## statements of the form :: lineno, operator, { var | literal ,}
            for i in range(2,len(ir)):
                if not isnumber(ir[i]):
                    localVarList.add(ir[i])
    return list(localVarList)[:]
