import sys

input = sys.argv[1]
filename = input.split('.')
output = '.'.join(filename[:-1]) + '.hack'  
# catch the output filename

f = open(input, 'r', encoding='ascii')  
lines = [line for line in f.readlines() if line.strip()]  # remove space
new_lines = []
for line in lines:
    new_lines.append(line.split('\n')[0])  
    
symbol = {'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4, 'R0':0, 'R1':1, 
          'R2':2, 'R3':3, 'R4':4, 'R5':5, 'R6':6, 'R7':7, 'R8':8, 'R9':9, 
          'R10':10, 'R11':11, 'R12':12, 'R13':13, 'R14':14, 'R15':15, 
          'SCREEN':16384, 'KBD':24576 }

RAMval = 16

idx = 0
cpy = new_lines.copy()
for line in cpy:
    if line[0] == '(' and line[-1]  == ')':
        symbol[line[1:-1]] = idx   # store code chunk names into table
        cpy.remove(line)  # remove this line
    idx += 1  # and check next line
#print (cpy)

for line in cpy:
    if line[0] == '@' and line[1:].isdigit() == False:
        if line[1:] not in symbol():  # if key not added, add it to table
            symbol[line[1:]] = RAMval 
            RAMval = RAMval + 1

result = []

comp_0 = {'0':'101010', '1': '111111', '-1': '111010', 'D':'001100', 'A':'110000', '!D':'001101', '!A':'110001',
            '-D':'001111', '-A':'110011', 'D+1':'011111', 'A+1':'110111', 'D-1':'001110', 'A-1':'110010',
            'D+A':'000010', 'A+D':'000010', 'D-A':'010011','A-D':'000111', 'D&A':'000000', 'D|A':'010101'}
comp_1 = {'M':'110000', '!M':'110001', '-M':'110011', 'M+1':'110111', 'M-1':'110010', 'D+M':'000010', 'M+D':'000010',
            'D-M':'010011', 'M-D':'000111', 'D&M':'000000', 'D|M':'010101'}
dst = {'null':'000', 'M':'001', 'D':'010', 'MD':'011', 'A':'100', 'AM':'101', 'AD':'110', 'AMD':'111'}

jmp = {'null':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011', 'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'}

for line in cpy:
    a = ''
    comp = ''
    dest = ''
    jump = ''
    if line[0] == '@':   # this is an A-instruction
        instr = line[1:]
        #print (instr)
        if instr.isdigit():  # numerical variables, output 16 bit binary value directly
            # print (bin(int(instr)))
            bin_ins = bin(int(instr))[2:].zfill(16)
            result.append(bin_ins)
        else:   # otherwise search in table and convert
            bin_ins = bin(symbol[instr])[2:].zfill(16)
            result.append(bin_ins)


    elif '=' in line:  # this is a C-instruction
        dest_char = line.split('=')[0]
        # print (dest_char)
        comp_char = line.split('=')[1]
        # print (comp_char)
        if ';' in comp_char:
            jump_char = comp_char.split(';')[1]
            comp_char = comp_char.split(';')[0]
        else:
            jump_char = 'null'
        # print (dest_char, comp_char, jump_char)
        if comp_char in comp_0.keys():
            comp = comp_0[comp_char]
            a = '0'
        elif comp_char in comp_1.keys():
            comp = comp_1[comp_char]
            a = '1'
        # print (a+comp)
        dest = dst[dest_char]
        jump = jmp[jump_char]
        result.append('111' + a + comp + dest + jump)

    elif ';' in line:   # if this is a jump instruction
        dest_char = 'null'  # with no '=', dest will be null
        comp_char = line.split(';')[0]
        jump_char = line.split(';')[1]
        if comp_char in comp_0.keys():
            comp = comp_0[comp_char]
            a = '0'
        elif comp_char in comp_1.keys():
            comp = comp_1[comp_char]
            a = '1'
        dest = dst[dest_char]
        jump = jmp[jump_char]
        result.append('111' + a + comp + dest + jump)


#print(cpy[137])
#print(table['sys.init'])
# print (len(new_lines))
# print(len(new_lines))
# print (len(result))

msg = ""

for item in result:
    msg = msg + item + "\n"  # combine the results into one string

# write string into output.hack
out_file = open(output, 'w')
out_file.write(msg)