from copy import deepcopy
from enum import Enum
import sys

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

typeSizeMap = {'int': 4, 'real': 8, 'boolean': 1, 'string': None} ## FIXME :: String size ?? 

class Category(Enum):
    Class=1
    Function=2
    Interface=3
    Block=4


class VarType(object):
    def __init__(self, name, category, vtype, size=None):
        self.name=name
        self.category = category
        self.vtype = vtype
        #  self.size = size

    def __repr__(self):
        return "category: {}, type: {}".format(self.category, self.vtype)

class SymbolTable(object):
    def __init__(self, category, attr, parent=None):
        self.category = category  ## class or function or interface or block
        self.parent = parent
        self.attr = deepcopy(attr)  ## holds all relevant information for this block
        self.vars = {}  ## contains variables directly under it
        self.temps= {}  ## contains temporaries direclty under it
        self.children = [] if category in ['function', 'block'] else {}  ## list of blocks under it

    def insert(self, lexeme, ltype, category):
        ## category can either be array or a simple variable
        ## TODO :: case of array
        size = typeSizeMap[ltype]
        self.vars[lexeme] = VarType(lexeme,category, ltype, size)
        return self.vars[lexeme]

    def insertTemp(self, lexeme, ltype, category):
        ## category can either be array or a simple variable
        ## TODO :: case of array
        if ltype!=None:
            size = typeSizeMap[ltype]
        self.temps[lexeme] = VarType(lexeme,category, ltype, size)
        return self.temps[lexeme]

    def lookup(self, lexeme):
        #TODO DO WE NEED TO CHECK THE FUNCTIONS ALSO HERE ???
        if lexeme in self.vars:
            return self.vars[lexeme]
        return None

    def printMe(self):
        ## printing attributes first
        if len(self.attr) > 0:
            print("Attributes: ")
            for k,v in self.attr.items():
                print(k + ":" + v)
        ## printing vars
        if len(self.vars) > 0:
            print("Variables: ")
            for k,v in self.vars.items():
                print(k + ":" + v)

    def setAttr_Cat(self,category,attr):
        self.category = category
        self.attr=deepcopy(attr)



class TableManager(object):
    def __init__(self):
        self.currentTable = {}
        #self.currentTable = None
        #self.makeTable(None,None,None)
        self.mainTable = self.currentTable
        self.tempCount = 0
        self.labelCount = 0

    def makeTable(self, name, category, attr):
        #self.currentTable =  SymbolTable(category,attr,self.currentTable)
        ##NOTE The below will be taken care in parser code

        ## class :: attr should be interface
        ## function :: attr are returnType, argsLength, argsTypes
        ## interface and block have no attribute
        pass

    #NOTE DISCUSS THIS
    def setAttr_Cat(self,category,attr):
        self.currentTable.setAttr_cat(category,attr)


    def newTemp(self,ltype, table=None):
        if table==None:
            table= self.currentTable
        self.tempCount+=1
        return table.insertTemp('`t' + str(self.tempCount-1),ltype,None)

    def newLabel(self):
        label = "L" + str(self.labelCount)
        self.labelCount += 1
        return label

    #def lookup(self, lexeme, table = self.currentTable):
    #TODO Above line was giving error so I changed, please check
    def lookup(self, lexeme, table=None):
        if table == None:
            table =self.currentTable
        #ASSUMPTION -- Temporaries are not called for lookup
        if type(table) != dict:
            val = table.lookup(lexeme)
            if val != None:
                return val
            if table.parent == None:
                return None
            return self.lookup(lexeme, table.parent)
        return None

    def insert(self, lexeme, ltype, category):
        #TODO CHECK WHETHER THE VARIABLE ALREADY EXISTS IN SYM TALBLE OT NOT
        #TODO JUST CHECK ONLY IN CURRENT SYM TABLE, NOT THE PARRENT & THE STUFF
        return self.currentTable.insert(lexeme, ltype, category)

    def beginScope(self, category, attr):
        newTab = SymbolTable(category, attr, self.currentTable)
        if type(self.currentTable) == dict:
            ## newTab has to be a class or an interface
            self.currentTable[attr['name']] = newTab
        elif self.currentTable.category in ['class', 'interface']:
            ## newTab cannot be a block but a function
            self.currentTable.children[attr['name']] = newTab
        elif self.currentTable.category in ['function', 'block']:
            self.currentTable.children.append[newTab]
        else:
            print("Unknown Argument !!")
            exit(EXIT_FAILURE)
        self.currentTable = newTab
        return self.currentTable

    def endScope(self):
        self.currentTable = self.currentTable.parent

    #def printMe(self, t = self.mainTable):
    #TODO Above line was giving error so I changed, please check
    def printMe(self, t):
        if type(t) == dict:
            for k,v in t:
                self.printMe(v)
        else:
            if t.category != 'block':
                print("beginScope for: " + t.attr['name'])
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
