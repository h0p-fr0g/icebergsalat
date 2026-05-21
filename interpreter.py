class BreakException(Exception): pass
class ContinueException(Exception): pass

def eval_ast(node, env=None):
    if env is None:
        env = {}

    kind = node[0]

    if kind == 'num':    return node[1]
    if kind == 'bool':   return node[1]
    if kind == 'id':     return env[node[1]]

    if kind == 'assign_decl' or kind == 'assign':
        var_name = node[1]
        expr_node = node[-1]
        env[var_name] = eval_ast(expr_node, env)
        return None

    if kind == 'not':
        return not eval_ast(node[1], env)

    if kind == 'if':
        cond = eval_ast(node[1], env)
        return eval_ast(node[2], env) if cond else eval_ast(node[3], env)

    if kind == 'binop':
        op, left, right = node[1], node[2], node[3]
        v_left = eval_ast(left, env)
        v_right = eval_ast(right, env)

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

    if kind == 'if_stmt':
        cond = eval_ast(node[1], env)
        if cond:
            for stmt in node[2]:
                eval_ast(stmt, env)
        return None

    if kind == 'while_stmt':
        while eval_ast(node[1], env):
            try:
                for stmt in node[2]:
                    eval_ast(stmt, env)
            except BreakException:
                break
            except ContinueException:
                continue
        return None

    if kind == 'break':
        raise BreakException()
    if kind == 'continue':
        raise ContinueException()

    raise ValueError(f"Runtime Error: Unknown Node {kind}")