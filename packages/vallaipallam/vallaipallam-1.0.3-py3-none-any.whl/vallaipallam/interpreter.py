# ✅ Optimized interpreter.py for Vallaipallam
# ✅ Preserves all logic and syntax (no grammar/keyword changes)
# ✅ Faster recursion, correct scoping, efficient eval
# ✅ Handles user-defined and built-in function calls in expressions and conditions

from vallaipallam.tokens import *
from vallaipallam.data import Scope, Data
import os,io
from vallaipallam.lexer import Lexer
from vallaipallam.parser import Parser
from vallaipallam.errors import *
from vallaipallam.network import *

class Interpreter:
    continuing = 0
    value_to_return = ''
    line_no = 1

    def __init__(self, tree, root):
        self.tree = tree
        self.data = root

    def read_மாறி(self, id, scope=None):
        target = scope if isinstance(scope, Scope) else self.data
        value = target.get(id)
        return value if isinstance(value,(float,int,str)) else getattr(self, f'read_{value.type}')(value.value)

    def read_எண்(self, val, scope=None): return float(val)
    def read_சொல்(self, val, scope=None): return str(val)
    def read_மெய்ப்பு(self, val, scope=None): return bool(val)
    def read_பட்டியல்(self, val, scope=None):return self.extract_list(val)
    def read_FO(self, val, scope=None): return FileObject(val)
    def read_காலி(self, val, scope=None): return Null()
    def read_KEY(self, val, scope=None): return val
    def read_NET(self,val,scope=None):return val
    def compute_unary(self, op, node):
        val = self.read_மாறி(node.value) if node.type.startswith("மாறி") else getattr(self, f'read_{node.type}')(node.value)
        return Number(+val if op.value == '+' else -val) if op.value in '+-' else Boolean(1.0 if not val else 0.0)

    def compute_operation(self, left, op, right, scope=None):
        if op.value == '=':
            left.type = f'மாறி({right.type})' 
            if isinstance(right,List):
                right=List(self.extract_list(right.value))
            (scope or self.data).set(left, right)
            return True

        left = left if isinstance(left, float) else getattr(self, f'read_{left.type if not left.type.startswith("மாறி") else "மாறி"}')(left.value, scope)
        right = right if isinstance(right, float) else getattr(self, f'read_{right.type if not right.type.startswith("மாறி") else "மாறி"}')(right.value, scope)
        # Use Python-native ops where allowed
        print(left,right)
        if op.value=='+' :
            output=left+right
        elif op.value=='-' :
            output=left-right
        elif op.value=='*' :
            output=left*right
        elif op.value=='/':            
            output=left/right if right!=0 else Zero_Division_Error(Interpreter.line_no,"0 CANNOT DIVIDE")
        elif op.value=='%':
            output=left%right    
        elif op.value=='>':
            output=1.0 if left>right else 0.0
            output=Boolean(output)    
        elif op.value=='<':
            output=1.0 if left<right else 0.0  
            output=Boolean(output) 
        elif op.value=='>=':
            output=1.0 if left>=right else 0.0
            output=Boolean(output)   
        elif op.value=='<=':
            output=1.0 if left<=right else 0.0  
            output=Boolean(output) 
        elif op.value=='==':
            output=1.0 if left==right else 0.0  
            output=Boolean(output) 
        elif op.value=='!=':
            output=1.0 if left!=right else 0.0  
            output=Boolean(output) 
        elif op.value=='மற்றும்':
            output=1.0 if left and right else 0.0   
            output=Boolean(output)
        elif op.value=='அல்லது':
            output=1.0 if left or right else 0.0   
            output=Boolean(output)
        elif op.value=='உள்ளது':
            output=1.0 if left in right else 0
            output=Boolean(output)                                                                                                
                
        if isinstance(output, float): return Number(output)
        if isinstance(output, str): return String(output)
        return output

    def compute_function(self, tree,object=None):
        identifier, args = tree
        args=[self.interpret(i,object=object) for i in args ]
        scope = next((i[0] for i in Scope.details if i[1] == identifier.value), None)
        if not scope:
            Name_Error("", f"{identifier.value} NOT A FUNCTION")

        func = self.data.get(identifier.value).value
        if len(func[0]) != len(args):
            Type_Error(Interpreter.line_no, "UNEQUAL PARAMETERS AND ARGUEMENTS.")

        for param, val in zip(scope.localvariables, args):
            scope.set(Variable(param), self.interpret(val,object) if isinstance(val,list) else val)
        
        for stmt in func[-1]:
            if stmt[0].value == 'கொடு':
                return self.interpret(stmt[1], object=scope)
            result = self.interpret(stmt, object=scope)
            if Interpreter.continuing == -2:
                Interpreter.continuing=0
                return Interpreter.value_to_return
            
        return Null()
    
    def interpret_if(self, tree, scope=None):
        conds, blocks = tree[1]
        for cond, stmts in zip(conds, blocks):
            check=self.interpret(cond, scope)
            if Boolean(check if not hasattr(check,'value') else check.value).value == 'மெய்':
                return [cond, [self.interpret(stmt, scope) for stmt in stmts]]
        if len(blocks) > len(conds):
            return [None, [self.interpret(stmt, scope) for stmt in blocks[-1]]]

    def interpret_while(self, tree, scope=None):
        condition_node = tree[1][0]
        condition = Boolean(self.interpret(condition_node))
        block = tree[1][1][0]
        result = []
        while condition.value == 'மெய்':
            for stmt in block:
                action = self.interpret(stmt, scope)
                if Interpreter.continuing in [-1,1,-2]:
                    break
                result.append(action)
            if Interpreter.continuing in [-1,-2]:
                break    
            condition = Boolean(self.interpret(condition_node))
        return [condition, result]
    
    def extract_list(self,tree):
        for i in range(len(tree)):
            tree[i]=self.interpret(tree[i])
        return tree
    
    def interpret(self, tree=None, object=None):
        if tree is None:
            tree = self.tree 
        if isinstance(tree, list):
            if len(tree) == 2 and isinstance(tree[0], Operator):
                return self.compute_unary(tree[0], self.interpret(tree[1], object))

            if isinstance(tree[0], Condition):
                if tree[0].value == 'இது':
                    return self.interpret_if(tree, object)
                elif tree[0].value == 'அதுவரை':
                    output = []
                    result = self.interpret_while(tree, object)
                    output.append(result[1])
                    return output
                elif tree[0].value == 'இதில்':
                    sequence = self.interpret(tree[1][0], object)
                    var=tree[1][1]
                    actions = tree[1][2]
                    result = []
                    seq = sequence.value if hasattr(sequence, "value") else sequence
                    for item in seq:
                        self.data.set(var, String(item) if isinstance(item, str) else item)
                        for stmt in actions:
                            value = self.interpret(stmt, object)
                            if Interpreter.continuing in (1, -1): break
                            result.append(value)
                        if Interpreter.continuing == -1: break
                    return result

            if isinstance(tree[0], Function):
                if tree[0].value == 'வேலை':
                    scope = Scope(tree[1][0].value)
                    for param in tree[1][1][0]:
                        if isinstance(param,list): 
                            scope.set(param[0], param[2])
                        else:
                            scope.set(param,Null)    
                    self.data.set(scope, List(tree[1][1]))
                elif tree[0].value == 'கூப்பிடு':
                    return self.compute_function(tree[1],object)
                elif tree[0].value == 'கொடு':
                    Interpreter.continuing = -2
                    Interpreter.value_to_return = self.interpret(tree[1], object)
                return None

            if isinstance(tree[0], Built_in_Function):
                args = [self.interpret(arg, object) for arg in tree[1]]
                if tree[0].value in ['நீக்கு',  'இணை', 'செருகு'] and isinstance(tree[1][0],Variable):
                    value=getattr(List, tree[0].value)(args,Interpreter.line_no)
                    (object or self.data).set(tree[1][0],value)
                    return None
                elif tree[0].value in ['பிரி','படி', 'எழுது', 'மூடு'] and isinstance(args[0],(str,FileObject)) :
                    value=getattr(String if isinstance(args[0],str) else FileObject, tree[0].value)(args,Interpreter.line_no)
                    return value
                
                return getattr(tree[0], tree[0].value)(args,Interpreter.line_no)
            
            if isinstance(tree[0],NetworkObject):
                if len(tree)>1:
                    for i in range(len(tree[1])):
                        if isinstance(tree[1][i],Variable):
                            tree[1][i]=String(self.interpret(tree[1][i]))
                return tree[0].execute_command(Interpreter.line_no,args=tree)
            if not isinstance(tree[0], list):
                if tree[0].value == 'இறக்கு':
                    file_name = tree[1]
                    if os.path.isfile(f'{file_name}.jnr'):
                        root = Data()
                        with open(f'{file_name}.jnr', 'r', encoding='utf-8') as f:
                            code = f.read()
                        tokens = Lexer(code).tokenize()
                        ast = Parser(tokens).parse()
                        return Interpreter(ast, root).home()

                if isinstance(tree[1], List):
                    value = self.read_மாறி(tree[0].value) if isinstance(tree[0], Variable) else tree[0].value
                    idx = [int(e.value) for e in tree[1].value]
                    return value[slice(*idx)]
            
            left = self.interpret(tree[0], object) if isinstance(tree[0], list) else tree[0]
            right = self.interpret(tree[2], object) if (len(tree) > 2 and isinstance(tree[2], list)) or isinstance(tree[2],NetworkObject) else tree[2]
            print(left,right)
            return self.compute_operation(left, tree[1], right, object)
        if isinstance(tree, Keyword):
            if tree.value == 'ரத்து':
                Interpreter.continuing = -1
            elif tree.value == 'தொடர்':
                Interpreter.continuing = 1
            return tree.value

        if isinstance(tree, Boolean): return tree
        if isinstance(tree, Variable): return self.read_மாறி(tree.value, object)
        if isinstance(tree,NetworkObject): return tree.execute_command(Interpreter.line_no)
        if isinstance(tree,List):return self.extract_list(tree)
        return tree

    def home(self):
        Interpreter.continuing=0
        return [self.interpret(line) for line in self.tree]
