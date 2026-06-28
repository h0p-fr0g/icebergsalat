# =============================================================================
# --- TYPE CHECKER ---
# =============================================================================

from environment import Env

def types_match(type1, type2):
    if isinstance(type1, str) and isinstance(type2, str):
        return type1 == type2
        
    if isinstance(type1, tuple) and isinstance(type2, tuple):
        if type1[0] == 'func_type' and type2[0] == 'func_type':
            params1, ret1 = type1[1], type1[2]
            params2, ret2 = type2[1], type2[2]
            
            if len(params1) != len(params2):
                return False
            for p1, p2 in zip(params1, params2):
                if not types_match(p1, p2):
                    return False
            return types_match(ret1, ret2)
    return False

def parse_type_node(type_node):
    if type_node == 'int': return 'NUM'
    if type_node == 'bool': return 'BOOL'
    if type_node == 'void': return 'VOID'
    
    if isinstance(type_node, tuple) and type_node[0] == 'func_type':
        params = [parse_type_node(p) for p in type_node[1]]
        ret = parse_type_node(type_node[2])
        return ('func_type', params, ret)
        
    return type_node # Fallback


def check_statement(node, env): 
    kind = node[0]

    # --- DECLARATION ---
    if kind == 'assign_decl':
        var_name, type_node, expr_node = node[1], node[2], node[3]
        actual_type = check_expression(expr_node, env)
        expected_type = parse_type_node(type_node)
        
        if not types_match(actual_type, expected_type):
            raise TypeError(f"Typeconflict at declaration of '{var_name}': Expected {expected_type}, received {actual_type}")
        
        env.vars[var_name] = expected_type
        return 'VOID'

    # --- ASSIGNMENT ---
    if kind == 'assign':
        var_name, expr_node = node[1], node[2]
        existing_type = env.lookup(var_name)
        if not existing_type:
            raise TypeError(f"Variable '{var_name}' needs to be declared before assignment")
        
        actual_type = check_expression(expr_node, env)
        if not types_match(actual_type, existing_type):
            raise TypeError(f"Typeconflict at assignment of '{var_name}': Can't save {actual_type} into {existing_type}")
        return 'VOID'

    # --- FUNCTION DEFINITION ---
    if kind == 'function_def':
        func_name, type_node, params, body = node[1], node[2], node[3], node[4]

        expected_ret_type = parse_type_node(type_node)
        param_types = [parse_type_node(p[1]) for p in params]

        env.vars[func_name] = ('func_type', param_types, expected_ret_type)

        local_env = Env(parent=env) 
        local_env.current_return = expected_ret_type

        for (p_name, _), p_type in zip(params, param_types):
            local_env.vars[p_name] = p_type

        for stmt in body:
            check_statement(stmt, local_env)

        if expected_ret_type != 'VOID':
            if not has_guaranteed_return(body):
                raise TypeError(f"Function '{func_name}' expects to return {expected_ret_type} but not all execution paths end with a RETURN statement.")
                
        return 'VOID'

    # --- RETURN STATEMENT ---
    if kind == 'return':
        expr_node = node[1]
        type_expr = check_expression(expr_node, env)
        
        if env.current_return is None:
            raise TypeError("RETURN is only allowed inside a function or lambda!")
        
        if env.current_return == 'VOID':
            raise TypeError("Can't return a value from a VOID function!")
            
        if not types_match(type_expr, env.current_return):
            raise TypeError(f"Return type conflict: Expected {env.current_return}, received {type_expr}")
            
        return 'VOID'

    if kind in ['if_stmt', 'while_stmt']:
        cond_node, stmt_list = node[1], node[2]
        type_cond = check_expression(cond_node, env)
        if type_cond != 'BOOL':
            raise TypeError(f"Condition for IF/WHILE expects BOOL, received {type_cond}")
        
        for stmt in stmt_list:
            check_statement(stmt, env)
        return 'VOID'

    # --- IF-ELSE STATEMENT ---
    if kind == 'if_else_stmt':
        cond_type = check_expression(node[1], env)
        
        if cond_type != 'BOOL':
            raise TypeError(f"Condition of 'if-else' expects BOOL, received {cond_type}")
        
        for stmt in node[2]:
            check_statement(stmt, env)
            
        for stmt in node[3]:
            check_statement(stmt, env)
        
        return 'VOID'

    if kind in ['break', 'continue']:
        return 'VOID'
    
    check_expression(node, env)
    return 'VOID'


def check_expression(node, env):
    kind = node[0]

    # --- LITERALS ---
    if kind == 'num':    return 'NUM'
    if kind == 'bool':   return 'BOOL'
    
    # --- VARIABLES ---
    if kind == 'id':
        var_name = node[1]
        var_type = env.lookup(var_name)
        if var_type:
            return var_type
        raise TypeError(f"Variable '{var_name}' is not declared in this scope!")
    
    # --- NEGATION ---
    if kind == 'NEGATE':
        type_expr = check_expression(node[1], env)
        if type_expr != 'NUM':
            raise TypeError(f"Negation '~' expects NUM, received {type_expr}")
        return 'NUM'

    # --- LAMBDA EXPRESSION (NEU) ---
    if kind == 'lambda':
        params, type_node, body = node[1], node[2], node[3]
        
        expected_ret_type = parse_type_node(type_node)
        param_types = [parse_type_node(p[1]) for p in params]
        
        local_env = Env(parent=env)
        local_env.current_return = expected_ret_type
        
        for (p_name, _), p_type in zip(params, param_types):
            local_env.vars[p_name] = p_type
            
        for stmt in body:
            check_statement(stmt, local_env)
            
        if expected_ret_type != 'VOID' and not has_guaranteed_return(body):
            raise TypeError("Lambda expects to return a value, but not all execution paths end with a RETURN statement.")
            
        return ('func_type', param_types, expected_ret_type)

    # --- FUNCTION CALL ---
    if kind == 'function_call':
        target_node, args = node[1], node[2]
        
        if isinstance(target_node, str):
            target_type = env.lookup(target_node)
            if not target_type:
                raise TypeError(f"'{target_node}' is not defined!")
        else:
            target_type = check_expression(target_node, env)
            
        if not isinstance(target_type, tuple) or target_type[0] != 'func_type':
            raise TypeError(f"Target is not a function! Cannot call type {target_type}")
            
        _, expected_param_types, return_type = target_type
        
        if len(args) != len(expected_param_types):
            raise TypeError(f"Expected {len(expected_param_types)} arguments, received {len(args)}")
            
        for i, arg_node in enumerate(args):
            arg_type = check_expression(arg_node, env)
            if not types_match(arg_type, expected_param_types[i]):
                raise TypeError(f"Argument {i+1}: Expected {expected_param_types[i]}, received {arg_type}")
                
        return return_type

    # --- BINARY OPERATORS ---
    if kind == 'binop':
        op, left, right = node[1], node[2], node[3]
        type_left = check_expression(left, env)
        type_right = check_expression(right, env)

        if op in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'POWER']:
            if type_left == 'NUM' and type_right == 'NUM':
                return 'NUM'
            raise TypeError(f"'{op}' expected NUM NUM, received {type_left} {type_right}")

        if op in ['LT', 'LE', 'GT', 'GE', 'EQ', 'NE']:
            if type_left == 'NUM' and type_right == 'NUM':
                return 'BOOL'
            raise TypeError(f"Compare '{op}' expected NUM NUM, received {type_left} {type_right}")

        if op in ['AND', 'OR']:
            if type_left == 'BOOL' and type_right == 'BOOL':
                return 'BOOL'
            raise TypeError(f"Logic '{op}' expected BOOL BOOL, received {type_left} {type_right}")

    # --- UNARY OPERATOR ---
    if kind == 'not':
        type_expr = check_expression(node[1], env)
        if type_expr == 'BOOL':
            return 'BOOL'
        raise TypeError(f"'!' expected BOOL, received {type_expr}")

    # --- SHORTHAND IF (TERNARY EXPRESSION) ---
    if kind == 'if':
        type_cond = check_expression(node[1], env)
        type_then = check_expression(node[2], env)
        type_else = check_expression(node[3], env)
        if type_cond != 'BOOL':
            raise TypeError(f"Condition '?' expects BOOL, received {type_cond}")
        if not types_match(type_then, type_else):
            raise TypeError(f"Branches of '?' incompatible: {type_then} vs {type_else}")
        return type_then

    raise ValueError(f"Invalid Expression Node: {kind}")


def check_type(node, env=None):
    if env is None:
        env = Env()
    return check_statement(node, env)


def has_guaranteed_return(stmts):
    if not isinstance(stmts, list):
        stmts = [stmts]
        
    for stmt in stmts:
        if stmt is None: 
            continue
            
        kind = stmt[0]
        
        if kind == 'return':
            return True
            
        if kind == 'if_else_stmt':
            then_block = stmt[2]
            else_block = stmt[3]
            if has_guaranteed_return(then_block) and has_guaranteed_return(else_block):
                return True
                
    return False