class luaClass(object):
    """docstring for luaClass."""
    def __init__(self):
        self.globalSymTable = {}
        self.funcList = {}
        ## Why dict, so that its easy to access the function with function name

class luaInterface(object):
    """docstring for luaClass."""
    def __init__(self):
        self.funcDecList = {}
        ## Why dict, so that its easy to access the function with function name

class funcDef(object):
    def __init__(self):
        self.localSymTable ={}
        self.irlist = []

def makeSymStructure(program):
    ## we would have the lift before hand
    ## we are harcoding Main class, and main function 
    mainClass = luaClass()
    # mainClass.symTable = the current symbol table
    mainClass.funcList['main'] = funcDef();

    program['Main'] = mainClass
