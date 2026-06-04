# =============================================================================
# --- INTERPRETER / EVALUATOR ---
# =============================================================================

class BreakException(Exception): pass
class ContinueException(Exception): pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


def eval_statement(node, env):
    kind = node[0]

    # --- DECLARATION AND ASSIGNMENT ---
    if kind == 'assign_decl' or kind == 'assign':
        var_name = node[1]
        expr_node = node[-1]
        env['vars'][var_name] = eval_expression(expr_node, env)
        return None

    # --- IF STATEMENT ---
    if kind == 'if_stmt':
        cond = eval_expression(node[1], env)
        if cond:
            for stmt in node[2]:
                eval_statement(stmt, env)
        return None

    # --- WHILE STATEMENT ---
    if kind == 'while_stmt':
        while eval_expression(node[1], env):
            try:
                for stmt in node[2]:
                    eval_statement(stmt, env)
            except BreakException:
                break
            except ContinueException:
                continue
        return None

    # --- LOOP CONTROLS ---
    if kind == 'break':
        raise BreakException()
    if kind == 'continue':
        raise ContinueException()

    # --- FUNCTION DEFINITION ---
    if kind == 'function_def':
        func_name, ret_type, params, body = node[1], node[2], node[3], node[4]
        param_names = [p_name for p_name, _ in params]
        env['funcs'][func_name] = (param_names, body)
        return None

    # --- RETURN STATEMENT ---
    if kind == 'return':
        val = eval_expression(node[1], env)
        raise ReturnException(val)

    eval_expression(node, env)
    return None


def eval_expression(node, env):
    kind = node[0]

    # --- LITERALS ---
    if kind == 'num':    return node[1]
    if kind == 'bool':   return node[1]

    # --- VARIABLES ---
    if kind == 'id':
        return env['vars'][node[1]]

    # --- UNARY OPERATOR ---
    if kind == 'not':
        return not eval_expression(node[1], env)

    # --- SHORTHAND IF (TERNARY EXPRESSION) ---
    if kind == 'if':
        cond = eval_expression(node[1], env)
        return eval_expression(node[2], env) if cond else eval_expression(node[3], env)

    # --- BINARY OPERATORS ---
    if kind == 'binop':
        op, left, right = node[1], node[2], node[3]
        v_left = eval_expression(left, env)
        v_right = eval_expression(right, env)

        if op == 'PLUS':    return v_left + v_right
        if op == 'MINUS':   return v_left - v_right
        if op == 'TIMES':   return v_left * v_right
        if op == 'DIVIDE':  return v_left // v_right
        if op == 'MODULO':  return v_left % v_right
        if op == 'POWER':   return v_left ** v_right
        
        if op == 'LT':      return v_left < v_right
        if op == 'LE':      return v_left <= v_right
        if op == 'GT':      return v_left > v_right
        if op == 'GE':      return v_left >= v_right
        if op == 'EQ':      return v_left == v_right
        if op == 'NE':      return v_left != v_right
        
        if op == 'AND':     return v_left and v_right
        if op == 'OR':      return v_left or v_right

    # --- FUNCTION CALL ---
    if kind == 'function_call':
        func_name, args = node[1], node[2]
        
        param_names, body = env['funcs'][func_name]
        
        evaluated_args = [eval_expression(arg, env) for arg in args]
        
        local_env = {
            'vars': {},          
            'funcs': env['funcs'] 
        }
        
        for p_name, p_val in zip(param_names, evaluated_args):
            local_env['vars'][p_name] = p_val
            
        try:
            for stmt in body:
                eval_statement(stmt, local_env)
        except ReturnException as e:
            return e.value
            
        return None

    raise ValueError(f"Runtime Error: Invalid Expression Node {kind}")


def eval_ast(node, env=None):
    if env is None:
        env = {
            'vars': {},
            'funcs': {}
        }
    return eval_statement(node, env)