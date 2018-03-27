from copy import deepcopy
from enum import Enum
import sys

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

typeSizeMap = {'int': 4, 'real': 8, 'boolean': 1, 'String': None} ## FIXME :: String size ??

class Category(Enum):
    Class=1
    Function=2
    Interface=3
    Block=4

class VarType(object):
    def __init__(self, lexeme, category, vtype, size=None):
        self.lexeme = lexeme
        self.category = category
        self.type = vtype
        self.size = size

    def __repr__(self):
        return "category: {}, type: {}".format(self.category, self.type)

    def __str__(self):
        return self.lexeme

class SymbolTable(object):
    def __init__(self, category, attr, parent=None):
        self.category = category  ## class or function or interface or block
        self.parent = parent
        self.attr = deepcopy(attr)  ## holds all relevant information for this block
        self.vars = {}  ## contains variables directly under it
        self.temps= {}  ## contains temporaries direclty under it
        self.children = [] if category in [Category.Function, Category.Block] else {}

    def insert(self, lexeme, ltype, category):
        ## category can either be array or a simple variable
        ## TODO :: case of array
        if ltype != None:
            size = typeSizeMap[ltype]
        else:
            size = None
        self.vars[lexeme] = VarType(lexeme,category, ltype, size)
        return self.vars[lexeme]

    def lookup(self, lexeme):
        #TODO DO WE NEED TO CHECK THE FUNCTIONS ALSO HERE ???
        if lexeme in self.vars:
            return self.vars[lexeme]
        if self.category in [Category.Class, Category.Interface]:
            if lexeme in self.children:
                return self.children[lexeme]
        return None

    def printMe(self):
        ## printing attributes
        if len(self.attr) > 0:
            print("## Attributes ##")
            for k,v in self.attr.items():
                print(k + " -> " + str(v))
        ## printing vars
        if len(self.vars) > 0:
            print("## Variables ##")
            for k,v in self.vars.items():
                print(k + " -> " + repr(v))

    def setAttr_Cat(self, category, attr):
        self.category = category
        self.attr = deepcopy(attr)



class TableManager(object):
    def __init__(self):
        self.currentTable = {}
        self.mainTable = self.currentTable
        self.labelCount = 0

    #NOTE DISCUSS THIS
    def setAttr_Cat(self, category, attr):
        self.currentTable.setAttr_cat(category,attr)

    def newLabel(self):
        self.labelCount += 1
        return "L" + str(self.labelCount - 1)

    def lookup(self, lexeme, table = None, flag = False):
        if table == None:
            table = self.currentTable

        if type(table) != dict:
            val = table.lookup(lexeme)
            if val != None:
                return val
            if table.parent == None:
                return None

            if not flag:
                return self.lookup(lexeme, table.parent)

        return None

    def insert(self, lexeme, ltype, category):
        assert (self.currentTable != dict ), "Global Variables Encountered"
        return self.currentTable.insert(lexeme, ltype, category)

    def beginScope(self, category, attr):
        newTab = SymbolTable(category, attr, self.currentTable)
        if type(self.currentTable) == dict:
            ## newTab has to be a class or an interface
            self.currentTable[attr['name']] = newTab
        elif self.currentTable.category in [Category.Class, Category.Interface]:
            ## newTab cannot be a block but a function
            self.currentTable.children[attr['name']] = newTab
        elif self.currentTable.category in [Category.Function, Category.Block]:
            self.currentTable.children.append[newTab]
        else:
            raise ValueError("Invalid Category Encountered")
        self.currentTable = newTab
        return self.currentTable

    def endScope(self):
        self.currentTable = self.currentTable.parent

    def printMe(self, t = None):
        if t == None:
            t = self.mainTable

        if type(t) == dict:
            for k,v in t.items():
                self.printMe(v)
        else:
            print("="*50)
            if t.category != 'block':
                print("beginScope for: " + str(t.category) + " : " + t.attr['name'])
            else:
                print("newScope :: ")

            t.printMe()
            if type(t.children) == dict:
                for k,v in t.children.items():
                    self.printMe(v)
            else:
                ## it must be a list
                for v in t.children:
                    self.printMe(v)

            if t.category != 'block':
                print("endScope for: " + t.attr['name'])
            else:
                print(":: closeScope")
            print("="*50)


tmpCount = 0
def newTemp(ltype):
    global tmpCount
    tmpCount += 1
    return VarType('`t' + str(tmpCount-1), None, ltype)
