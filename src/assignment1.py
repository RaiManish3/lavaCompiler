#!/usr/bin/env python

import os.path
import sys

sys.path.extend(['.','..'])

import ply.lex as lex
from src import myLexer
import argparse

MyLexer = myLexer.MyLexer

def getTestFileName():
    argParser = argparse.ArgumentParser(description='Provide the filename which is to be lexed')
    argParser.add_argument('filename', type=str, help="filename to be parsed")
    args = argParser.parse_args()
    return args.filename

def iterateOverToken():
    if os.path.exists(filename):
        fs = open(filename, 'r')
        data = fs.read()
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok: break
            tokenTable[tok.type][0] += 1
            tokenTable[tok.type][1].add(tok.value)
        fs.close()
    else:
        print("File Does Not Exists ...")


def prettyPrintTokens():
    print('%20s | %10s | %20s'%("Token", "Occurrances", "Lexemes",))
    print('-'*60)

    for k,v in tokenTable.items():
        if v[0] == 0:
            pass
        else:
            lv = list(v[1])
            l = len(lv)
            print('%20s |  %10d | %20s'%(k, v[0], lv[0],))
            for x in range(1,l):
                print('%20s    %10s   %20s'%("", "", lv[x],))

if __name__ == "__main__":
    tokens = MyLexer.tokens
    tokenTable = { k:[0,set()] for k in tokens}   ## tokenName : [count, occurences]
    
    lexer = lex.lex(module=MyLexer())    ## observation :: if I set optimise argument to 1 then it is not able to parse the strings

    filename = getTestFileName()
    iterateOverToken()
    prettyPrintTokens()
