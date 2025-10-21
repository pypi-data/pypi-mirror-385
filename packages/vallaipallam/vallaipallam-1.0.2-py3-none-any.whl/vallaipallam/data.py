# ✅ Optimized data.py for Vallaipallam
# ✅ Preserves logic and syntax exactly
# ✅ Improves performance, memory handling, and structure
# ✅ Tamil-English comments added for clarity

from vallaipallam.errors import *

class Data:
    # ✅ Shared global variables dictionary
    variables = {}

    def __init__(self):
        self.variables = {}
        Data.variables.update(self.variables)

    def get(self, id):
        """பொது நிலை மாறியை பெறும் / Fetch global variable"""
        try:
            return Data.variables[id]
        except KeyError:
            Name_Error("", f"{id} NOT DEFINED")

    def get_all(self):
        return self.variables

    def set(self, variable, expression):
        """மாறி மதிப்பை அமை/ Set global variable"""
        variable_name = variable.value
        self.variables[variable_name] = expression
        Data.variables[variable_name] = expression


class Scope(Data):
    # ✅ Tracks all scopes
    details = []

    def __init__(self, name=None):
        super().__init__()
        self.localvariables = {}
        self.value = name
        Scope.details.append([self, name])

    def get(self, id):
        """மாறியை பெறும் / First try global, then local"""
        try:
            if id in self.variables:
                return self.variables[id]
            return self.localvariables[id]
        except KeyError:
            Name_Error("", f"{id} NOT DEFINED")

    def get_all(self):
        return self.localvariables

    def set(self, variable, expression):
        """உள்ளக மாறி அமை/ Set local variable only"""
        variable_name = variable.value
        self.localvariables[variable_name] = expression

