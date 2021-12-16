import sys

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
        return False

input = sys.argv[1]
filename = input.split('.')
output_file = '.'.join(filename[:-1]) + '.asm'

f = open(input, 'r', encoding='ascii')  
lines = [line for line in f.readlines() if line.strip()]  
# remove space on the left
new_lines = []

#remove commentss
for line in lines:
    if line[0:2] == '//':
        continue
    else:
        new_lines.append(line.split('\n')[0])

# push 
def push_write(type, val):
    code = ""
    structure_0 = "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
    structure_1 = "A=D+A\n" + "D=M\n" + structure_0

    if type == "constant":
        code = "@" + val + "\n" + "D=A\n" + structure_0
        # move it to D, load sp, put D onto stack, load stack pointer address into A, increment sp

    elif type == "local": 
        code = "@LCL\n" + "D=M\n" + "@" + val + "\n" + structure_1

    elif type == "argument":
        code = "@ARG\n" + "D=M\n" + "@" + val + "\n" + structure_1

    elif type == "this":
        code = "@THIS\n" + "D=M\n" + "@" + val + "\n" + structure_1

    elif type == "that":
        code = "@THAT\n" + "D=M\n" + "@" + val + "\n" + structure_1

    elif type == "pointer":
        code = "@R3\n" + "D=A\n" + "@" + val + "\n" + structure_1

    elif type == "temp":
        code = "@R5\n" + "D=A\n" + "@" + val + "\n" + structure_1

    elif type == "static":
        code = "@" + '.'.join(filename[:-1]) + "." + val + "\n" + "D=M\n" + structure_0

    return code

# pop 
def pop_write(type, val):
    code = ""
    structure_2 = "D=D+A\n" + "@R13\n" + "M=D\n" + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "A=M\n" + "M=D\n"

    if type == "constant":
        code = "@SP\n" + "M=M-1\n"  

    elif type == "local":
        code = "@LCL\n" + "D=M\n" + "@" + val + "\n" + structure_2

    elif type == "argument":
        code = "@ARG\n" + "D=M\n" + "@" + val + "\n" + structure_2

    elif type == "this":
        code = "@THIS\n" + "D=M\n" + "@" + val + "\n" + structure_2

    elif type == "that":
        code = "@THAT\n" + "D=M\n" + "@" + val + "\n" + structure_2

    elif type == "pointer":
        code = "@R3\n" + "D=A\n" + "@" + val + "\n" + structure_2

    elif type == "temp":
        code = "@R5\n" + "D=A\n" + "@" + val + "\n" + structure_2

    elif type == "static":
        code = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@" + '.'.join(filename[:-1]) + '.' + val + "\n" + "M=D\n"

    return code


def asm_write(line, eq, gt, lt):
    code = ""
    input = line.split(' ')

    # arithmetic operation
    if len(input) == 1:   
        command = input[0]
        if command == 'add':
            code = "@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n" + "M=M+D\n"

        elif command == 'sub': 
            code = "@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n" + "M=M-D\n" 

        elif command == 'neg':  
            code = "@SP\n" + "AM=M-1\n" + "M=-M\n" + "@SP\n" + "M=M+1\n"

        #jump to false if x-y !=0
        elif command == 'eq':  
            code = "@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n" + "D=M-D\n" + '@EQTRUE' + str(eq) + '\n' + 'D;JEQ\n' + "@SP\n" + "A=M-1\n" + "M=0\n" + "@EQEND" + str(eq) + '\n' + "0;JMP\n" + "(EQTRUE" + str(eq) + ")\n" + "@SP\n" + "A=M-1\n" + "M=-1\n" + "(EQEND" + str(eq) + ")\n"
            eq = eq + 1

        elif command == 'gt': 
            code = "@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n" + "D=M-D\n"  + '@GTTRUE' + str(gt) + '\n' + 'D;JGT\n' + "@SP\n" + "A=M-1\n" + "M=0\n" + "@GTEND" + str(gt) + '\n' + "0;JMP\n" + "(GTTRUE" + str(gt) + ")\n" + "@SP\n" + "A=M-1\n" + "M=-1\n"  + "(GTEND" + str(gt) + ")\n"
            gt = gt + 1

        elif command == 'lt':
            code = "@SP\n" + "AM=M-1\n" + "D=M\n" + "A=A-1\n" + "D=M-D\n" + '@LTTRUE' + str(lt) + '\n' + 'D;JLT\n' + "@SP\n" + "A=M-1\n" + "M=0\n" + "@LTEND" + str(lt) + '\n' + "0;JMP\n" + "(LTTRUE" + str(lt) + ")\n" + "@SP\n" + "A=M-1\n" + "M=-1\n" + "(LTEND" + str(lt) + ")\n"
            lt = lt + 1

        elif command == 'and':
            code = "@SP\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + "A=A-1\n" + "M=D&M\n"

        elif command == 'or':
            code = "@SP\n" + "M=M-1\n" + "A=M\n" + "D=M\n" + "A=A-1\n" + "M=M|D\n"

        elif command == 'not':
            code = "@SP\n" + "A=M-1\n"+ "M=!M\n"


    else: 
    # push/pop 
        c_1 = input[0]
        c_2 = input[1]
        c_3 = input[2]

        if c_1 == "push":
            code = push_write(c_2, c_3)
        else:
            code = pop_write(c_2, c_3)

    return code, eq, gt, lt

# translate
n_1 = 0
n_2 = 0
n_3 = 0
output = ''
for line in new_lines:
    output += asm_write(line, n_1, n_2, n_3)[0]
    n_1 = asm_write(line, n_1, n_2, n_3)[1]
    n_2 = asm_write(line, n_1, n_2, n_3)[2]
    n_3 = asm_write(line, n_1, n_2, n_3)[3]

# generate asm file
out_file = open(output_file, 'w')
out_file.write(output)