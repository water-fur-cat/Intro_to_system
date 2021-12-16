import sys
import os

keyletter = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 
            'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbols = ['(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*', '/', '&', '|', '~', '<', '>']

# generate xml files
def construct_xml(file_name, tokenizer):
    file = open(file_name, "w")
    file.write('<tokens>')
    file.write('\n')
    while tokenizer.not_empty():
        file.write('<{t}>'.format(t=tokenizer.token_type()))
        file.write(tokenizer.value())
        file.write('</{t}>'.format(t=tokenizer.token_type()))
        file.write('\n')
        tokenizer.next_input()
    file.write('</tokens>')

# a stack
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
        index1 = self.file.find('"')
        if index1 == -1: 
            return self.file.split()
        else:
            index2 = self.file.find('"', index1 + 1)
            while index1 != -1:
                indices.append((index1, index2))
                index1 = self.file.find('"', index2 + 1)
                index2 = self.file.find('"', index1 + 1)
                if index2 == -1:
                    index1 = -1
            letter = []
            start_index = 0
            for (start, end) in indices:
                letter += self.file[start_index:start].split()
                letter.append(self.file[start:end + 1])
                start_index = end + 1
            letter += self.file[start_index:].split()
        return letter

    def not_empty(self):
        return not self.stack.is_empty()

    def next_input(self):
        self.stack.pop()
    
    def keyword(self):
        if self.stack.top_element() in keyletter:
            return self.stack.top_element()

    def symbol(self):
        if self.stack.top_element() in symbols:
            if self.stack.top_element() == '<':
                return "&lt;"
            if self.stack.top_element() == '>':
                return "&gt;"
            if self.stack.top_element() == '&':
                return "&amp;"
            return self.stack.top_element()

    def identifier(self):
        return self.stack.top_element()

    def int_val(self):
        return self.stack.top_element()

    def string_val(self):
        return self.stack.top_element().strip('"')

    def value(self):
        dic = {"keyword": self.keyword, "symbol": self.symbol, "identifier": self.identifier, "stringConstant": self.string_val,
               "integerConstant": self.int_val}
        return dic[self.token_type()]()

    def token_type(self):
        type_token = None 
        while not type_token:
            value = self.stack.top_element()
            if value in keyletter:
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
        for symbol in symbols:
            if symbol in string:
                index = string.find(symbol)
                if index == 0:
                    s1 = string[0]
                    s2 = string[1:]
                elif index == len(string) - 1:
                    s1 = string[0:len(string) - 1]
                    s2 = string[-1]
                else:
                    s1 = string[0:index]
                    s2 = string[index:]
                self.stack.pop()
                self.stack.push(s2)
                self.stack.push(s1)
                return True
        return False


path = str(sys.argv[1])
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
        tokenizerfile = jackfile[0:jackfile.find(".")] + "T.xml"
        tokenizerfile = os.path.join(os.path.dirname(path), tokenizerfile)
        tokenizer = Tokenizer(file)
        construct_xml(tokenizerfile, tokenizer)
    else:
        raise Exception("invalid jack file")
else:
    raise Exception("invalid path")