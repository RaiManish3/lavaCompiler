#!/usr/bin/env python

from sys import path, argv
path.extend(['.','..'])

import os.path
import re
import ast
from myLexer import MyLexer

## GLOBALS
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
tokens = MyLexer.tokens

def extractTerminals(regMatch):
    rhs = regMatch.group(1).split(' -> ')[1].split()
    subs = regMatch.group(2)
    lrhs = len(rhs)
    if 'COMMA' in rhs:
        subs = '[' + subs + ']'
        subs = ast.literal_eval(subs)
        actuals = []
        for i in subs:
            if i == None:
                actuals.append('None')
            else:
                actuals.append('\''+i.strip()+'\'')
    else:
        actuals = subs.split(',')
    strx = ''
    stry = ''
    for i in range(lrhs):
        if actuals[i] != 'None':
            strx += rhs[i] + ", "
            stry += actuals[i][1:-1] + ", "
    if strx == '':
        return strx
    return strx[:-2] + " -> " + stry[:-2] + "\n"


def getReduceRules(fd):
    reducedString = ""
    matchPat = re.compile('^Action : Reduce rule \[([^]]+)\] with \[(([^]]|\'\]\')+)\] .*')
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
            *{
                margin: 0;
                padding: 0;
            }
            div.rule{
                margin: 10px auto;
                padding: 10px;
                background-color: white;
                width: 80%;
            }
            div.main{
                background-color: rgba(200,200,200,0.8);
                padding: 10px;
            }
            div.tab{
                margin-left: 10px;
            }
        </style>
        </head>
        <body>
            <div class="main">

   """

    reversedList = reversed(reducedString.split('\n')[:-1])
    prevHtmlLine = "\t\t<div class='rule'> program </div>\n"

    for i in reversedList:
        lhs, rhs = i.split(' -> ')
        lhsList = lhs.split(', ')
        rhsList = rhs.split(', ')
        l_lhsList = len(lhsList)
        lastHtmlIndex = 0
        thisHtmlLine = ''
        nextHtmlLine = prevHtmlLine

        for i in range(l_lhsList):
            lhsRule = lhsList[i]
            rhsRule = rhsList[i]

            if rhsRule.strip() == "empty":
               rhsRule = "" 

            htmlIndex = prevHtmlLine.rfind(lhsRule) ## TODO :: confirm if it does full string match
            htmlIndex2 = nextHtmlLine.rfind(lhsRule)

            nl = pl = ''
            if lhsRule in ['BEGIN', 'THEN']:
                pl = '<br>'
                nl = '<br><div class="tab">'
            elif lhsRule in ['STMT_TERMINATOR']:
                nl = '<br>'
            elif lhsRule in ['ELSE']:
                pl = '</div>'
                nl = '<br><div class="tab">'
            elif lhsRule in ['END']:
                pl = '</div>'
                nextStringIndex = htmlIndex + 4
                if len(prevHtmlLine[nextStringIndex:]) > 9:
                    maxIndex = nextStringIndex + 9
                else:
                    maxIndex = nextStringIndex + len(prevHtmlLine[nextStringIndex:])
                if '</div>end' != prevHtmlLine[nextStringIndex:maxIndex]:
                    nl = '<br>'

            if lhsRule in tokens:
                thisHtmlLine += prevHtmlLine[lastHtmlIndex:htmlIndex] + pl + "<i>" \
                    + prevHtmlLine[htmlIndex:htmlIndex+len(lhsRule)] + "</i>" + nl
            else:
                thisHtmlLine += prevHtmlLine[lastHtmlIndex:htmlIndex] + "<b>" \
                    + prevHtmlLine[htmlIndex:htmlIndex+len(lhsRule)] + "</b>"

            nextHtmlLine = nextHtmlLine[:htmlIndex2] + pl + rhsRule + nl \
                + nextHtmlLine[htmlIndex2+len(lhsRule):]

            lastHtmlIndex = htmlIndex+len(lhsRule)

        htmlCode += thisHtmlLine + prevHtmlLine[lastHtmlIndex:]
        prevHtmlLine = nextHtmlLine

    htmlCode += prevHtmlLine
    htmlCode += "\t    </div>\n\t</body>\n\t</html>"
    return htmlCode


if __name__ == "__main__":
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
