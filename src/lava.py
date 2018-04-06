from sys import path
path.extend(['.','..'])

from includes import SymTab
from src import myParser, myCodeGen


def printIR(irList):
    for i in irList:
        print(', '.join(map(str,i)))

def main():
    irList = myParser.main()['code']
    printIR(irList)
    #  myCodeGen.main(irList)

if __name__ == '__main__':
    main()
