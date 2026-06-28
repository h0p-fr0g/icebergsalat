# =============================================================================
# --- INTERPRETER / EVALUATOR ---
# =============================================================================

from environment import Env 

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
        val = eval_expression(expr_node, env)
        
        if kind == 'assign_decl':
            env.vars[var_name] = val
        else:
            target_env = env.resolve(var_name)
            
            if target_env:
                target_env.vars[var_name] = val
            else:
                raise NameError(f"Runtime Error: Variable '{var_name}' is not defined!")
        return None

    # --- IF STATEMENT ---
    if kind == 'if_stmt':
        cond = eval_expression(node[1], env)
        if cond:
            for stmt in node[2]:
                eval_statement(stmt, env)
        return None
    
    # --- IF-ELSE STATEMENT ---
    if kind == 'if_else_stmt':
        cond_val = eval_expression(node[1], env)
        
        if cond_val:
            for stmt in node[2]:
                eval_statement(stmt, env)
        else:
            for stmt in node[3]:
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

    # --- FUNCTION DEFINITION (CLOSURE) ---
    if kind == 'function_def':
        func_name, _, params, body = node[1], node[2], node[3], node[4]
        param_names = [p_name for p_name, _ in params]
        
        env.vars[func_name] = (param_names, body, env)
        return None

    # --- RETURN STATEMENT ---
    if kind == 'return':
        if len(node) > 1 and node[1] is not None:
            val = eval_expression(node[1], env)
        else:
            val = None
            
        raise ReturnException(val)

    # --- FALLBACK ---
    eval_expression(node, env)
    return None


def eval_expression(node, env):
    kind = node[0]

    # --- LITERALS ---
    if kind == 'num':    return node[1]
    if kind == 'bool':   return node[1]

    # --- VARIABLES (AND FUNCTIONS) ---
    if kind == 'id':
        var_name = node[1]
        val = env.lookup(var_name)
        if val is not None:
            return val
        raise NameError(f"Runtime Error: Variable '{var_name}' is not defined!")

    # --- LAMBDA EXPRESSION (NEU) ---
    if kind == 'lambda':
        params, _, body = node[1], node[2], node[3]
        param_names = [p_name for p_name, _ in params]
        
        return (param_names, body, env)

    # --- NEGATION ---
    if kind == 'NEGATE':
        return -eval_expression(node[1], env)

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

        if op == 'AND':
            if not eval_expression(left, env): 
                return False
            return eval_expression(right, env)
                
        if op == 'OR':
            if eval_expression(left, env): 
                return True
            return eval_expression(right, env)

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

    # --- FUNCTION CALL ---
    if kind == 'function_call':
        target_node, args = node[1], node[2]
        
        if isinstance(target_node, str):
            func_obj = env.lookup(target_node)
            if not func_obj:
                raise NameError(f"Runtime Error: '{target_node}' is not defined!")
        else:
            func_obj = eval_expression(target_node, env)
            
        if not isinstance(func_obj, tuple) or len(func_obj) != 3:
            raise TypeError("Runtime Error: Target is not a callable function!")
            
        param_names, body, closure_env = func_obj
        
        evaluated_args = [eval_expression(arg, env) for arg in args]
        
        local_env = Env(parent=closure_env)
        
        for p_name, p_val in zip(param_names, evaluated_args):
            local_env.vars[p_name] = p_val
            
        try:
            for stmt in body:
                eval_statement(stmt, local_env)
        except ReturnException as e:
            return e.value
            
        return None

    raise ValueError(f"Runtime Error: Invalid Expression Node {kind}")


def eval_ast(node, env=None):
    if env is None:
        env = Env()
    return eval_statement(node, env)