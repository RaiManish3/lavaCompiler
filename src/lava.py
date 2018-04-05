from sys import path
path.extend(['.','..'])

from includes import SymTab
from src import myParser, myCodeGen

if __name__ == '__main__':
    irList = myParser.main()['code']
    myCodeGen.main(irList)
