#!/usr/bin/env python

from sys import path, argv
path.extend(['.','..'])

import os.path
import re

## GLOBALS

FLAG_LITERAL = 0
FLAG_BOP = 1
FLAG_UOP = 2

literal_tokens = ['INTEGER_LITERAL']
bop_tokens = ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']
uop_tokens = ['PLUS','MINUS'] ## TODO :: resolve conflict here

def extractHelper(stx, regMatch, flag):
    if flag == FLAG_LITERAL: 
        tmp = regMatch.group(2)[1:-1]
    elif flag == FLAG_BOP:
        tmp = regMatch.group(2).split(',')[1][1:-1]
    elif flag == FLAG_UOP:
        tmp = regMatch.group(2)[1]
    return stx + " -> " + tmp + '\n'

def extractTerminal(regMatch):
    ## check for literals
    for i in literal_tokens:
        if i in regMatch.group(1):
            return extractHelper(i, regMatch, FLAG_LITERAL)

    ## check for uops
    for i in uop_tokens:
        if i in regMatch.group(1):
            if len(regMatch.group(2).split(','))==3:
                break
            return extractHelper(i, regMatch, FLAG_UOP)

    ## check for binops
    for i in bop_tokens:
        if i in regMatch.group(1):
            return extractHelper(i, regMatch, FLAG_BOP)

    return ''

def getReduceRules(fd):
    reducedString = ""
    matchPat = re.compile('^Action : Reduce rule \[([^]]+)\] with \[([^]]+)\] .*')
    for line in fd:
        #  if line.startswith("Action :") and line[9:].startswith("Reduce rule"):
        x = matchPat.search(line)
        if x != None:
            reducedString += extractTerminal(x)
            reducedString += x.group(1) + '\n'
    return reducedString


def reverseLines(reducedString):
    reversedString = '\n'.join(reversed(reducedString.split('\n')))
    return reversedString


def beautifyHtml(reversedString):
    pass

if __name__ == "__main__":
    ## for now assume that parser debug is written into a file
    filename = argv[1] 
    if os.path.exists(filename):
        fd = open(filename, 'r')
        reducedString = getReduceRules(fd)
        reversedString = reverseLines(reducedString)
        htmlCode = beautifyHtml(reversedString)
        fd.close()
    else:
        print("File Does Not Exist ...")
