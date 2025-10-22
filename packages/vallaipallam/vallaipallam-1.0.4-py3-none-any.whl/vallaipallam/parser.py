# Optimized parser for Vallaipallam (no syntax/logic changes)
# - Fixes token movement bugs (esp. in term/factor)
# - Supports DEC declaration *and* reassignment without DEC
# - Allows builtin & user-defined function calls inside expressions/conditions
# - Preserves expected AST shapes for interpreter.py

from vallaipallam.tokens import (
    Null, Operator, Number, String, List, Boolean,
    Variable, Declaration, Keyword, Member,
    Function, Built_in_Function, Condition
)
from vallaipallam.errors import *


class Parser:
    line_no = 1

    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        self.token = self.tokens[self.idx] if self.tokens else None
             

    # ---------- core cursor helpers ----------
    def move(self):
        self.idx += 1
        if self.idx < len(self.tokens):
            self.token = self.tokens[self.idx]
        else:
            self.token = Keyword('EOF')
        return self.token

    def peek(self, k=1):
        i = self.idx + k
        return self.tokens[i] if 0 <= i < len(self.tokens) else Keyword('EOF')

    def expect(self, value=None, type_=None, msg=None):
        if value is not None and self.token.value != value:
            Syntax_Error(Parser.line_no, msg or f"<-- '{value}' NEEDED")
        if type_ is not None and not (self.token.type == type_ or (isinstance(type_, tuple) and self.token.type in type_)):
            Syntax_Error(Parser.line_no, msg or f"<-- {type_} NEEDED")
        tok = self.token
        self.move()
        return tok
    
    def network_commands(self):
        """
        Parse  English DSL network commands
        Returns: [command_token, args...]
        """
        cmd = self.token
        args = []
        
        # --- Category 1: Simple single-argument commands ---
        if cmd.value in ["RUN_AS_ADMIN","SHOW_INTERFACE_ADDRESSES","SHOW_INTERFACE_STATUS","SHOW_NETWORK_IO","SHOW_NETWORK_IO_PER_INTERFACE","SHOW_ACTIVE_CONNECTIONS","SHOW_GATEWAY",'ENABLE_FIREWALL','DISABLE_FIREWALL','LIST_FIREWALL_RULES','LIST_WIFI',"DISCONNECT_WIFI"]:
            self.move()
        elif cmd.value in ["ENABLE_INTERFACE","DISABLE_INTERFACE",'PING','TRACEROUTE','DNS_LOOKUP','LATENCY_TEST',
            "SET_DHCP","SHOW_NETWORK_SPEED",'ALLOW_PORT','BLOCK_PORT','ALLOW_SERVICE','BLOCK_SERVICE'
        ]:
            self.move()
            iface = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு இடைமுகம் தேவை")
            args.append(iface)

        # --- Category 2: Wi-Fi connect (needs SSID + password) ---
        elif cmd.value in ['CONNECT_WIFI','PORT_SCAN']:
            ARRTRIBUTES={
                'CONNECT_WIFI':'PASSWORD',
                'PORT_SCAN':'PORT'
            }
            self.move()
            ssid = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு SSID தேவை")
            self.expect(value=ARRTRIBUTES[cmd.value], msg=f"{cmd.value}க்கு  keyword தேவை")
            password = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு கடவுச்சொல் தேவை")
            args.extend([ssid, password])

        # --- Category 3: Static IP setup ---
        elif cmd.value in ["SET_IP"]:
            self.move()
            iface = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு இடைமுகம் தேவை")
            ip = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு IP முகவரி தேவை")

            self.expect(value='GATEWAY', msg=f"{cmd.value}க்கு gateway keyword தேவை")
            gw = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு gateway தேவை")

            self.expect(value='NETMASK', msg=f"{cmd.value}க்கு netmask keyword தேவை")
            mask = self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value}க்கு netmask தேவை")

            args.extend([iface, ip, gw, mask])
        
        elif cmd.value == "ACTIVATE_AGENT_VALLAI":
            self.move()
            self.expect(value="WORKING_DIRECTORY",msg=f"{cmd.value} meeded  WORKING_DIRECTORY keyword")
            working_dir=self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value} needed working directory")
            self.expect(value="GEMINI_API_KEY",msg=f"{cmd.value} meeded  GEMINI_API_KEY keyword")
            gemini_api=self.expect(type_=('சொல்','மாறி'), msg=f"{cmd.value} needed gemini api key.")
            
            args.extend([working_dir,gemini_api])

        else:
            Name_Error(Parser.line_no, f"{cmd.value} UNKNOWN NETWORK COMMAND")

         # advance after handling
        return [cmd, args] if args else [cmd]

    # ---------- expressions ----------
    def factor(self):
        t = self.token

        # literals & identifiers
        if t.type in ('எண்', 'சொல்', 'மெய்ப்பு') or t.type.startswith('மாறி') or t.type == 'KEY':
            self.move()
            return t
        if t.type == 'பட்டியல்':
            elements = []
            for element_tokens in t.value:
                element_parser = Parser(element_tokens)
                element_ast = element_parser.parse()[0]
                elements.append(element_ast)
            t.value = elements
            self.move()
            return t
            
        # parenthesized
        if t.value == '(':
            self.move()
            node = self.logical_expression()
            self.expect(')')
            return node

        # unary +/-
        if t.value in ('+', '-'):
            op = t
            self.move()
            return [op, self.factor()]

        # logical NOT
        if t.value == 'அல்ல':
            op = t
            self.move()
            return [op, self.comparison_expression()]

        # return keyword (handled as prefix unary list at stmt level, but allow here for nested)
        if t.value == 'கொடு':
            self.move()
            return t

        # call sites: கூப்பிடு <id>(...)
        if t.value == 'கூப்பிடு':
            func = t
            call = self.function_call()
            return [func, call]

        # built-in function bare (e.g., அளவு(...))
        if t.type == 'BIF':
            bif = t
            args = self.builtin_function()
            return [bif, args]

        # closing delimiters should be handled by expect
        if t.value in (')', '}', ']'):
            return t
        
        if t.type=='NET':
            return self.network_commands()
        Name_Error(Parser.line_no, f"{t} DOES NOT EXIST")

    def call_or_member(self):
        # base factor (literal/var/call/parenthesized)
        node = self.factor()
        # member/builtin like  
        while self.token.value == '.':
            self.move()
            if self.token.type == 'BIF':
                bif = self.token
                args = self.builtin_function(node)
                node = [bif, args]
            else:
                Syntax_Error(Parser.line_no, '<-- ABSENCE OF BIF')
        if self.peek().type in ['பட்டியல்','சொல்'] and self.token.type=='பட்டியல்' and len(self.token.value)==1:
            node=[self.peek()]
            while self.token.type=='பட்டியல்' and len(self.token.value)==1:
                node.append(self.token.value[0])
                self.move()
            if self.token.value=='=':
                self.move()
                node=[node,self.token,self.statement()]
        
        return node

    def term(self):
        left = self.call_or_member()

        while self.token.value in ('*', '/', '%'):
            op = self.token
            self.move()
            right = self.call_or_member()
            left = [left, op, right]
        return left

    def expression(self):
        left = self.term()
        while self.token.value in ('+', '-'):
            op = self.token
            self.move()
            right = self.term()
            left = [left, op, right]
        return left

    def comparison_expression(self):
        left = self.expression()
        while self.token.value in ('>', '<', '>=', '<=', '!=', '==', 'உள்ளது'):
            op = self.token
            self.move()
            right = self.expression()
            left = [left, op, right]
        return left

    def logical_expression(self):
        left = self.comparison_expression()
        while self.token.value in ('மற்றும்', 'அல்லது'):
            op = self.token
            self.move()
            right = self.comparison_expression()
            left = [left, op, right]
        return left

    # ---------- statements ----------
    def variable(self):
        if self.token.type.startswith('மாறி'):
            tok = self.token
            self.move()
            return tok
        if self.token.value in ['வெளியிடு','உள்ளிடு','எண்','வரம்பு','பட்டியல்','சொல்','வகை','பிரி','திற','படி','எழுது','மூடு','என்றால்','இது','இல்லை','இல்லையெனில்','அதுவரை','இதில்','இருந்து','மற்றும்','அல்லது','அல்ல','மெய்','பொய்','தொடர்','ரத்து','கொடு','இறக்கு','உருவாக்கு','உள்ளது','கூப்பிடு','வேலை']:
            Syntax_Error(Parser.line_no, f"{self.token} மாறியாக பயன்படுத்தக்கூடாது")
        Syntax_Error(Parser.line_no, 'மாறி பயன்படுத்த')

    def assignment_like(self):
        # Handles: DEC <var> [= expr]  |  <var> = expr
        
        if self.token.type.startswith('DEC'):
            self.move()
            left = self.variable()
            if self.token.value == '=':
                op = self.token; self.move()
                right = self.logical_expression()
            else:
                op = Operator('='); right = Null()
            return [left, op, right]

        # reassignment without DEC
        if self.token.type.startswith('மாறி') and self.peek().value == '=':
            left = self.variable()
            op = self.expect('=')
            right = self.logical_expression()
            return [left, op, right]
        return None

    def if_statement(self):
        # token is 'இது'
        self.move()
        condition = self.logical_expression()
        actions = []
        self.expect('என்றால்')
        self.expect('{')
        block = []
        while self.token.value != '}' and self.idx < len(self.tokens):
            block.append(self.statement())
        self.expect('}')
        actions.append(block)
        return condition, actions

    def if_statements(self):
        # ஆரம்ப 'இது'
        conds = []
        blocks = []
        first_cond, first_block = self.if_statement()
        conds.append(first_cond)
        blocks += first_block
    
        # else-if(s)
        while self.token.value == 'இல்லையெனில்':
            cond, blk = self.if_statement()
            conds.append(cond)
            blocks += blk
            
        # else
        if self.token.value == 'இல்லை':
            self.move()
            self.expect('{')
            else_block = []
            while self.token.value != '}' and self.idx < len(self.tokens):
                else_block.append(self.statement())
            self.expect('}')
            blocks.append(else_block)
        return [conds, blocks]

    def while_statement(self):
        # token is 'அதுவரை'
        self.move()
        condition = self.logical_expression()
        self.expect('{')
        block = []
        while self.token.value != '}' and self.idx < len(self.tokens):
            block.append(self.statement())
        self.expect('}')
        actions = [block]
        # optional else block
        if self.token.value == 'இல்லை':
            self.move()
            self.expect('{')
            else_block = []
            while self.token.value != '}' and self.idx < len(self.tokens):
                else_block.append(self.statement())
            self.expect('}')
            actions.append(else_block)
        return [condition, actions]

    def for_statement(self):
        # token is 'இதில்'
        self.move()
        sequence = self.logical_expression()
        self.expect('இருந்து')
        var = self.variable()
        self.expect('{')
        actions = []
        while self.token.value != '}' and self.idx < len(self.tokens):
            actions.append(self.statement())
        self.expect('}')
        return [sequence, var, actions]

    def function_block(self):
        # token is 'வேலை'
        self.move()
        identifier = self.variable()
        self.expect('(')
        params = []
        if self.token.value != ')':
            while True:
                params.append(self.statement())
                if self.token.value == ',':
                    self.move(); continue
                break
        self.expect(')')
        self.expect('{')
        actions = []
        while self.token.value != '}' and self.idx < len(self.tokens):
            actions.append(self.statement())
        self.expect('}')
        return [identifier, [params, actions]] 

    def function_call(self):
        # current token is 'கூப்பிடு'
        self.move()
        identifier = self.variable()
        self.expect('(')
        values = []
        if self.token.value != ')':
            while True:
                values.append(self.logical_expression())
                if self.token.value == ',':
                    self.move(); continue
                break
        self.expect(')')
        return [identifier, values]

    def builtin_function(self, var=None):
        # current token is BIF name
        bif = self.token
        self.move()
        self.expect('(')
        args = []
        if self.token.value != ')':
            while True:
                args.append(self.logical_expression())
                if self.token.value == ',':
                    self.move(); continue
                break
        self.expect(')')
        if var is not None:
            args.insert(0, var)
        return args
        
    def statement(self):
        # handle declarations/assignments first
        assign = self.assignment_like()
        if assign is not None:
            return assign

        # control flow & functions
        if self.token.value == 'கொடு':
            kw = self.token; self.move()
            return [kw, self.statement()]
        if self.token.value == 'இறக்கு':
            kw = self.token; self.move()
            file_name = self.token; self.move()
            return [kw, file_name]
        if self.token.value == 'இது':
            return [Condition('இது'), self.if_statements()]
        if self.token.value == 'அதுவரை':
            return [Condition('அதுவரை'), self.while_statement()]
        if self.token.value == 'இதில்':
            return [Condition('இதில்'), self.for_statement()]
        if self.token.value == 'வேலை':
            return [Function('வேலை'), self.function_block()]
        if self.token.value == 'கூப்பிடு':
            return [Function('கூப்பிடு'), self.function_call()]
        if self.token.type == 'BIF':
            return [Built_in_Function(self.token.value), self.builtin_function()]
        if self.token.type=='NET':
            return self.network_commands()
        # expression fall-through (incl. literals, vars, calls)
        if self.token.type in ('எண்', 'சொல்', 'மெய்ப்பு', 'பட்டியல்', 'KEY', 'MEM','NET') or \
           self.token.type.startswith('மாறி') or self.token.value in ('(', '+', '-', 'அல்ல', 'கூப்பிடு') or \
           self.token.type == 'BIF':
            return self.logical_expression()

        Name_Error(Parser.line_no, f"{self.token} DOES NOT EXIST")

    # ---------- entry ----------
    def parse(self):
        output = []
        while self.idx < len(self.tokens):
            stmt = self.statement()
            output.append(stmt)
            Parser.line_no += 1

        return output