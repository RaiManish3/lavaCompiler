from sys import path
path.extend(['.','..'])
import os
from sys import argv

from includes import SymTab
from src import myParser, myCodeGen

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def handle_errors(argv):
    if len(argv) == 2:
        if argv[1].find('.lua') == -1:
            print('\'{}\' is not a .lua file'.format(argv[1]))
            exit(EXIT_FAILURE)

        elif not os.path.isfile(argv[1]):
            print('file \'{}\' does not exists'.format(argv[1]))
            exit(EXIT_FAILURE)
    else:
        print('To run script: src/parser.py [mode] <path_to_file> ')
        exit(EXIT_FAILURE)

def printIR(irList):
    for i in irList:
        print(', '.join(map(str,i)))

def main():
    handle_errors(argv)
    filename = argv[1]
    irList = myParser.main(filename)['code']
    asmCode = myCodeGen.main(filename, irList)
    #  printIR(irList)
    #  print(asmCode)

if __name__ == '__main__':
    main()
