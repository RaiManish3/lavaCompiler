from sys import path
import os
path.extend(['.','..'])

import ply.lex as lex
import ply.yacc as yacc
from myLexer import MyLexer

from sys import argv

## GLOBALS
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

class MyParser(object):
    
    tokens = MyLexer.tokens
    
    # Precedence and associativity of operators
    precedence = (
        ('right', 'EQ'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'BIT_OR'),
        ('left', 'BIT_XOR'),
        ('left', 'BIT_AND'),
        ('left', 'EQEQ', 'NTEQ'),
        ('left', 'GT', 'GE', 'LT', 'LE'),
        ('left', 'RSHIFT', 'LSHIFT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MODULUS'),
        ('right', 'NOT'),
        ('left', 'DOT') ## member access
    )

    def __init__(self, lexer):
        self.lexer = lex.lex(module=MyLexer())

    def p_program(self, p):
        '''
            program : expression
        '''

    def p_expression(self, p):
        '''
            expression : expression MULTIPLY expression
                       | expression DIVIDE expression
                       | expression PLUS expression
                       | expression MINUS expression
                       | INTEGER_LITERAL
        '''

    def p_error(self, p):
        print('\n-------------------------------------------------------')

        print('Error: \'{}\' at line no: {}'.format(p.value, p.lineno))

        if len(argv) == 2:
            filename = argv[1]
        elif len(argv) == 3:
            filename = argv[2]

        with open(filename,'r') as fp:
            for i, line in enumerate(fp):
                if i+1 == p.lineno:
                    print("\t\t\tin {}".format(line.strip(),))

        print('-------------------------------------------------------')

        exit(EXIT_FAILURE)


class Parser(object):

    def __init__(self):
        self.lexer = lex.lex(module=MyLexer())
        self.parserObj = MyParser(self.lexer)
        self.parser = yacc.yacc(module=self.parserObj, start='program')

    def read_file(self, _file):
        if type(_file) == str:
            _file = open(_file)
        content = _file.read()
        _file.close()
        return content

    def tokenize_string(self, code):
        self.lexer.input(code)
        for token in self.lexer:
            print(token)

    def tokenize_file(self, _file):
        content = self.read_file(_file)
        return self.tokenize_string(content)

    def parse_string(self, code, debug=False, lineno=1):
        return self.parser.parse(code, lexer=self.lexer, debug=debug)

    def parse_file(self, _file, debug=False):
        content = self.read_file(_file)
        parse_ret = self.parse_string(content, debug=debug)
        return parse_ret


def handle_errors(argv):
    fileIndex = -1

    if len(argv) == 2:
        fileIndex = 1
    elif len(argv) == 3:
        fileIndex = 2

    if fileIndex > -1:

        if fileIndex == 2:
            if argv[1] not in ['-l', '-p']:
                print('No such option \'{}\''.format(argv[1]))
                exit(EXIT_FAILURE)
                
        if argv[fileIndex].find('.lua') == -1:
            print('\'{}\' is not a .lua file'.format(argv[fileIndex]))
            exit(EXIT_FAILURE)

        elif not os.path.isfile(argv[fileIndex]):
            print('file \'{}\' does not exists'.format(argv[fileIndex]))
            exit(EXIT_FAILURE)

    else:
        print('To run script: src/parser.py [mode] <path_to_file> ')
        exit(EXIT_FAILURE)


if __name__=="__main__":
    # initialize Parser
    parser = Parser()
    handle_errors(argv)

    # for Tokenizing a file
    if argv[1] == '-l':
        parser.tokenize_file(argv[2])
        exit()

    else:
        if argv[1] == '-p':
            filename = argv[2]
        else:
            filename = argv[1]

        result = parser.parse_file(filename, debug = True)
