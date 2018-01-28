class MyLexer(object):

    keywords = ("and" , "begin" , "boolean" , "break" , "class" , "continue" , "else" , "end" , "for" , "function" , "if" , "int" , "implements" , "interface" , "new" , "nil" , "not" , "or" , "real" , "return" , "then", "void" , "while" , "readInt" , "readReal" , "readString" , "print" , "String")


    tokens = [k.upper() for k in keywords] + ["EQ","BIT_OR", "BIT_XOR", "BIT_AND", "EQEQ", "NTEQ", "LT", "LE", "GT", "GE", "LSHIFT", "RSHIFT", "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "MODULUS", "LSQUARE", "RSQUARE", "LPAREN", "RPAREN", "LCURLY", "RCURLY", "DOT", "INTEGER_LITERAL", "FLOAT_LITERAL", "STRING_LITERAL", "BOOLEAN_LITERAL", "IDENTIFIER", "STMT_TERMINATOR", "COMMA", "DCOLON"]


    t_ignore = ' \t\f'                  ## ignore whitespace

    ## ARITHMETIC OPERATORS
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MODULUS = r'%'

    ## BITWISE OPERATIONS
    t_BIT_OR = r'\|'
    t_BIT_XOR = r'\^'
    t_BIT_AND = r'&'
    t_LSHIFT = r'<<'
    t_RSHIFT = r'>>'

    ## RELATIONAL OPERATIONS
    t_GT = r'>'
    t_GE = r'>='
    t_LT = r'<'
    t_LE = r'<='
    t_NTEQ = r'~='
    t_EQEQ = r'=='
    t_EQ = r'='

    ## LITERALS
    t_LSQUARE = r'\['
    t_RSQUARE = r'\]'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LCURLY = r'{'
    t_RCURLY = r'}'
    t_DOT = r'\.'
    t_COMMA = r','
    t_DCOLON = r'::'
    t_STMT_TERMINATOR = r';'

    ## SINGLE LINE COMMENT
    t_ignore_LINE_COMMENT = '--.*'

    ## MULTI-LINE COMMENT -> --[[ SOME TEXT + NEWLINE --]]
    def t_BLOCK_COMMENT(self, t):
        r'--\[\[(.|\n)*?--\]\]'
        t.lexer.lineno += t.value.count('\n')


    ## STRING LITERAL -> "SOME TEXT"
    def t_STRING_LITERAL(self, t):
        r'\"([^\\\n]|(\\.))*?\"'
        return t

    ## FLOAT_LITERAL -> NUM DOT NUM [ EXPONENT PART ]
    def t_FLOAT_LITERAL(self, t):
        r'\d+\.\d+([eE][-+]?\d+)?'
        return t

    ## BOOLEAN LITERAL -> either TRUE or FALSE
    def t_BOOLEAN_LITERAL(self, t):
        r'true|false'
        return t

    ## INTEGER LITERAL -> NUM
    def t_INTEGER_LITERAL(self, t):
        r'\d+'
        return t

    ## IDENTIFIER -> ALPHA { ALPHANUMERIC or UNDERSCORE }
    def t_IDENTIFIER(self, t):
        '[A-Za-z_][A-Za-z0-9_]*'
        if t.value in MyLexer.keywords:
            t.type = t.value.upper()
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_newlineWINDOWS(self, t):
        r'(\r\n)+'
        t.lexer.lineno += len(t.value) / 2

    def t_error(self, t):
        print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
        exit("Program exits ...")
