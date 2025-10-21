from vallaipallam.errors import *
import os,sys



class Token:
    __slots__ = ('type', 'value')

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return str(self.value)
    def unwrap(self,arg):
        """Ensure we always return the raw Python value, regardless of Token or primitive"""
        return arg.value if hasattr(arg, 'value') else arg

    def அளவு(self, arguements, line_no):
        try:
            value = arguements[0].value if isinstance(arguements, list) else arguements
            return Number(len(value))
        except Exception:
            Value_Error(line_no, f'{value} அளவு இல்லை')

    def வெளியிடு(self, arguements,line_no):
        try:
            sys.stdout.write('  '.join(str(i) for i in arguements) + '\n')
        except Exception as e:
            print(e)

    def உள்ளிடு(self, arguements,line_no):
        prompt = str(arguements[0].value) if arguements else ''
        sys.stdout.write(prompt)
        sys.stdout.flush()
        value=sys.stdin.readline().strip()
        return String(value)

    def எண்(self, arguements, line_no):
        try:
            arg=arguements[0] if isinstance(arguements, list) else arguements
            value = self.unwrap(arg)
            return Number(float(value))
        except:
            Value_Error(line_no, f"{arguements[0].value} --> எண் மாற்ற முடியாது")

    def சொல்(self, arguements, line_no):
        try:
            arg=arguements[0] if isinstance(arguements, list) else arguements
            value = self.unwrap(arg)
            return String(str(value))
        except IndexError:
            return String(str())
        except:
            Value_Error(line_no, f"{arguements[0].value} --> சொல் மாற்ற முடியாது")

    def பட்டியல்(self, arguements, line_no):
        try:
            arg=arguements[0] if isinstance(arguements, list) else arguements
            value = self.unwrap(arg)
            return List(list(value))
        except IndexError:
            return List(list())
        except:
            Value_Error(line_no, f"{arguements[0].value} --> பட்டியல் மாற்ற முடியாது")

    def வகை(self, arguements,line_no):
        value_type = None
        if isinstance(arguements[0], Number):
            value_type = 'எண்'
        elif isinstance(arguements[0], String):
            value_type = 'சொல்'
        elif isinstance(arguements[0], List):
            value_type = 'பட்டியல்'
        elif isinstance(arguements[0], Function):
            value_type = 'வேலை'
        return value_type

    def வரம்பு(self, arguements, line_no):
        try:
            number = int(arguements[0].value)
            if len(arguements) == 1:
                return List([Number(i) for i in range(number)])
            elif len(arguements) == 2:
                end = int(arguements[1].value)
                return List([Number(i) for i in range(number, end)])
            elif len(arguements) == 3:
                step = int(arguements[2].value)
                end = int(arguements[1].value)
                return List([Number(i) for i in range(number, end, step)])
        except Exception:
            raise Exception('வரம்பு: தவறான அளவுருக்கள்')

    def திற(self, arguements, line_no):
        file_name = arguements[0].value
        mode_map = {'ப': 'r', 'எ': 'w', 'சே': 'a'}
        mode = mode_map.get(arguements[1].value)

        if not mode:
            Value_Error(line_no, f"{arguements[1].value} என்ற முறை இல்லை")

        if os.path.isfile(file_name) or mode in ('w', 'a'):
            return FileObject(open(file_name, mode, encoding='utf-8'))
        else:
            Name_Error(line_no, f"{file_name} என்ற கோப்பு இல்லை")

# Remaining classes (unchanged logic, with __slots__ where applicable)
class Number(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('எண்', value)

class Operator(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('கணிதசெயலி', value)

class Declaration(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('DEC', value)

class Variable(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('மாறி', value)

class Logical(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('தருக்க', value)

class Comparison(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('ஒப்பீடு', value)

class Boolean(Token):
    __slots__ = ()
    def __init__(self, value):
        if hasattr(value,'value'):
            value=value.value
        value = 'பொய்' if value in (0.0, 'பொய்','காலி') else 'மெய்'
        super().__init__('மெய்ப்பு', value)

class Null(Token):
    __slots__ = ()
    def __init__(self):
        super().__init__('காலி', 'காலி')

class Condition(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('CON', value)

class String(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('சொல்', value)

    def பிரி(arguements,line_no):
        value = arguements[0]
        limit = arguements[1].value if len(arguements) >= 2 else None
        maxsplit = arguements[2].value if len(arguements) == 3 else -1
        if limit:
            return List([String(i) for i in value.split(limit, maxsplit)])
        return List([String(i) for i in value.split()])

class List(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('பட்டியல்', value)

    def இணை(arguements, line_no):
        value, element = arguements[0], arguements[1]
        if isinstance(element, (int, float)):
            element = Token().எண்([element], line_no)
        elif isinstance(element, str):
            element = Token().சொல்([element], line_no)
        elif isinstance(element, list):
            element = Token().பட்டியல்([element], line_no)
        value.append(element)
        return List(value)

    def நீக்கு(arguements, line_no):
        value = arguements[0]
        index = arguements[1] if isinstance(arguements[1], int) else -1
        print(value.pop(index))
        return List(value)

    def செருகு(arguements, line_no):
        value, index, element = arguements[0], int(arguements[1].value), arguements[2]
        if isinstance(element, (int, float)):
            element = Token().எண்([element], line_no)
        elif isinstance(element, str):
            element = Token().சொல்([element], line_no)
        elif isinstance(element, list):
            element = Token().பட்டியல்([element], line_no)
        value.insert(index, element)
        return List(value)

class Delimiter(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('DELIMIT', value)

class Keyword(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('KEY', value)

class Member(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('MEM', value)

class Function(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('வேலை', value)

class Built_in_Function(Token):
    __slots__ = ()
    def __init__(self, value):
        super().__init__('BIF', value)

class FileObject(Token):
    __slots__ = ('name', 'mode', 'encoding', 'value')

    def __init__(self, value):
        self.name = value.name
        self.mode = value.mode
        self.encoding = value.encoding
        super().__init__('FO', value)

    def படி( arguements,line_no):
        element = arguements[0]
        noofchar = arguements[1] if len(arguements) == 2 else -1
        return String(element.value.read(noofchar))

    def எழுது(arguements, line_no):
        element = arguements[0]
        if isinstance(arguements[1].value, str):
            return Number(element.value.write(arguements[1].value))
        else:
            Type_Error("", "சொல் வகை மட்டும்")

    def மூடு(arguements,line_no):
        return arguements[0].value.close()

