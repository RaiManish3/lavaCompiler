class SymbolTable(object):
    def __init__(self, stype, parent):
        self.elems = {}
        self.type = stype
        self.parent = parent

    def insert(self, s,t):
        pass

    def lookup(self, s):
        pass

    def printMe(self):
        pass


class TableManager(object):
    def __init__(self):
        self.currentTable = SymbolTable(None,None)
        self.mainTable = self.currentTable
        self.tempCount = 0
        self.labelCount = 0

    def makeTable(self, stype):
        pass

    def newTemp(self, table):
        pass

    def newLabel(self):
        pass

    def lookup(self, s):
        pass

    def insert(self, s):
        pass

    def beginScope(self):
        pass

    def endScope(self):
        pass

    def printMe(self):
        pass
