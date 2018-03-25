from sys import path
import os
path.extend(['.','..'])

import ply.lex as lex
import ply.yacc as yacc
from myLexer import MyLexer

from sys import argv
from includes import SymTab

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
        self.stManager=SymTab.TableManager()

        #This is needed to make symtable entry before parsing the whole
        #type-variabledeclarators , as to tackle with the problem - int a=2,b=a*a
        self.recentType=None

    def gen(self,x,y,z=None,w=None):
        if w==None:
            if z==None:
                return str(x)+', '+str(y)+'\n'
            else:
                return str(x)+', '+str(y)+', '+str(z)+'\n'
        return str(x)+', '+str(y)+', '+str(z)+', '+str(w)+'\n'

    ## program and class
    def p_program(self, p):
        '''
            program : program class_declaration
                    | program interface_declaration
                    | program STMT_TERMINATOR
                    | empty
        '''
        if p.slice[1].type == 'class_declaration':
            print("class declaration recognized");
        print("recog");
        print(p.slice)
        #if p[2] is main:
        #    p[0]=p[2]+p[1]
        #else
        #    p[0]=p[1]+p[2]

        #p[0]={}
        #p[0]['code']=p[1]['code']+p[2]['code']
        #print(p[0])

    def p_class_declaration(self, p):
        '''
            class_declaration : CLASS IDENTIFIER IMPLEMENTS interface_type_list BEGIN class_body_declarations END
                              | CLASS IDENTIFIER BEGIN class_body_declarations END
        '''
        #p[0]={'code':}
        print(p.slice)

    def p_interface_type_list(self, p):
        '''
            interface_type_list : interface_type_list COMMA interface_type
                                | interface_type
        '''

    def p_class_body_declaration(self, p):
        '''
            class_body_declarations : class_body_declarations class_member_declaration
                                    | class_body_declarations constructor_declaration
                                    | empty
        '''


    def p_class_member_declaration(self, p):
        '''
            class_member_declaration : field_declaration
                                     | method_declaration
        '''

    ## constructor
    def p_constructor_declaration(self, p):
        '''
            constructor_declaration : FUNCTION constructor_declarator constructor_body
        '''

    def p_constructor_declarator(self, p):
        '''
            constructor_declarator : type_name LPAREN formal_parameter_list RPAREN
                                   | type_name LPAREN RPAREN
        '''

    def p_constructor_body(self, p):
        '''
            constructor_body : BEGIN block_statement END
                             | BEGIN END
        '''

    def p_formal_parameter_list(self, p):
        '''
            formal_parameter_list : formal_parameter_list COMMA type variable_declarator_id
                                  | type variable_declarator_id
        '''

    def p_field_declaration(self, p):
        '''
            field_declaration : type variable_declarators STMT_TERMINATOR
        '''
        p[0]={'code':''}
        print(*p)
        if p[2] is None:
            print("p2 is null"+str(p.slice))
        else:
            for i in p[2]:
                #symentry = symtable.insert(p[1]['type'],i['name'])
                symentry = 'thisIsMOckEntryForTest'
                if i[1]!=None:
                    #p[0]['code']=p[0]['code']+self.gen('=',symentry,i[1])
                    p[0].ltype = p[1]['type']
                    p[0].size = SymTab.typeSizeMap[p[1]['type']]
        print(p[0]['code'])

    ## variables
    def p_variable_declarators(self, p):
        '''
            variable_declarators : variable_declarators COMMA variable_declarator
                                 | variable_declarator
        '''
        print(*p)
        if len(p.slice)==2:
            p[0]=[]
            p[0].append(p[1])
        else:
            print("the wrong"+str(p.slice))
            #TODO, the below gives error
            #p[0]=p[1].append((p[3]['name'],p[3]['value']))

    def p_variable_declarator(self, p):
        '''
            variable_declarator : variable_declarator_id
                                | variable_declarator_id EQ variable_initializer
        '''
        print("157"+str(len(p.slice)))
        print(p.slice)
        if len(p.slice)==2:
            p[0]={'name':p[1]['name'],'value':None}
        else:
            #TODO check
            #TODO TYPE CHECK
            #p[0]={'place':p[1],'value':p[3]['place']}
            p[0] = {'place':p[1],'code':gen('=',p[1],p[3]['place'])}
            #TODO
            pass
            print('162'+str(p[0]))

    def p_variable_declarator_id(self, p):
        '''
            variable_declarator_id : variable_declarator_id LSQUARE RSQUARE
                                   | IDENTIFIER
        '''
        #p[0] contains symbol table entry of newly inserted IDENTIFIER,
        #without type and size which will be added later
        print("168"+str(p.slice))
        if str(p.slice[1])=='variable_declarator_id':
            #TODO
            pass
        else:
            p[0] = self.stManager.insert(p.slice[1].value,None,None)
            print('174'+str(p[0]))

    def p_variable_initializer(self, p):
        '''
            variable_initializer : expression
                                 | array_initializer_with_curly
                                 | input
        '''
        #TODO check
        p[0]=p[1]

    def p_input(self, p):
        '''
            input : READINT LPAREN RPAREN
                  | READREAL LPAREN RPAREN
                  | READSTRING LPAREN RPAREN
        '''

    def p_array_initializer_with_curly(self, p):
        '''
            array_initializer_with_curly : LCURLY array_initializer_without_curly RCURLY
                                         | LCURLY RCURLY

        '''

    def p_array_initializer_without_curly(self, p):
        '''
            array_initializer_without_curly : array_initializer_without_curly COMMA variable_initializer
                                            | variable_initializer
        '''

    ## methods
    def p_method_declaration(self, p):
        '''
            method_declaration : method_header method_body
        '''
        print(p.slice)

    def p_method_header(self, p):
        '''
            method_header : FUNCTION DCOLON result_type method_declarator
        '''

    def p_result_type(self, p):
        '''
            result_type : type
                        | VOID
        '''

    def p_method_declarator(self, p):
        '''
            method_declarator : IDENTIFIER LPAREN formal_parameter_list RPAREN
                              | IDENTIFIER LPAREN RPAREN
        '''

    def p_method_body(self, p):
        '''
            method_body : block
                        | STMT_TERMINATOR
        '''

    ## interfaces
    def p_interface_declaration(self, p):
        '''
            interface_declaration : INTERFACE IDENTIFIER interface_body
        '''

    def p_interface_body(self, p):
        '''
            interface_body : BEGIN interface_member_declarations END
                           | BEGIN END
        '''

    def p_interface_member_declarations(self, p):
        '''
            interface_member_declarations : interface_member_declarations interface_member_declaration
                                          | interface_member_declaration
        '''

    def p_interface_member_declaration(self, p):
        '''
            interface_member_declaration : method_header STMT_TERMINATOR
        '''

    ## types
    def p_type(self, p):
        '''
            type : primitive_type
                 | reference_type
        '''
        print(p.slice)
        self.recentType = p[1]
        if str(p.slice[1])=='primitive_type':
           p[0]=p[1]
        if str(p.slice[1])=='reference_type':
            pass
            #TODO

    def p_primitive_type(self, p):
        '''
            primitive_type : INT
                           | REAL
                           | BOOLEAN
                           | STRING
        '''
        # str(p.slice[1])[9:].split(',')[0]
        #print(p.slice[1].value)
        #print(p.slice[1].type)
        #print(p.slice[1].lineno)
        p[0]={'type':p.slice[1].value}

    def p_reference_type(self, p):
        '''
            reference_type : class_type
                            | array_type
        '''

    def p_class_type(self, p):
        '''
            class_type : type_name
        '''

    def p_interface_type(self, p):
        '''
            interface_type : type_name
        '''

    def p_array_type(self, p):
        '''
            array_type : type LSQUARE RSQUARE
        '''

    ## block statements
    def p_block(self, p):
        '''
            block : BEGIN block_statements END
                  | BEGIN END
        '''

    def p_block_statements(self, p):
        '''
            block_statements : block_statements block_statement
                             | block_statement
        '''

    def p_block_statement(self, p):
        '''
            block_statement : local_variable_declaration STMT_TERMINATOR
                            | statement
        '''

    def p_local_variable_declaration(self, p):
        '''
            local_variable_declaration : type variable_declarators
        '''

    def p_statement(self, p):
        '''
            statement : block
                      | statement_expression STMT_TERMINATOR
                      | break_statement
                      | continue_statement
                      | return_statement
                      | if_then_else_statement
                      | while_statement
                      | for_statement
                      | print_statement
        '''

    def p_print_statement(self, p):
        '''
            print_statement : PRINT LPAREN expression RPAREN STMT_TERMINATOR
        '''

    def p_statement_expression(self, p):
        '''
            statement_expression : assignment
                                 | method_invocation
                                 | class_instance_creation_expression
        '''

    def p_if_then_else_statement(self, p):
        '''
            if_then_else_statement : IF LPAREN expression RPAREN THEN block_statements ELSE block_statements END
                                   | IF LPAREN expression RPAREN THEN block_statements END
        '''

    def p_while_statement(self, p):
        '''
            while_statement : WHILE LPAREN expression RPAREN block
        '''

    def p_for_statement(self, p):
        '''
            for_statement : FOR LPAREN for_init STMT_TERMINATOR expression STMT_TERMINATOR for_update RPAREN block
                          | FOR LPAREN for_init STMT_TERMINATOR STMT_TERMINATOR for_update RPAREN block
        '''

    def p_statement_expressions(self, p):
        '''
            statement_expressions : statement_expressions COMMA statement_expression
                                  | statement_expression
        '''

    def p_for_init(self, p):
        '''
            for_init : statement_expressions
                     | local_variable_declaration
                     | empty
        '''

    def p_for_update(self, p):
        '''
            for_update : statement_expressions
                       | empty
        '''

    def p_break_statement(self, p):
        '''
            break_statement : BREAK STMT_TERMINATOR
        '''

    def p_continue_statement(self, p):
        '''
            continue_statement : CONTINUE STMT_TERMINATOR
        '''

    def p_return_statement(self, p):
        '''
            return_statement : RETURN expression STMT_TERMINATOR
                             | RETURN STMT_TERMINATOR
        '''

    def implicitTypeConversion(self,t1,v1,t2,v2):
        #TODO if something is wrong throw error here
        if t1==t2:
            p={'type':t1,'value1':v1,'value2':v2}
            return p
        else:
            #TODO type converseion
            print(str(t1))
            print(str(t2))
            #assert(False)
            p={'type':t1,'value1':v1,'value2':v2}
            return p





    def p_expression(self, p):
        '''
            expression : expression binaryop expression
                       | unaryop expression
                       | assignment
                       | primary
                       | identifier_name_with_dot
                       | IDENTIFIER
        '''

        #TODO I think the type convsersion is wrong, please check
        print("416"+str(p.slice))
        if str(p.slice[1])=='primary':
            p[0]={'place':p[1]['value'],'type':p[1]['type'],'code':''}
        elif len(p.slice)==4:
            #TODO PRIORITY IS VIOLATED
            res = self.implicitTypeConversion(p[1]['type'],p[1]['place'],p[3]['type'],p[3]['place'])
            temp = self.stManager.newTemp(p[1]['type'])
            #temp = 'temporary_temp1'
            #TODO
            p[0]={'place':temp,'type':res['type'],'code':p[1]['code']+p[3]['code']+self.gen(p[2],temp,res['value1'],res['value2'])}
        elif len(p.slice)==3:
            #temp = 'temporary_temp2'
            if p[2]['type']=='String' or p[2]['type']=='Boolean':
                #TODO THROW ERROR
                print("error")
                assert(False)
            temp = self.stManager.newTemp(p[2]['type'])
            p[0]={'place':temp,'type':p[2]['type'],'code':p[2]['code']+self.gen(p[1],temp,p[2]['place'])}
        elif str(p.slice[1])=='assignment':
            pass
        elif str(p.slice[1])=='identifier_name_with_dot':
            pass
        else:
            #CASE FOR IDENTIFIER
            #self.symtable.printMe(self.symtable)
            #TODO Error in below and above line
            #symentry=self.symtable.lookup(p.slice[1].value,self.symtable)
            #print("symentry"+str(*symentry))

            #symentry='test_symentry'
            #TODO for above
            #TODO for below do I need to separate expression and IDENTIFIER?   yesss
            #TODO Remove below dummy values
            #temp = 'temporary_temp5'
            symentry = self.stManager.lookup(p.slice[1].value)
            temp = self.stManager.newTemp()
            print(*symentry)
            p[0]={'place':temp,'type':symentry.ltype,'code':self.gen('=',temp,'loc_test_symentry')}


        print('----------------------------------------\n'+str(p[0]['code'])+'-----------------------------------\n')


    def p_binaryop(self, p):
        '''
            binaryop : PLUS
                     | MINUS
                     | MULTIPLY
                     | DIVIDE
                     | MODULUS
                     | LSHIFT
                     | RSHIFT
                     | LT
                     | LE
                     | GT
                     | GE
                     | EQEQ
                     | NTEQ
                     | AND
                     | OR
                     | BIT_XOR
                     | BIT_OR
                     | BIT_AND
        '''
        #TODO, whether all can be converted to their single token representation. Ask manish
        p[0]=p.slice[1].value;

    def p_unaryop(self, p):
        '''
            unaryop : MINUS
                    | NOT
        '''
        p[0]=p.slice[1].value;

    def p_assignment(self, p):
        '''
            assignment : left_hand_side EQ expression
        '''

    def p_left_hand_side(self, p):
        '''
            left_hand_side : identifier_name_with_dot
                           | IDENTIFIER
                           | field_access
                           | array_access
        '''

    def p_method_invocation(self, p):
        '''
            method_invocation : identifier_name_with_dot LPAREN argument_list RPAREN
                              | IDENTIFIER LPAREN argument_list RPAREN
                              | identifier_name_with_dot LPAREN RPAREN
                              | IDENTIFIER LPAREN RPAREN
                              | field_access LPAREN argument_list RPAREN
                              | field_access LPAREN RPAREN

        '''

    def p_field_access(self, p):
        '''
            field_access : primary DOT IDENTIFIER
        '''

    def p_primary(self, p):
        '''
            primary : primary_no_new_array
                    | array_creation_expression
        '''
        print("480"+str(p.slice))
        p[0]=p[1]
        #TODO check

    def p_primary_no_new_array(self, p):
        '''
            primary_no_new_array : literal
                                 | LPAREN expression RPAREN
                                 | class_instance_creation_expression
                                 | field_access
                                 | method_invocation
                                 | array_access
        '''
        print("491"+str(p.slice))
        if str(p.slice[1])=='literal':
            p[0]=p[1]
        else:
            #TODO
            pass

    def p_class_instance_creation_expression(self, p):
        '''
            class_instance_creation_expression : NEW class_type LPAREN argument_list RPAREN
                                               | NEW class_type LPAREN RPAREN
        '''

    def p_argument_list(self, p):
        '''
            argument_list : argument_list COMMA expression
                          | expression
        '''

    def p_array_creation_expression(self, p):
        '''
            array_creation_expression : NEW primitive_type dim_exprs dims
                                      | NEW class_type dim_exprs dims
        '''

    def p_dim_exprs(self, p):
        '''
            dim_exprs : dim_exprs dim_expr
                      | empty
        '''

    def p_dim_expr(self, p):
        '''
            dim_expr : LSQUARE expression RSQUARE
        '''

    def p_dims(self, p):
        '''
            dims : LSQUARE RSQUARE dims
                 | empty
        '''

    def p_array_access(self, p):
        '''
            array_access : identifier_name_with_dot LSQUARE expression RSQUARE
                         | IDENTIFIER LSQUARE expression RSQUARE
                         | primary_no_new_array LSQUARE expression RSQUARE
        '''

    def p_type_name(self, p):
        '''
            type_name : IDENTIFIER
        '''

    def p_identifier_name_with_dot(self, p):
        '''
            identifier_name_with_dot : identifier_name_with_dot DOT IDENTIFIER
                            | IDENTIFIER DOT identifier_one_step
        '''


    def p_identifier_one_step(self,p):
        '''
            identifier_one_step : IDENTIFIER
        '''

    def p_literal(self, p):
        '''
            literal : INTEGER_LITERAL
                    | FLOAT_LITERAL
                    | BOOLEAN_LITERAL
                    | STRING_LITERAL
                    | NIL
        '''
        print("560"+str(p.slice))
        tp = str(p.slice[1].type)
        if str(tp)=='INTEGER_LITERAL':
            p[0]={'type':'int','value':p.slice[1].value}

        if str(tp)=='FLOAT_LITERAL':
            p[0]={'type':'real','value':p.slice[1].value}
            #TODO -- check whether there should be real or float in upper line

        if str(tp)=='BOOLEAN_LITERAL':
            p[0]={'type':'boolean','value':p.slice[1].value}

        if str(tp)=='STRING_LITERAL':
            p[0]={'type':'String','value':p.slice[1].value}

        if str(tp)=='NIL':
            assert(False)
            #TODO what to do of this case
            p[0]={'type':'NIL','value':p.slice[1].value}

    ## empty
    def p_empty(self, p):
        '''
            empty :
        '''
        pass


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
        print('-------------------------------------------------------\n')
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
