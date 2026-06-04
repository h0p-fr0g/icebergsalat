# =============================================================================
# --- MAIN TEST SUITE ---
# =============================================================================

from lexer import build_lexer
from parser import parser
from type_checker import check_type
from interpreter import eval_ast

def run_compiler_pipeline(test_name, source_code):
    print(f"\n==================================================================")
    print(f"RUNNING: {test_name}")
    print(f"==================================================================")
    print(f"Source Code:\n{source_code.strip()}\n")
    
    # 1. Lexer für diesen Durchlauf frisch initialisieren
    test_lexer = build_lexer()
    test_lexer.input(source_code.strip())
    
    try:
        # 2. Parsing (AST-Generierung)
        ast = parser.parse(lexer=test_lexer)
        print("-> 1. Parser: Success! AST successfully generated. 🌳")
        
        # 3. Statische Typ-Prüfung
        type_env = {
            'vars': {},
            'funcs': {},
            'current_return': None
        }
        for statement in ast:
            check_type(statement, type_env)
        print("-> 2. Type Checker: Success! All types are valid. ✅")
        
        # 4. Ausführung / Interpretation
        runtime_env = {
            'vars': {},
            'funcs': {}
        }
        for statement in ast:
            eval_ast(statement, runtime_env)
        print("-> 3. Interpreter: Success! Code executed flawlessly. 🎉")
        print(f"\nFinal State of Global Variables: {runtime_env['vars']}")
        
    except SyntaxError as e:
        print(f"❌ PARSING ERROR (Expected if negative test): {e}")
    except TypeError as e:
        print(f"❌ TYPE ERROR (Expected if negative test): {e}")
    except Exception as e:
        print(f"❌ RUNTIME ERROR: {e}")


if __name__ == "__main__":
    
    # --- TEST 1: POSITIV - Die Fakultätsfunktion (Schleife, Scopes, Mathe, Return) ---
    code_factorial = '''
(n int) fakultaet int LETTUCE
	1 res int =:
	n 1 > WHILE
		res n * res =:
		n 1 - n =:
	res RETURN

(5) fakultaet ergebnis int =:
'''
    run_compiler_pipeline("Positive Case 1: Advanced Factorial Function (5!)", code_factorial)


    # --- TEST 2: POSITIV - Komplexe Logik mit Shorthand IF (Ternary) und normalen Verzweigungen ---
    code_logic = '''
10 x int =:
F bed bool =:

x 5 > IF
	T bed =:

bed IF
	100 y int =:
	200 y =:

T F bed ? z bool =:
'''
    run_compiler_pipeline("Positive Case 2: Standard IF and Shorthand Ternary Operator", code_logic)


    # --- TEST 3: NEGATIV - Syntax-Fehler (Infix statt Postfix in der Funktion) ---
    code_neg_syntax = '''
(x int, y int) add int LETTUCE
	x + y RETURN
'''
    run_compiler_pipeline("Negative Case 1: Infix Operator Syntax Error inside Function", code_neg_syntax)


    # --- TEST 4: NEGATIV - Typ-Fehler (Falscher Argumenten-Typ beim Aufruf) ---
    code_neg_type = '''
(n int) quadrat int LETTUCE
	n n * RETURN

(T) quadrat ergebnis int =:
'''
    run_compiler_pipeline("Negative Case 2: Passing BOOL to INT Parameter Type Error", code_neg_type)


    # --- TEST 5: NEGATIV - Scope-Fehler (Zugriff auf lokale Variable außerhalb der Funktion) ---
    code_neg_scope = '''
() scope_test int LETTUCE
	99 geheimnis int =:
	geheimnis RETURN

() scope_test
geheimnis x int =:
'''
    run_compiler_pipeline("Negative Case 3: Accessing Local Variable Outside Scope Error", code_neg_scope)


    # --- TEST 6: NEGATIV - Return-Fehler (Globales Return ohne Funktion) ---
    code_neg_return = '''
5 x int =:
x RETURN
'''
    run_compiler_pipeline("Negative Case 4: Global RETURN Statement Error", code_neg_return)