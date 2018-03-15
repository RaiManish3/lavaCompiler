#!/usr/bin/env python

from sys import path, argv
path.extend(['.','..'])

import os.path
import re
import ast
from myLexer import MyLexer
import linecache

## GLOBALS
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
tokens = MyLexer.tokens

def handleLongString(reqToken):
    curLine = lineno - 1
    strLine = linecache.getline(filename, curLine)
    tokenIndex = strLine.find(reqToken+" .") ## left to right search for index : Only works if our assumption is correct
    tokenPat = re.compile('^' + strLine[:tokenIndex] + '\. LexToken\(' + reqToken +',\'(.+)\',.*')

    while curLine > 0:
        ## bottom up search from current line
        curLine -= 1
        strLine = linecache.getline(filename, curLine)
        tmp = tokenPat.search(strLine)
        if tmp != None:
            return tmp

    print("Could not find right string for token at line: !!", lineno)
    exit(EXIT_FAILURE)


def extractTerminals(regMatch):
    rhs = regMatch.group(1).split(' -> ')[1].split()
    subs = regMatch.group(2)
    lrhs = len(rhs)
    if '<str @ 0x' not in subs:
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
        if actuals[i].startswith('<str @ 0x'):
            ## Case of relatively long string
            ## NOTE : Works for a single long string token in a rule.
            actuals[i] = "'" + handleLongString(rhs[i]).group(1) + "'"

        if actuals[i] != 'None':
            strx += "$" + rhs[i] + ", "
            stry += actuals[i][1:-1] + ", "
    if strx == '':
        return strx
    return strx[:-2] + " -> " + stry[:-2] + "\n"


def getReduceRules(fd):
    global lineno
    reducedString = ""
    matchPat = re.compile('^Action : Reduce rule \[([^]]+)\] with \[(([^]]|\'\]\')+)\] .*')
    for line in fd:
        x = matchPat.search(line)
        if x != None:
            reducedString += extractTerminals(x)
            lhs, rhs = x.group(1).split(' -> ')
            lhs = "$" + lhs
            rhs = ' '.join(map(lambda x: "$"+x, rhs.split()))
            reducedString +=  lhs + " -> " + rhs + '\n'
        lineno+=1
    return reducedString

def removeMarker(text):
    strx = ''
    quoteFlag = False
    dquote = False
    i, l = 0, len(text)
    while i < l:
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == '"' :
            quoteFlag = not quoteFlag
        if not text[i] == '$' or quoteFlag:
            strx += text[i]
        i += 1
    return strx


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
                word-wrap: break-word;
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
    prevHtmlLine = "\t\t<div class='rule'> $program </div>\n"

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

            if rhsRule.strip() == "$empty":
               rhsRule = "" 

            htmlIndex = prevHtmlLine.rfind(lhsRule)
            htmlIndex2 = nextHtmlLine.rfind(lhsRule)

            nl = pl = ''
            if lhsRule in ['$BEGIN', '$THEN']:
                pl = '<br>'
                nl = '<br><div class="tab">'
            elif lhsRule == '$STMT_TERMINATOR':
                nl = '<br>'
            elif lhsRule == '$ELSE':
                pl = '</div>'
                nl = '<br><div class="tab">'
            elif lhsRule == '$END':
                pl = '</div>'
                nextStringIndex = htmlIndex + 5
                if 'class' == prevHtmlLine[nextStringIndex:nextStringIndex+5] or 'interface' == prevHtmlLine[nextStringIndex:nextStringIndex+9]:
                    nl = '<br><br>'
                elif '</div>end' != prevHtmlLine[nextStringIndex+1:nextStringIndex+9]:
                    nl = '<br>'

            if lhsRule[1:] in tokens:
                thisHtmlLine += prevHtmlLine[lastHtmlIndex:htmlIndex] + pl + "<i>" \
                    + prevHtmlLine[htmlIndex:htmlIndex+len(lhsRule)] + "</i>" + nl
            else:
                thisHtmlLine += prevHtmlLine[lastHtmlIndex:htmlIndex] + "<b>" \
                    + prevHtmlLine[htmlIndex:htmlIndex+len(lhsRule)] + "</b>"

            nextHtmlLine = nextHtmlLine[:htmlIndex2] + pl + rhsRule + nl \
                + nextHtmlLine[htmlIndex2+len(lhsRule):]

            lastHtmlIndex = htmlIndex+len(lhsRule)

        htmlCode += removeMarker(thisHtmlLine + prevHtmlLine[lastHtmlIndex:])
        prevHtmlLine = nextHtmlLine

    htmlCode += prevHtmlLine
    htmlCode += "\t    </div>\n\t</body>\n\t</html>"
    return htmlCode


if __name__ == "__main__":
    filename = argv[1]
    lineno = 1
    if os.path.exists(filename):
        fd = open(filename, 'r')
        reducedString = getReduceRules(fd)
        htmlCode = beautifyHtml(reducedString)
        fd.close()
        try:
            directory = "bin/"
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(directory + argv[2], 'w') as fs:
                fs.write(htmlCode)
        except:
            print("Cannot write to file!")
            exit(EXIT_FAILURE)
    else:
        print("File Does Not Exist ...")
