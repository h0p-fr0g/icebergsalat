def check_type(node, env=None):
    if env is None:
        env = {}
    
    kind = node[0]

    if kind == 'num':    return 'NUM'
    if kind == 'bool':   return 'BOOL'
    
    if kind == 'id':
        var_name = node[1]
        if var_name in env:
            return env[var_name]
        raise TypeError(f"Variable '{var_name}' is not declared!")
    
    if kind == 'assign_decl':
        var_name, var_type_str, expr_node = node[1], node[2], node[3]
        type_expr = check_type(expr_node, env)
        expected_type = 'NUM' if var_type_str == 'int' else 'BOOL'
        
        if type_expr != expected_type:
            raise TypeError(f"Typeconflict at declaration of '{var_name}': Expected {expected_type}, received {type_expr}")
        
        env[var_name] = expected_type
        return 'VOID'

    if kind == 'assign':
        var_name, expr_node = node[1], node[2]
        if var_name not in env:
            raise TypeError(f"Variable '{var_name}' needs to be declared before assignment")
        
        type_expr = check_type(expr_node, env)
        if type_expr != env[var_name]:
            raise TypeError(f"Typeconflict at assignment of '{var_name}': Can't save {type_expr} into {env[var_name]}")
        return 'VOID'

    if kind == 'binop':
        op, left, right = node[1], node[2], node[3]
        type_left = check_type(left, env)
        type_right = check_type(right, env)

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

    elif kind == 'not':
        type_expr = check_type(node[1], env)
        if type_expr == 'BOOL':
            return 'BOOL'
        raise TypeError(f"'!' expected BOOL, received {type_expr}")

    elif kind == 'if':
        type_cond = check_type(node[1], env)
        type_then = check_type(node[2], env)
        type_else = check_type(node[3], env)
        if type_cond != 'BOOL':
            raise TypeError(f"Condition '?' expects BOOL, received {type_cond}")
        if type_then != type_else:
            raise TypeError(f"Branches of '?' incompatible: {type_then} vs {type_else}")
        return type_then
    
    elif kind == 'if_stmt' or kind == 'while_stmt':
        cond_node, stmt_list = node[1], node[2]
        type_cond = check_type(cond_node, env)
        if type_cond != 'BOOL':
            raise TypeError(f"Condition for IF/WHILE expects BOOL, received {type_cond}")
        
        for stmt in stmt_list:
            check_type(stmt, env)
        return 'VOID'

    elif kind in ['break', 'continue']:
        return 'VOID'

    raise ValueError(f"Unknown Node: {kind}")