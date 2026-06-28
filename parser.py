import ply.yacc as yacc
import itertools
import sys
from lexer import tokens

start = 'program'
module = sys.modules[__name__]


def p_program(p):
    '''program : separator_list statement_list separator_list
               | statement_list
               | separator_list
               | empty'''
    if len(p) == 4:
        p[0] = p[2]
    elif len(p) == 2 and p[1] is not None:
        p[0] = p[1]
    else:
        p[0] = []

def p_statement_list_multiple(p):
    'statement_list : statement_list separator_list statement'
    if p[3] is not None:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = p[1]

def p_statement_list_single(p):
    'statement_list : statement'
    if p[1] is None:
        p[0] = []
    else:
        p[0] = [p[1]]

def p_separator_list_multiple(p):
    'separator_list : separator_list LINEBREAK'
    p[0] = None

def p_separator_list_single(p):
    'separator_list : LINEBREAK'
    p[0] = None


def p_statement_exp(p):
    'statement : expression'
    p[0] = p[1]

def p_statement_assign(p):
    'statement : expression ID type ASSIGN'
    p[0] = ('assign_decl', p[2], p[3], p[1])

def p_statement_reassign(p):
    'statement : expression ID ASSIGN'
    p[0] = ('assign', p[2], p[1])

def p_statement_if(p):
    '''statement : expression IF separator_list INDENT statement_list DEDENT
                 | expression IF separator_list INDENT statement_list DEDENT separator_list ELSE separator_list INDENT statement_list DEDENT'''
    if len(p) == 7:
        p[0] = ('if_stmt', p[1], p[5])
    else:
        p[0] = ('if_else_stmt', p[1], p[5], p[11])

def p_statement_while(p):
    'statement : expression WHILE separator_list INDENT statement_list DEDENT'
    p[0] = ('while_stmt', p[1], p[5])

def p_statement_break(p):
    'statement : BREAK'
    p[0] = ('break',)

def p_statement_continue(p):
    'statement : CONTINUE'
    p[0] = ('continue',)

def p_function_definition(p):
    '''statement : LPAREN parameterlist RPAREN ID type FUNCTION separator_list INDENT statement_list DEDENT
                 | LPAREN RPAREN ID type FUNCTION separator_list INDENT statement_list DEDENT'''
    if len(p) == 11:
        p[0] = ('function_def', p[4], p[5], p[2], p[9])
    else:
        p[0] = ('function_def', p[3], p[4], [], p[8])

def p_return_statement(p):
    'statement : expression RETURN'
    p[0] = ('return', p[1])

def p_empty(p):
    'empty :'
    p[0] = None

def p_expression_negate(p):
    'expression : expression TILDE'
    p[0] = ('NEGATE', p[1])

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ('num', p[1])

def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = ('bool', p[1])

def p_expression_id(p):
    'expression : ID'
    p[0] = ('id', p[1])


def p_function_call_expr(p):
    '''function_call : LPAREN expressionlist RPAREN ID
                     | LPAREN RPAREN ID
                     | LPAREN expressionlist RPAREN function_call
                     | LPAREN RPAREN function_call'''
    if len(p) == 5:
        p[0] = ('function_call', p[4], p[2])
    else:
        p[0] = ('function_call', p[3], [])

def p_expression_function_call(p):
    'expression : function_call'
    p[0] = p[1]


def binop(op):
    production = f'expression : expression expression {op}'
    def f(p):
        p[0] = ('binop', op, p[1], p[2])
    f.__doc__ = production
    setattr(module, next(binop.unique_production), f)

binop.unique_production = (f"p_binop{i}" for i in itertools.count())

for op in [
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'POWER',
    'LE', 'GE', 'LT', 'GT', 'EQ', 'NE', 'AND', 'OR'
]:
    binop(op)

def p_expression_not(p):
    'expression : expression NOT'
    p[0] = ('not', p[1])

def p_expression_shorthand(p):
    'expression : expression expression expression SH'
    p[0] = ('if', p[1], p[2], p[3])


def p_expressionlist(p):
    '''expressionlist : expression COMMA expressionlist
                      | expression'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_parameterlist(p):
    '''parameterlist : ID type COMMA parameterlist
                     | ID type'''
    if len(p) == 5:
        p[0] = [(p[1], p[2])] + p[4]
    else:
        p[0] = [(p[1], p[2])]


def p_type_simple(p):
    'type : TYPE'
    p[0] = p[1]

def p_type_function(p):
    'type : BACKSLASH typelist COLON type'
    p[0] = ('func_type', p[2], p[4])

def p_typelist(p):
    '''typelist : type typelist
                | type'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_expression_lambda(p):
    'expression : LPAREN parameterlist RPAREN type LEAF separator_list INDENT statement_list DEDENT'
    p[0] = ('lambda', p[2], p[4], p[8])


def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}' (line {p.lineno})")    
    else:
        raise SyntaxError(f"Syntax error EOF")

parser = yacc.yacc(debug=False, write_tables=False)