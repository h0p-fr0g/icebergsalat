# =============================================================================
# --- MAIN TEST SUITE ---
# =============================================================================

from lexer import build_lexer
from parser import parser
from type_checker import check_type
from interpreter import eval_ast
from environment import Env  


def run_compiler_pipeline(test_name, source_code):
    print(f"\n==================================================================")
    print(f"RUNNING: {test_name}")
    print(f"==================================================================")
    print(f"Source Code:\n{source_code.strip()}\n")
    
    test_lexer = build_lexer()
    test_lexer.input(source_code.strip())
    
    try:

        ast = parser.parse(lexer=test_lexer)
        print("-> 1. Parser: Success! AST successfully generated.")
        

        type_env = Env() 
        for statement in ast:
            check_type(statement, type_env)
        print("-> 2. Type Checker: Success! All types are valid.")
        
        runtime_env = Env() 
        for statement in ast:
            eval_ast(statement, runtime_env)
        print("-> 3. Interpreter: Success! Code executed flawlessly.")
        
        print(f"\nFinal State of Global Variables: {runtime_env.vars}")
        
        return runtime_env

    except SyntaxError as e:
        print(f"❌ PARSING ERROR (Expected if negative test): {e}")
    except TypeError as e:
        print(f"❌ TYPE ERROR (Expected if negative test): {e}")
    except Exception as e:
        print(f"❌ RUNTIME ERROR: {e}")

    return None

if __name__ == "__main__":

# --- TEST 1: POSITIV - Basic Math Operations (Add, Subtract, Mult, Divide) ---
    code_basic_math = '''
        12 a int =:
        4 b int =:

        a b + res_add int =:
        a b - res_sub int =:
        a b * res_mult int =:
        a b / res_div int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 1: Basic Math Operations Table (+, -, *, /)", code_basic_math)
    
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['res_add'] == 16, f"Expected 16, got {runtime_env.vars['res_add']}"
        assert runtime_env.vars['res_sub'] == 8, f"Expected 8, got {runtime_env.vars['res_sub']}"
        assert runtime_env.vars['res_mult'] == 48, f"Expected 48, got {runtime_env.vars['res_mult']}"
        assert runtime_env.vars['res_div'] == 3, f"Expected 3, got {runtime_env.vars['res_div']}"
        print("-> 4. Math Verification: Success! All calculations match perfectly.")


    # --- TEST 2: NEGATIV - Type Error (Adding INT and BOOL) ---
    code_neg_math_type = '''
        10 a int =:
        T b bool =:

        a b + illegal_res int =:
    '''
    run_compiler_pipeline("Negative Case 1: Invalid Operand Types for Addition (INT + BOOL)", code_neg_math_type)


    # --- TEST 3: NEGATIV - Postfix Syntax Error (Missing Second Operand) ---
    code_neg_missing_operand = '''
        5 - broken_res int =:
    '''
    run_compiler_pipeline("Negative Case 2: Missing Operand for Binary Minus Operator", code_neg_missing_operand)


    # --- TEST 4: NEGATIV - Postfix Syntax Error (Too Many Operands) ---
    code_neg_too_many_operands = '''
        10 5 2 + extra_res int =:
    '''
    run_compiler_pipeline("Negative Case 3: Too Many Operands on the Postfix Stack", code_neg_too_many_operands)


    # --- TEST 5: NEGATIV - Runtime Division by Zero Error ---
    code_neg_div_by_zero = '''
        12 0 / zero_div_res int =:
    '''
    run_compiler_pipeline("Negative Case 4: Division by Zero Runtime Exception", code_neg_div_by_zero)


    # --- TEST 6: POSITIV - Trailing Tilde Negation and Negative Math ---
    code_negation_math = '''
        5~ a int =:
        3~ b int =:

        a b * res_mult_neg int =:
        10~ 4 + res_add_neg int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 4: Trailing Tilde (~) and Negative Arithmetic", code_negation_math)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['res_mult_neg'] == 15, f"Expected 15, got {runtime_env.vars['res_mult_neg']}"
        assert runtime_env.vars['res_add_neg'] == -6, f"Expected -6, got {runtime_env.vars['res_add_neg']}"
        print("-> 4. Math Verification: Success! Negative math is correct.")


    # --- TEST 7: POSITIV - Complex Postfix Order (Emulating Parentheses) ---
    code_postfix_order = '''
        3 5 + 10 4 - * res_postfix int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 5: Nested Postfix Structure", code_postfix_order)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['res_postfix'] == 48, f"Expected 48, got {runtime_env.vars['res_postfix']}"
        print("-> 4. Math Verification: Success! Sequential stack execution is correct.")


    # --- TEST 8: NEGATIV - Classic Infix Syntax Error ---
    code_neg_infix = '''
        10 a int =:
        5 b int =:

        a + b illegal_res int =:
    '''
    run_compiler_pipeline("Negative Case 5: Accidental Infix Usage (a + b) Error", code_neg_infix)


    # --- TEST 9: POSITIV - Unary Variable Negation with Tilde (~) ---
    code_var_negation = '''
        5 a int =:
        a~ b int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 6: Variable Negation with Tilde", code_var_negation)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['b'] == -5, f"Expected -5, got {runtime_env.vars['b']}"
        print("-> 4. Math Verification: Success! Tilde negation on variables works perfectly.")

    # --- TEST 10: NEGATIV - Type Error (Unary Negation on Boolean) ---
    code_neg_bool_negation = '''
        T a bool =:
        a~ broken_neg bool =:
    '''
    run_compiler_pipeline("Negative Case 12: Invalid Operand Type for Unary Negation (BOOL~)", code_neg_bool_negation)

    # --- TEST 11: POSITIV - Basic Comparison Operations (<, >, ==, !=, <=, >=) ---
    code_basic_comparisons = '''
        15 a int =:
        20 b int =:
        15 c int =:

        a b < res_lt bool =:
        a b > res_gt bool =:
        a c == res_eq bool =:
        a b != res_ne bool =:
        a c <= res_le bool =:
        a b >= res_ge bool =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 7: Basic Comparison Table (<, >, ==, !=, <=, >=)", code_basic_comparisons)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['res_lt'] is True
        assert runtime_env.vars['res_gt'] is False
        assert runtime_env.vars['res_eq'] is True
        assert runtime_env.vars['res_ne'] is True
        assert runtime_env.vars['res_le'] is True
        assert runtime_env.vars['res_ge'] is False
        print("-> 4. Comparison Verification: Success! All comparison results match perfectly.")


    # --- TEST 12: POSITIV - Complex Postfix Expression Combining Math and Comparisons ---
    code_math_comparison_mix = '''
        10 5 + 20 2 - > complex_comp bool =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 8: Combined Math and Comparison Postfix Expression", code_math_comparison_mix)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['complex_comp'] is False
        print("-> 4. Comparison Verification: Success! Mixed expression evaluated correctly.")


    # --- TEST 13: NEGATIV - Type Error (Comparing INT with BOOL) ---
    code_neg_comp_type = '''
        10 a int =:
        T b bool =:

        a b == illegal_comp bool =:
    '''
    run_compiler_pipeline("Negative Case 7: Invalid Operand Types for Comparison (INT == BOOL)", code_neg_comp_type)


    # --- TEST 14: NEGATIV - Assignment Type Mismatch (Saving BOOL Result into INT) ---
    code_neg_comp_assignment = '''
        5 a int =:
        3 b int =:

        a b < broken_target int =:
    '''
    run_compiler_pipeline("Negative Case 8: Saving Boolean Comparison Result into Integer Variable", code_neg_comp_assignment)


    # --- TEST 15: NEGATIV - Postfix Syntax Error (Chained Comparisons Without Connectors) ---
    code_neg_chained_comp = '''
        5 a int =:
        10 b int =:
        12 c int =:

        a b < c < illegal_chained bool =:
    '''
    run_compiler_pipeline("Negative Case 9: Illegal Chained Postfix Comparison Without Logical AND", code_neg_chained_comp)


    # --- TEST 16: POSITIV - Extended Math Operations (Modulo & Power) ---
    code_extended_math = '''
        17 5 % res_mod int =:
        2 4 ^ res_pow int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 9: Extended Math Operators (% and ^)", code_extended_math)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['res_mod'] == 2
        assert runtime_env.vars['res_pow'] == 16
        print("-> 4. Math Verification: Success! Modulo and Power calculated correctly.")


    # --- TEST 17: POSITIV - Boolean Operations and Truth Values (AND, OR, NOT) ---
    code_boolean_logic = '''
        T F & res_and bool =:
        T F | res_or bool =:
        T ! res_not bool =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 10: Boolean Logic and Log Values (&, |, !)", code_boolean_logic)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['res_and'] is False
        assert runtime_env.vars['res_or'] is True
        assert runtime_env.vars['res_not'] is False
        print("-> 4. Logic Verification: Success! All boolean operations match specifications.")


    # --- TEST 18: NEGATIV - Type Error (Logical Expression with Invalid Operand Types) ---
    code_neg_logic_type = '''
        5 T & illegal_logic bool =:
    '''
    run_compiler_pipeline("Negative Case 10: Invalid Operand Types for Logical AND (INT & BOOL)", code_neg_logic_type)


    # --- TEST 19: NEGATIV - Shorthand IF Branch Type Conflict ---
    code_neg_ternary_type = '''
        T 42 F ? incompatible_ternary int =:
    '''
    run_compiler_pipeline("Negative Case 11: Incompatible Branch Types in Ternary Expression Error", code_neg_ternary_type)


    # --- TEST 20: POSITIV - Correct Ternary Operand Order (a b c ?) ---
    code_shorthand_correct_order = '''
        T 100 200 ? ternary_true int =:
        F 500 600 ? ternary_false int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 11: Correct Ternary Argument Order (a b c ?)", code_shorthand_correct_order)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['ternary_true'] == 100
        assert runtime_env.vars['ternary_false'] == 600
        print("-> 4. Ternary Verification: Success! Shorthand IF uses correct 'a b c ?' order.")


    # --- TEST 21: POSITIV - Short Circuiting of AND & OR ---
    # Typsicherer Vergleich: 1 1 == anstelle von T T ==
    code_short_circuit_logic = '''
        F  1 1 ==  & short_and bool =:
        T  1 2 ==  | short_or bool =:
    '''
    run_compiler_pipeline("Positive Case 12: Short Circuit Logical Evaluation", code_short_circuit_logic)


    # --- TEST 22: POSITIV - Proving Short Circuiting avoids Exceptions ---
    code_prove_short_circuit = '''
        F  1 0 /  2 0 / ==  &  proof_and bool =:
        T  1 0 /  2 0 / ==  |  proof_or bool =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 13: Proving Short Circuiting (Evading DivByZero)", code_prove_short_circuit)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['proof_and'] is False
        assert runtime_env.vars['proof_or'] is True
        print("-> 4. Short-Circuit Verification: Success! The interpreter successfully skipped the Division by Zero.")


    # --- TEST 23: NEGATIV - Syntax Error (Wrong Assignment Operator) ---
    code_wrong_assignment = '''
        10 a int :=
    '''
    run_compiler_pipeline("Negative Case 12: Invalid Assignment Syntax (:= instead of =:)", code_wrong_assignment)


    # --- TEST 24: POSITIV - Unary Negation Assignment ---
    code_negation_assign = '''
        20~ b int =:
    '''
    runtime_env = run_compiler_pipeline("Positive Case 14: Unary Negation in Assignment", code_negation_assign)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['b'] == -20, f"Expected -20, got {runtime_env.vars['b']}"
        print("-> 4. Assignment Verification: Success! Negated value correctly assigned.")

# --- TEST 25: POSITIV - Simple Function Definition and Call ---
    code_func_quad = '''
(x int) quad int LETTUCE
\t x x * return
(4) quad a int =:
'''
    runtime_env = run_compiler_pipeline("Positive Case 15: Function Definition and Call (quad)", code_func_quad)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['a'] == 16, f"Expected 16, got {runtime_env.vars['a']}"
        print("-> 4. Function Verification: Success! Function 'quad' evaluated correctly.")


    # --- TEST 26: POSITIV - Nested Functions / Closures ---
    code_nested_func = '''
(x int) outer int LETTUCE
\t1 x + x =:
\t(y int) inner int LETTUCE
\t\ty x - return
\tinner return

(2)(5) outer z int =:
'''
    runtime_env = run_compiler_pipeline("Positive Case 16: Nested Functions and Closures", code_nested_func)
    if runtime_env and hasattr(runtime_env, 'vars'):
        assert runtime_env.vars['z'] == -4, f"Expected -4, got {runtime_env.vars['z']}"
        print("-> 4. Function Verification: Success! Nested scope and closures work perfectly.")


    # --- TEST 27: NEGATIV - Scope Error (Calling inner function globally) ---
    code_scope_error = '''
(x int) outer int LETTUCE
\t1 x + x =:
\t(y int) inner int LETTUCE
\t\ty x - return
\tinner return

(5) inner broken int =:
'''
    run_compiler_pipeline("Negative Case 13: Scope Error (Calling nested function globally)", code_scope_error)


    # --- TEST 28: NEGATIV - Missing Return in Control Flow Branch ---
    code_missing_return = '''
(x int) outer int LETTUCE
\tT if
\t\t5 return
\telse
\t\t5 y int =:
'''
    run_compiler_pipeline("Negative Case 14: Missing Return in Control Flow Branch", code_missing_return)