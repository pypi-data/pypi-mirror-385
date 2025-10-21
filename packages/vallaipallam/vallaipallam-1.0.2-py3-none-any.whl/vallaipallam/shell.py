# ✅ Optimized shell.py for Vallaipallam
# ✅ Handles all error types in proper Tamil wording
# ✅ Cleaner structure, and better handling for user feedback

from vallaipallam.lexer import Lexer
from vallaipallam.parser import Parser
from vallaipallam.interpreter import Interpreter
from vallaipallam.data import Data
from vallaipallam.errors import Syntax_Error, Name_Error, Type_Error, Value_Error, Zero_Division_Error, Index_Error
import sys
import os
import time as t

root = Data()

def main():
    try:
        sys.stdout.reconfigure(encoding='utf8')
        if len(sys.argv)==2 :
            file_name = sys.argv[1]
            # கோப்பு சரிபார்ப்பு
            if not file_name or len(file_name) < 4:
                raise Syntax_Error(0, 'INAPROPRIATE FILE NAME')
            if not file_name.endswith('.jnr'):
                raise Syntax_Error(0, 'NOT A VALLAIPALLAM .jnr file')
            if not os.path.exists(file_name):
                raise Syntax_Error(0, f'"{file_name}" DOES NOT EXIST')

            with open(file_name, 'r', encoding='utf-8') as f:
                code = f.read()

            if not code.strip():
                raise Syntax_Error(0, 'FILE EMPTY')
        else:
            code=sys.argv[1]
        # Tokenize
        tokens = Lexer(code).tokenize()
        #Parse
        tree = Parser(tokens).parse()
        #Interpret
        output = Interpreter(tree, root).home()

        
    except (Syntax_Error, Name_Error, Type_Error, Value_Error, Zero_Division_Error, Index_Error):
        pass  # Already handled inside the error class

   

if __name__ == '__main__':
    start=t.time()
    main()
    end=t.time()
    print("Execution time:",end-start,"seconds")
