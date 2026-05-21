import ply.lex as lex

tokens = (
    'ID', 'NUMBER', 'BOOLEAN',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'MODULO', 'POWER', 'SH',
    'LE', 'GE', 'LT', 'GT', 'EQ', 'NE',
    'AND', 'OR', 'NOT',
    'ASSIGN',
    'IF', 'ELSE', 'WHILE', 'BREAK', 'CONTINUE',
    'TYPE', 
    'LINEBREAK', 'INDENT', 'DEDENT' 
)

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MODULO  = r'%'
t_POWER   = r'\^'
t_SH      = r'\?'
t_LE      = r'<='
t_GE      = r'>='
t_LT      = r'<'
t_GT      = r'>'
t_EQ      = r'=='
t_NE      = r'!='
t_AND     = r'&'
t_OR      = r'\|'
t_NOT     = r'!'
t_ASSIGN  = r'=:'

keywords = {
    'int': 'TYPE',
    'IF': 'IF',
    'ELSE': 'ELSE',
    'WHILE': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE'
}

def t_NUMBER(t):
    r'\d+~?'
    if t.value.endswith('~'):
        t.value = -int(t.value[:-1])
    else:
        t.value = int(t.value)
    return t

def t_BOOLEAN(t):
    r'[TF]'
    t.value = True if t.value == 'T' else False
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'ID')
    return t

def t_LINEBREAK(t):
    r'\n+[ \t]*'
    t.lexer.lineno += t.value.count('\n')
    last_newline_idx = t.value.rfind('\n')
    spaces = t.value[last_newline_idx + 1:]
    indent = spaces.count('\t')
    current = t.lexer.indent_stack[-1]

    if indent > current:
        t.lexer.indent_stack.append(indent)
        tok = lex.LexToken()
        tok.type = 'INDENT'
        tok.value = indent
        tok.lineno = t.lineno
        tok.lexpos = t.lexpos
        t.lexer.pending_tokens.append(tok)
    elif indent < current:
        while t.lexer.indent_stack[-1] > indent:
            t.lexer.indent_stack.pop()
            tok = lex.LexToken()
            tok.type = 'DEDENT'
            tok.value = ''
            tok.lineno = t.lineno
            tok.lexpos = t.lexpos
            t.lexer.pending_tokens.append(tok)

    t.type = 'LINEBREAK'
    return t

t_ignore  = ' '

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def get_next_token(lexer_obj):
    if lexer_obj.pending_tokens:
        return lexer_obj.pending_tokens.pop(0)
        
    tok = lexer_obj.original_token()

    if not tok and len(lexer_obj.indent_stack) > 1:
        while len(lexer_obj.indent_stack) > 1:
            lexer_obj.indent_stack.pop()
            ded_tok = lex.LexToken()
            ded_tok.type = 'DEDENT'
            ded_tok.value = ''
            ded_tok.lineno = lexer_obj.lineno
            ded_tok.lexpos = lexer_obj.lexpos
            lexer_obj.pending_tokens.append(ded_tok)
        return lexer_obj.pending_tokens.pop(0)

    return tok

def build_lexer():
    lexer_obj = lex.lex()
    lexer_obj.indent_stack = [0]
    lexer_obj.pending_tokens = []
    lexer_obj.original_token = lexer_obj.token
    lexer_obj.token = lambda: get_next_token(lexer_obj)
    return lexer_obj