import sys
import os
from lexer import build_lexer
from parser import parser
from type_checker import check_type
from interpreter import eval_ast

def execute_code(source_code, label="Source Code"):
    """Runs the provided source code through all compiler pipeline stages."""
    print(f"\n==========================================")
    print(f"RUNNING: {label}")
    print(f"==========================================")
    print("Code being executed:")
    print(source_code.strip())
    print("------------------------------------------")
    
    # 1. Initialize Lexer
    print("-> 1. Initializing Lexer...")
    test_lexer = build_lexer()
    test_lexer.input(source_code.strip())
    
    try:
        # 2. Parsing (AST generation)
        print("-> 2. Starting Parser...")
        ast = parser.parse(lexer=test_lexer)
        if ast is None:
            print("❌ Error: The parser returned no result (AST is None).")
            return
        print("   [Generated AST]:", ast)
        print("   Parser: Success! AST generated. ✅")
        
        # 3. Type Checking (Static Type Analysis)
        print("-> 3. Starting Type Checker...")
        symbol_table = {}
        for statement in ast:
            check_type(statement, symbol_table)
        print("   Type Checker: Success! No type errors found. ✅")
        
        # 4. Execution (Interpreter Runtime)
        print("-> 4. Starting Interpreter...")
        runtime_env = {}
        for statement in ast:
            eval_ast(statement, runtime_env)
        print("   Interpreter: Success! Code executed safely. 🎉")
        
        print("------------------------------------------")
        print(f"Final Environment/Variables State: {runtime_env}")
        print("==========================================\n")
        
    except SyntaxError as e:
        print(f"\n❌ SYNTAX ERROR: {e}")
    except TypeError as e:
        print(f"\n❌ TYPE ERROR: {e}")
    except Exception as e:
        print(f"\n❌ RUNTIME ERROR: {e}")

if __name__ == '__main__':
    print("DEBUG: main.py started!")

    # Check if a file path argument was passed via command line
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            print(f"Reading code from file: '{file_path}'")
            with open(file_path, 'r', encoding='utf-8') as f:
                code_to_run = f.read()
            execute_code(code_to_run, label=f"File Execution ({file_path})")
        else:
            print(f"❌ Error: File '{file_path}' not found.")
    else:
        # Fallback: Run the default built-in test loop case
        print("No input file provided. Running default test suite string...")
        default_code = '''
1 i int =:
100 result int =:
i 10 < WHILE
\ti 1 + i =:
\ti 3 == IF
\t\tbreak
2 3 ^ x int =:
'''

execute_code(default_code, label="Built-in Test Suite Case")