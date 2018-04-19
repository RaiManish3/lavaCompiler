from copy import deepcopy
from enum import Enum
import sys

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

typeSizeMap = {'int': 4, 'real': 8, 'boolean': 4, 'String': 4}

class Category(Enum):
    Class=1
    Function=2
    Interface=3
    Block=4

class VarType(object):
    def __init__(self, lexeme, category, vtype, offset, size=None):
        self.xname = lexeme
        self.name='ebp-'+str(offset)
        self.category = category
        self.type = vtype
        self.size = size
        self.offset=offset
        self.stringlen=0

    def updateCategory(self, newCategory):
        self.category = newCategory

    def updateType(self, newType):
        self.type = newType

    def __repr__(self):
        return "name: {}, category: {}, type: {}".format(self.xname, self.category, self.type)

    def __str__(self):
        return self.xname

class SymbolTable(object):
    def __init__(self, category, attr, parent=None):
        self.category = category  ## class or function or interface or block
        self.parent = parent
        self.attr = attr          ## holds all relevant information for this block
        self.vars = {}            ## contains variables directly under it
        self.children = [] if category in [Category.Function, Category.Block] else {}
        self.offset=0

    def insert(self, lexeme, ltype, category):
        ## category can either be array or a simple variable
        offset=None
        size=None
        classeslist = self
        while classeslist.category == Category.Block or classeslist.category == Category.Function:
            classeslist=classeslist.parent
        classeslist=classeslist.parent
        if False:
            offset=5
            size=4
            self.vars[lexeme] = VarType(lexeme,category, ltype, offset, size)
            self.vars[lexeme].name="ebp+8"
            return
        elif ltype in typeSizeMap.keys():
            size = typeSizeMap[ltype]
            tmp = self
            while tmp.category == Category.Block:
                tmp=tmp.parent
            offset=tmp.offset+size
            tmp.offset+=size
        elif isinstance(ltype, SymbolTable):
            assert(False)
            size=4
            tmp = self
            while tmp.category == Category.Block:
                tmp=tmp.parent
            offset=tmp.offset+size
            tmp.offset+=size
        elif ltype in classeslist.keys() or lexeme=="this":
            size=4
            tmp = self
            while tmp.category == Category.Block:
                tmp=tmp.parent
            offset=tmp.offset+size
            tmp.offset+=size
        elif lexeme not in ["`update_block","`after_block"]:
            size = None
            assert(False)

        self.vars[lexeme] = VarType(lexeme,category, ltype, offset, size)
        return self.vars[lexeme]

    def lookup(self, lexeme):
        if lexeme in self.vars:
            return self.vars[lexeme]
        if self.category in [Category.Class, Category.Interface]:
            ## check for function name
            if lexeme in self.children:
                return self.children[lexeme]
        return None

    def printMe(self):
        ## print attributes
        if len(self.attr) > 0:
            print("## Attributes ##")
            for k,v in self.attr.items():
                print(k + " -> " + str(v))
        ## print vars
        if len(self.vars) > 0:
            print("## Variables ##")
            for k,v in self.vars.items():
                print(k + " -> " + repr(v))



class TableManager(object):
    def __init__(self):
        self.currentTable = {}
        self.mainTable = self.currentTable
        self.labelCount = 0
        self.tmpCount = 0


    def newLabel(self):
        self.labelCount += 1
        return "L" + str(self.labelCount - 1)

    def lookup(self, lexeme, table = None):
        if table == None:
            table = self.currentTable

        if type(table) != dict:
            val = table.lookup(lexeme)
            if val != None:
                return val
            if table.parent == None:
                return None

            return self.lookup(lexeme, table.parent)

        else:
            for k in table:
                if k == lexeme:
                    return table[k]
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
            self.currentTable.children.append(newTab)
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


    def newTemp(self, ltype):
        self.tmpCount += 1
        size=None
        if "[]" in ltype:
            size = typeSizeMap[ltype[:str(ltype).find("[]")]]
        elif ltype in self.mainTable.keys():
            size=4
        elif ltype in typeSizeMap.keys():
            size = typeSizeMap[ltype]
        else:
            assert(False)

        tmp = self.currentTable
        while tmp.category == Category.Block:
            tmp=tmp.parent
        offset=tmp.offset+size
        tmp.offset+=size
        return VarType('$t' + str(self.tmpCount-1), 'temp', ltype, offset, size)
