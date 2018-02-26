#!/usr/bin/env python

from sys import path, argv
path.extend(['.','..'])

import os.path
import re
from myLexer import MyLexer

## GLOBALS

tokens = MyLexer.tokens
FLAG_LITERAL = 0
FLAG_BOP = 1
FLAG_UOP = 2


## TODO :: EXPAND THE LIST TO COVER UP THE TOKEN SET
literal_tokens = ['INTEGER_LITERAL']
bop_tokens = ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']
uop_tokens = ['PLUS','MINUS']

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
        x = matchPat.search(line)
        if x != None:
            reducedString += extractTerminal(x)
            reducedString += x.group(1) + '\n'
    return reducedString


# TODO :: HANDLE ERRORS
def beautifyHtml(reducedString):
    htmlCode = """
        <!DOCTYPE html>
        <html>
        <head>
        <title> cs335 asgn3 </title>
        <style>
            p{
                justify-content: center;
                margin-bottom: 5px;
            }
            div{
                background-color: rgba(240,240,240,0.4);
                margin: 10px;
            }
        </style>
        </head>
        <body>
            <div>
   """

    reversedList = reversed(reducedString.split('\n')[:-1])
    prevLine  = "program"

    for i in reversedList:
        lhs, rhs = i.split(' -> ')
        length_lhs = len(lhs)
        ruleIndex = prevLine.rfind(lhs)
        if lhs in tokens:
            htmlCode += "\t\t<p>" + prevLine[:ruleIndex] + "<i>" \
                + prevLine[ruleIndex:ruleIndex+length_lhs] + "</i>" \
                + prevLine[ruleIndex+length_lhs:] + " </p>\n"
        else:
            htmlCode += "\t\t<p>" + prevLine[:ruleIndex] + "<b>" \
                + prevLine[ruleIndex:ruleIndex+length_lhs] + "</b>" \
                + prevLine[ruleIndex+length_lhs:] + " </p>\n"

        thisLine = prevLine[:ruleIndex] + rhs + prevLine[ruleIndex+length_lhs:]
        prevLine = thisLine

    htmlCode += "\t\t<p>" + prevLine + "</p>\n"
    htmlCode += "\t    </div>\n\t</body>\n\t</html>"
    return htmlCode


if __name__ == "__main__":
    ## for now assume that parser debug is written into a file
    filename = argv[1] 
    if os.path.exists(filename):
        fd = open(filename, 'r')
        reducedString = getReduceRules(fd)
        htmlCode = beautifyHtml(reducedString)
        fd.close()
        try:
            directory = "bin/"
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(directory + "htmlCode.html", 'w') as fs:
                fs.write(htmlCode)
        except:
            print("Cannot write to file!")
            exit(EXIT_FAILURE)
    else:
        print("File Does Not Exist ...")
