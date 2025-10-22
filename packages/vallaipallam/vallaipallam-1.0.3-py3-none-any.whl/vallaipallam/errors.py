# ✅ Optimized errors.py for Vallaipallam
# ✅ Compact, consistent, and stderr-directed Tamil error reporting
# ✅ Ensures compatibility across interpreter, parser, lexer, and shell

import sys

class Error(Exception):
    color = '\033[91m'  # Red
    default = '\033[0m'

    def __init__(self, error_type, line, message):
        self.error_type = error_type
        self.line = line
        self.message = message
        self.display_error()

    def display_error(self):
        print(f"{self.color}LINE: {self.line}\nERROR: {self.error_type}\n{self.message}{self.default}", file=sys.stderr)
        sys.exit(1)

class Syntax_Error(Error):
    def __init__(self, line, message):
        super().__init__("SYNTAX_ERROR", line, str(message))

class Name_Error(Error):
    def __init__(self, line, message):
        super().__init__("NAME_ERROR", line, f"{message} ")

class Value_Error(Error):
    def __init__(self, line, message):
        super().__init__("VALUE_ERROR", line, f"{message} ")

class Type_Error(Error):
    def __init__(self, line, message):
        super().__init__("TYPE_ERROR", line, f"{message} ")

class Zero_Division_Error(Error):
    def __init__(self, line, message):
        super().__init__("Zero_Division_Error", line, str(message))

class Index_Error(Error):
    def __init__(self, line, message):
        super().__init__("iNDEX ERROR", line, str(message))
