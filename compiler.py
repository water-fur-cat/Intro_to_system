import sys
import os

keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 
            'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbols = ['(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*', '/', '&', '|', '~', '<', '>']

class Stack:
    def __init__(self):
        self.top = None
        self.stack = []

    def push(self, value):
        self.stack.append(value)
        self.top = value

    def pop(self):
        value = self.stack.pop()
        if self.stack:
            self.top = self.stack[-1]
        else:
            self.top = None
        return value

    def top_element(self):
        return self.top

    def is_empty(self):
        return self.top == None

class Tokenizer:
    def __init__(self, file):
        self.file = file
        self._current_word = 0
        letter = self.remove_string()
        self.stack = Stack()
        letter = letter[::-1]
        for i in range(len(letter)):
            value = letter[i]
            self.stack.push(value)
    
    def remove_string(self):
        letter = []
        indices = []
        i1 = self.file.find('"') #index
        if i1 == -1: 
            return self.file.split()
        else:
            i2 = self.file.find('"', i1 + 1)
            while i1 != -1:
                indices.append((i1, i2))
                i1 = self.file.find('"', i2 + 1)
                i2 = self.file.find('"', i1 + 1)
                if i2 == -1:
                    i1 = -1
            letter = []
            start_i = 0
            for (start, end) in indices:
                letter += self.file[start_i:start].split()
                letter.append(self.file[start:end + 1])
                start_i = end + 1
            letter += self.file[start_i:].split()
        return letter

    def not_empty(self):
        return not self.stack.is_empty()

    def next_input(self):
        self.stack.pop()

    def token_type(self):
        type_token = None
        while not type_token:
            value = self.stack.top_element()
            if value in keywords:
                type_token = "keyword"
            elif value.isdigit():
                type_token = "integerConstant"
            elif value.startswith('"') and value.endswith('"'):
                type_token = "stringConstant"
            elif value in symbols:
                type_token = "symbol"
            elif self.split_symbol(value):
                type_token = None
            else:
                type_token = "identifier"
        return type_token

    def split_symbol(self, string):
        n = len(string)
        for symbol in symbols:
            if symbol in string:
                index = string.find(symbol)
                if index == n - 1:
                    s1 = string[0:n - 1]
                    s2 = string[-1]
                elif index == 0:
                    s1 = string[0]
                    s2 = string[1:]
                else:
                    s1 = string[0:index]
                    s2 = string[index:]
                self.next_input()
                self.stack.push(s2)
                self.stack.push(s1)
                return True
        return False

    def keyword(self):
        if self.stack.top_element() in keywords:
            return self.stack.top_element()

    def symbol(self):
        if self.stack.top_element() in symbols:
            # if self.stack.top_element() == '<':
            #     return "&lt;"
            # if self.stack.top_element() == '>':
            #     return "&gt;"
            # if self.stack.top_element() == '&':
            #     return "&amp;"
            return self.stack.top_element()

    def identifier(self):
        return self.stack.top_element()

    def int_val(self):
        return self.stack.top_element()

    def string_val(self):
        return self.stack.top_element().strip('"')

    def value(self):
        map = {"keyword": self.keyword, "symbol": self.symbol, "identifier": self.identifier, "stringConstant": self.string_val, "integerConstant": self.int_val}
        return map[self.token_type()]()

class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.class_table_running_count = {"static": 0, "field": 0}
        self.subroutine_table_running_count = {"var": 0, "argument": 0}

    def start_subroutine(self):
        self.subroutine_table = {}
        self.subroutine_table_running_count = {"var": 0, "argument": 0}
    
    def get_name(self, name, index):
        if name in self.class_table:
            return self.class_table[name][index]
        if name in self.subroutine_table:
            return self.subroutine_table[name][index]
        return None

    def input(self, name, type, kind):
        if kind in ("static", "field"):
            self.class_table[name] = (type, kind, self.class_table_running_count[kind])
            self.class_table_running_count[kind] = self.class_table_running_count[kind] + 1
        else:
            self.subroutine_table[name] = (type, kind, self.subroutine_table_running_count[kind])
            self.subroutine_table_running_count[kind] = self.subroutine_table_running_count[kind] + 1

    def var_count(self, kind):
        if kind in self.subroutine_table_running_count:
            return self.subroutine_table_running_count[kind]
        elif kind in self.class_table_running_count:
            return self.class_table_running_count[kind]

    def kind_of(self, name):
        return self.get_name(name, 1)

    def type_of(self, name):
        return self.get_name(name, 0)

    def index_of(self, name):
        return self.get_name(name, 2)


class VMWriter:
    def __init__(self, file_name):
        self.output = open(file_name, "w")

    def write_push(self, segment, index):
        self.output.write('push {s} {i}'.format(s=segment, i=index))
        self.output.write('\n')

    def write_pop(self, segment, index):
        self.output.write('pop {s} {i}'.format(s=segment, i=index))
        self.output.write('\n')

    def write_call(self, name, nArgs):
        self.output.write('call {n} {a}'.format(n=name, a=nArgs))
        self.output.write('\n')

    def write_function(self, name, nlocals):
        self.output.write('function {n} {a}'.format(n=name, a=nlocals))
        self.output.write('\n')

    def write_arithmetic(self, command):
        self.output.write(command)
        self.output.write('\n')

    def write_label(self, label):
        self.output.write('label {l}'.format(l=label))
        self.output.write('\n')

    def write_goto(self, label):
        self.output.write('goto {l}'.format(l=label))
        self.output.write('\n')

    def write_if(self, label):
        self.output.write('if-goto {l}'.format(l=label))
        self.output.write('\n')

    def write_return(self):
        self.output.write('return')
        self.output.write('\n')

    def close(self):
        self.output.close()


class Compiler:
    def __init__(self, tokenizer, output_file):
        self.token = tokenizer
        self.symbol_table = SymbolTable()
        self.vmwriter = VMWriter(output_file)
        self.ops_stack = Stack()

        #if label
        self.ifid = -1
        #while label
        self.whileid = -1
        self.class_name = None
        self.function_name = None
        self.is_method = False
        self.is_void_function = False
        self.is_constructor = False
        self.no_arguments = 0
        
        
        self.compile_class()
        self.vmwriter.close()

    def getifid(self):
        self.ifid = self.ifid + 1
        return str(self.ifid)

    def getwhileid(self):
        self.whileid = self.whileid + 1
        return str(self.whileid)

    # Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
    def compile_class(self):
        self.process("class")
        self.class_name = self.token.value()
        self.process(None)
        self.process('{')
        self.classvar_dec_opt()
        self.subroutine_dec_opt()
        self.process('}')

    def classvar_dec_opt(self):
        class_var_dec_str = ["static", "field"]
        if self.token.not_empty and self.token.value() in class_var_dec_str:
            self.compile_class_vardec()
            self.classvar_dec_opt()

    def subroutine_dec_opt(self):
        subroutine_dec_str = ["constructor", "function", "method"]
        self.symbol_table.start_subroutine()
        if self.token.not_empty() and self.token.value() in subroutine_dec_str:
            if self.token.value() == "method":
                name = "this"
                type = self.class_name
                kind = "argument"
                self.symbol_table.input(name, type, kind)
                self.is_method = True
                self.is_constructor = False
            elif self.token.value() == "constructor":
                self.is_method = False
                self.is_constructor = True
            else:
                self.is_method = False
                self.is_constructor = False
            self.compile_subroutine()
            self.subroutine_dec_opt()

    # Grammar: ('static' | 'field') type varName (',' varName)* ';'
    def compile_class_vardec(self):
        kind = self.token.value()
        self.process(self.token.value())
        types = ["int", "char", "boolean"]
        type = self.token.value()
        if self.token.not_empty and self.token.value() in types:
            self.process(self.token.value())
        else:
            self.process(None)
        name = self.token.value()
        self.process(None)
        self.symbol_table.input(name, type, kind)
        self.var_name_opt(type, kind)
        self.process(';')

    def var_name_opt(self, type, kind):
        if self.token.not_empty and self.token.value() == ',':
            self.process(',')
            # identifer for varName
            self.symbol_table.input(self.token.value(), type, kind)
            self.process(None)
            self.var_name_opt(type, kind)

    # Grammar: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
    def compile_subroutine(self):
        self.process(self.token.value())
        ret_types = ["int", "char", "boolean", "void"]
        if self.token.value() in ret_types:
            if self.token.value() == "void":
                self.is_void_function = True
            else:
                self.is_void_function = False
            self.process(self.token.value())
        else:
            self.process(None)
            self.is_void_function = False
        self.function_name = self.token.value()
        self.process(None)
        self.process('(')
        self.compile_parameterlist()
        self.process(')')
        self.compile_subroutine_body()
        # reset labels
        self.ifid = -1
        self.whileid = -1

    # Grammar: '{' varDec* statements '}'
    def compile_subroutine_body(self):
        self.process('{')
        self.var_dec_opt()
        nlocals = self.symbol_table.var_count("var")
        self.vmwriter.write_function("{c}.{m}".format(c=self.class_name, m=self.function_name), nlocals)
        if self.is_method:
            self.vmwriter.write_push("argument", 0)
            self.vmwriter.write_pop("pointer", 0)
        if self.is_constructor:
            nfields = self.symbol_table.var_count("field")
            self.vmwriter.write_push("constant", nfields)
            self.vmwriter.write_call("Memory.alloc", 1)
            self.vmwriter.write_pop("pointer", 0)
        self.compile_statements()
        self.process('}')

    def var_dec_opt(self):
        if self.token.not_empty and self.token.value() == "var":
            self.compile_vardec()
            self.var_dec_opt()

    def var_opt(self, type, kind):
        if self.token.not_empty and self.token.value() == ',':
            self.process(',')
            self.symbol_table.input(self.token.value(), type, kind)
            self.process(None)
            self.var_opt(type, kind)

    def typevar_name_opt(self):
        if self.token.not_empty and self.token.value() == ',':
            self.process(',')
            if not self.compile_params():
                raise Exception("Token mismatch")
            self.typevar_name_opt()

    # Grammar: ((type varName) (',' type varName)*)?
    def compile_parameterlist(self):
        if self.compile_params():
            self.typevar_name_opt()

    def compile_params(self):
        check = False
        kind = "argument"
        types = ["int", "char", "boolean"]
        if self.token.not_empty() and self.token.value() in types:
            type = self.token.value()
            self.process(self.token.value())
            name = self.token.value()
            self.process(None)
            check = True
        elif self.token.not_empty() and self.token.token_type() == "identifier":
            type = self.token.value()
            self.process(None)
            name = self.token.value()
            self.process(None)
            check = True
        if check:
            self.symbol_table.input(name, type, kind)
        return check

    # Grammar: 'var' type varName (',' varName)* ';'
    def compile_vardec(self):
        kind = "var"
        self.process("var")
        types = ["int", "char", "boolean"]
        type = self.token.value()
        if self.token.value() in types:
            self.process(self.token.value())
        else:
            # identifer for className
            self.process(None)
        # identifier for varName
        name = self.token.value()
        self.process(None)
        self.symbol_table.input(name, type, kind)
        self.var_opt(type, kind)
        self.process(';')

    # Grammar: letStatement | ifStatement | whileStatement | doStatement | returnStatement
    def compile_statements(self):
        keyword_function_map = {"let": self.compile_let, "if": self.compile_if, "while": self.compile_while, "do": self.compile_do, "return": self.compile_return}
        if self.token.not_empty() and self.token.value() in keyword_function_map:
            keyword_function_map[self.token.value()]()
            # reset
            self.no_arguments = 0
            self.compile_statements()

    # Grammar: 'do' subroutineCall ';'
    def compile_do(self):
        method_call = False
        self.process("do")
        variable = self.token.value()
        self.process(None)
        # dealing with subroutineCall
        if self.token.value() == '(':
            # is direct method call
            method_call = True
            # pushing this to stack
            self.vmwriter.write_push("pointer", 0)
            self.process('(')
            self.compile_expressionlist()
            self.process(')')
            variable = "{c1}{d}{v}".format(c1=self.class_name, d='.', v=variable)
        elif self.token.value() == '.':
            result = self.symbol_table.type_of(variable)
            if result is not None:
                # is a method call using object ref, so first argument is object ref
                method_call = True
                # push object ref to stack
                self.push_pop_variable(variable, True)
                variable = result
            self.process('.')
            variable = "{v1}{d}{v2}".format(v1=variable, d='.', v2=self.token.value())
            self.process(None)
            self.process('(')
            self.compile_expressionlist()
            self.process(')')
        self.process(';')
        if method_call:
            self.no_arguments = self.no_arguments + 1
        self.vmwriter.write_call(variable, self.no_arguments)
        self.vmwriter.write_pop("temp", 0)

    # Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
    def compile_let(self):
        # refers to varName[expression]
        is_array = False
        self.process("let")
        variable = self.token.value()
        self.process(None)
        # refers to array access a[i]
        if self.token.value() == '[':
            is_array = True
            self.process('[')
            self.compile_expression()
            self.process(']')
            self.push_pop_variable(variable, True)
            self.vmwriter.write_arithmetic("add")
        else:
            is_array = False
        self.process('=')
        self.push_ops('(')
        self.compile_expression()
        self.write_ops()
        if not is_array:
            # poping variable from stack
            self.push_pop_variable(variable, False)
        self.process(';')
        if is_array:
            # align the that pointer
            self.vmwriter.write_pop("temp", 0)
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("temp", 0)
            self.vmwriter.write_pop("that", 0)

    # Grammar: 'while' '(' expression ')' '{' statements '}'
    def compile_while(self):
        while_id = self.getwhileid()
        l1 = "WHILE_EXP{u}".format(u=while_id)
        l2 = "WHILE_END{u}".format(u=while_id)
        self.vmwriter.write_label(l1)
        self.process("while")
        self.process('(')
        self.push_ops('(')
        self.compile_expression()
        self.write_ops()
        self.vmwriter.write_arithmetic("not")
        self.vmwriter.write_if(l2)
        self.process(')')
        self.process('{')
        self.compile_statements()
        self.vmwriter.write_goto(l1)
        self.vmwriter.write_label(l2)
        self.process('}')

    # Grammar: 'return' expression? ';'
    def compile_return(self):
        self.process("return")
        self.ops_stack.push('(')
        if self.token.not_empty() and self.token.value() != ';':
            self.compile_expression()
        self.process(';')
        if self.is_void_function:
            self.vmwriter.write_push("constant", 0)
        self.write_ops()
        self.vmwriter.write_return()

    # Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compile_if(self):
        if_id = self.getifid()
        l1 = 'IF_TRUE{u}'.format(u=if_id)
        l2 = 'IF_FALSE{u}'.format(u=if_id)
        l3 = 'IF_END{u}'.format(u=if_id)
        self.process("if")
        self.process('(')
        self.push_ops('(')
        self.compile_expression()
        self.write_ops()
        self.vmwriter.write_if(l1)
        self.vmwriter.write_goto(l2)
        self.vmwriter.write_label(l1)
        self.process(')')
        self.process('{')
        self.compile_statements()
        self.process('}')
        if self.token.not_empty and self.token.value() == "else":
            self.vmwriter.write_goto(l3)
            self.vmwriter.write_label(l2)
            self.process("else")
            self.process('{')
            self.compile_statements()
            self.process('}')
            self.vmwriter.write_label(l3)
        else:
            self.vmwriter.write_label(l2)

    # Grammar: term (op term)*
    def compile_expression(self):
        self.compile_term()
        self.ops_term_opt()

    def ops_term_opt(self):
        if not self.token.not_empty():
            return
        binary_ops = ['+', '-', '~', '=', '<', '>', '&', '|', '/', '*']
        if self.token.value() in binary_ops:
            self.ops_stack.push(self.token.value())
            self.process(self.token.value())
            self.compile_term()
            self.ops_term_opt()

    def push_ops(self, symbol):
        self.ops_stack.push(symbol)

    def write_ops(self):
        ops_map = {'+': "add", '-': "sub", '--': "neg", '~': "not", '=': "eq", '<': "lt", '>': "gt", '&': "and", '|': "or", '/': "Math.divide", '*': "Math.multiply"}
        while not self.ops_stack.is_empty():
            if self.ops_stack.top_element() == '(':
                self.ops_stack.pop()
                break
            if self.ops_stack.top_element() not in ('/', '*'):
                self.vmwriter.write_arithmetic(ops_map[self.ops_stack.pop()])
            else:
                self.vmwriter.write_call(ops_map[self.ops_stack.pop()], 2)

    def eval_array_expressions(self, variable):
        # array access a[i] 
        self.process('[')
        self.push_ops('(')
        self.compile_expression()
        self.process(']')
        self.write_ops()
        self.push_pop_variable(variable, True)
        self.vmwriter.write_arithmetic("add")
        # set the that pointer to base address of a[i]
        self.vmwriter.write_pop("pointer", 1)
        self.vmwriter.write_push("that", 0)

    def eval_subroutines(self):
        self.process('(')
        self.compile_expressionlist()
        self.process(')')

    # Grammar: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall  | unaryOp term
    def compile_term(self):
        if self.token.token_type() == "integerConstant":
            self.vmwriter.write_push("constant", self.token.value())
            self.process(self.token.value())
        elif self.token.token_type() == "stringConstant":
            # need to revisit
            length = len(self.token.value())
            self.vmwriter.write_push("constant", length)
            self.vmwriter.write_call('String.new', 1)
            for s in self.token.value():
                self.vmwriter.write_push("constant", ord(s))
                self.vmwriter.write_call('String.appendChar', 2)
            self.process(self.token.value())
        elif self.token.value() == "true":
            self.vmwriter.write_push("constant", 0)
            self.vmwriter.write_arithmetic("not")
            self.process(self.token.value())
        elif self.token.value() == "false" or self.token.value() == "null":
            self.vmwriter.write_push("constant", 0)
            self.process(self.token.value())
        elif self.token.value() == "this":
            self.vmwriter.write_push("pointer", 0)
            self.process(self.token.value())
        elif self.token.token_type() == "identifier":
            variable = self.token.value()
            self.process(None)
            if self.token.not_empty and self.token.value() == '[':
                self.eval_array_expressions(variable)
            elif self.token.not_empty and self.token.value() == '(':
                self.eval_subroutines()
            elif self.token.not_empty and self.token.value() == '.':
                is_method = False
                self.process('.')
                result = self.symbol_table.type_of(variable)
                if result is not None:
                    is_method = True
                    self.push_pop_variable(variable, True)
                    variable = result
                variable = "{v}{d}{va}".format(v=variable, d='.', va=self.token.value())
                self.process(None)
                self.eval_subroutines()
                if is_method:
                    self.no_arguments = self.no_arguments + 1
                self.vmwriter.write_call(variable, self.no_arguments)
            else:
                # dealing with accessing variables through let statement
                self.push_pop_variable(variable, True)
        elif self.token.value() == '(':
             # dealing with (expression)
            self.process('(')
            self.push_ops('(')
            self.compile_expression()
            self.process(')')
            self.write_ops()
        # dealing with unary ops
        elif self.token.value() == '-':
            self.push_ops('--')
            self.process(self.token.value())
            self.compile_term()
        elif self.token.value() == '~':
            self.push_ops(self.token.value())
            self.process(self.token.value())
            self.compile_term()

    def push_pop_variable(self, variable, push):
        index = self.symbol_table.index_of(variable)
        kind = self.symbol_table.kind_of(variable)
        kind_segment_map = {"field": "this", "static": "static", "var": "local", "argument": "argument"}
        if push:
            self.vmwriter.write_push(kind_segment_map[kind], index)
        else:
            self.vmwriter.write_pop(kind_segment_map[kind], index)

    def setup_compile_expressionstack(self):
        self.push_ops('(')
        self.compile_expression()

    # Grammar: (expression (',' expression)*)?
    def compile_expressionlist(self):
        if self.token.value() != ')':
            self.no_arguments = 1
            self.setup_compile_expressionstack()
            self.expression_opt()

    def expression_opt(self):
        self.write_ops()
        if self.token.not_empty() and self.token.value() == ',':
            self.no_arguments = self.no_arguments + 1
            self.process(',')
            self.setup_compile_expressionstack()
            self.expression_opt()

    def process(self, string):
        if string is None:
            if self.token.token_type() != "identifier":
                raise Exception("Identifier wrong")
        elif self.token.value() != string:
            raise Exception(
                "Actual value {t} does not match Expected {s}".format(t=self.token.value(), s=string))
        if self.token.not_empty():
            self.token.next_input()

path = str(sys.argv[1])
# path = "/Users/zhouyue/Desktop/ZhouYueProject10/Main.jack"
f = open(path, 'r')  
string_code = f.read()

# handle the "/* */" comment
while True:  
    comment_start = string_code.find('/*')
    if comment_start == -1:
        break
    comment_end = string_code.find('*/')
    if comment_end == -1:
        break
    string_code = string_code[:comment_start] + string_code[comment_end + 2:]

# delete // to end of line
f_rows = string_code.split('\n')  
new_code = ''
for rc in f_rows:
    if rc != '':  
        if '//' in rc:
            row = rc
            row = row[:row.find('//')] + '\n'  
        else:
            row = rc +'\n'
        if row in ['\n', '\r\n']:
            continue
        new_code = new_code + row 

file = new_code

if os.path.isfile(path):
    if path.endswith(".jack"):
        jackfile = path.split("/")[-1]
        vm_file = jackfile[0:jackfile.find(".")] + ".vm"
        vm_file = os.path.join(os.path.dirname(path), vm_file)
        tokenizer = Tokenizer(file)
        Compiler(tokenizer, vm_file) 

    else:
        raise Exception("invalid jack file")
else:
    raise Exception("invalid path")