#!/usr/bin/env python

from sys import path, argv
path.extend(['.','..'])

import os.path
import re
from myLexer import MyLexer

## GLOBALS

tokens = MyLexer.tokens

def extractTerminals(regMatch):
    rhs = regMatch.group(1).split(' -> ')[1].split()
    lrhs = len(rhs)
    actuals = regMatch.group(2).split(',')
    strx = ''
    for i in range(lrhs):
        if actuals[i] != 'None':
            strx +=  rhs[i] + " -> " + actuals[i][1:-1] + "\n"
    return strx


def getReduceRules(fd):
    reducedString = ""
    matchPat = re.compile('^Action : Reduce rule \[([^]]+)\] with \[([^]]+)\] .*')
    for line in fd:
        x = matchPat.search(line)
        if x != None:
            reducedString += extractTerminals(x)
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
        ruleIndex = prevLine.rfind(lhs) ## TODO :: confirm if it does full string match
        if lhs in tokens:
            htmlCode += "\t\t<p>" + prevLine[:ruleIndex] + "<i>" \
                + prevLine[ruleIndex:ruleIndex+length_lhs] + "</i>" \
                + prevLine[ruleIndex+length_lhs:] + " </p>\n"
        else:
            htmlCode += "\t\t<p>" + prevLine[:ruleIndex] + "<b>" \
                + prevLine[ruleIndex:ruleIndex+length_lhs] + "</b>" \
                + prevLine[ruleIndex+length_lhs:] + " </p>\n"

        if rhs.strip() == "empty":
            rhs = ""
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
