import ply.yacc as yacc
import itertools
import sys
from lexer import tokens

start = 'program'
module = sys.modules[__name__]

def p_program(p):
    '''program : optional_newlines statement_list optional_newlines
               | optional_newlines'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_statement_list_multiple(p):
    '''statement_list : statement_list statement_terminator statement
                      | statement_list statement'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement_list_single(p):
    'statement_list : statement'
    p[0] = [p[1]]

def p_statement_exp(p):
    'statement : expression'
    p[0] = p[1]

def p_statement_assign(p):
    'statement : expression ID TYPE ASSIGN'
    p[0] = ('assign_decl', p[2], p[3], p[1])

def p_statement_reassign(p):
    'statement : expression ID ASSIGN'
    p[0] = ('assign', p[2], p[1])

def p_statement_if(p):
    'statement : expression IF LINEBREAK INDENT statement_list DEDENT'
    p[0] = ('if_stmt', p[1], p[5])

def p_statement_while(p):
    'statement : expression WHILE LINEBREAK INDENT statement_list DEDENT'
    p[0] = ('while_stmt', p[1], p[5])

def p_statement_break(p):
    'statement : BREAK'
    p[0] = ('break',)

def p_statement_continue(p):
    'statement : CONTINUE'
    p[0] = ('continue',)

def p_statement_terminator(p):
    'statement_terminator : LINEBREAK'
    p[0] = None

def p_optional_newlines(p):
    '''optional_newlines : LINEBREAK
                         | empty'''
    p[0] = None

def p_empty(p):
    'empty :'
    p[0] = None

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ('num', p[1])

def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = ('bool', p[1])

def p_expression_id(p):
    'expression : ID'
    p[0] = ('id', p[1])

def binop(op):
    production = f'expression : expression expression {op}'
    def f(p):
        p[0] = ('binop', op, p[1], p[2])
    f.__doc__ = production
    setattr(module, next(binop.unique_production), f)

binop.unique_production = (f"p_binop{i}" for i in itertools.count())

for op in [
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'MODULO', 'POWER',
    'LE', 'GE', 'LT', 'GT', 'EQ', 'NE',
    'AND', 'OR'
]:
    binop(op)

def p_expression_not(p):
    'expression : expression NOT'
    p[0] = ('not', p[1])

def p_expression_shorthand(p):
    'expression : expression expression expression SH'
    p[0] = ('if', p[1], p[2], p[3])

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}' (line {p.lineno})")    
    else:
        raise SyntaxError(f"Syntax error at EOF")

parser = yacc.yacc()