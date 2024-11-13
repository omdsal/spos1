import os

LC = 0
symindex = 0

# Combined all constant definitions
MNEMONICS = {
    'STOP': ('00', 'IS', 0), 'ADD': ('01', 'IS', 2), 'SUB': ('02', 'IS', 2),
    'MUL': ('03', 'IS', 2), 'MOVER': ('04', 'IS', 2), 'MOVEM': ('05', 'IS', 2),
    'COMP': ('06', 'IS', 2), 'BC': ('07', 'IS', 2), 'DIV': ('08', 'IS', 2),
    'READ': ('09', 'IS', 1), 'PRINT': ('10', 'IS', 1), 'LTORG': ('05', 'AD', 0),
    'ORIGIN': ('03', 'AD', 1), 'START': ('01', 'AD', 1), 'EQU': ('04', 'AD', 2),
    'DS': ('01', 'DL', 1), 'DC': ('02', 'DL', 1), 'END': ('AD', 0)
}

REG = {'AREG': 1, 'BREG': 2, 'CREG': 3, 'DREG': 4}
symtab = {}
pooltab = []

# Initialize all files at once
def init_files():
    files = ['inter_code.txt', 'literals.txt', 'tmp.txt', 'machine_code.txt']
    for f in files:
        if os.path.exists(f):
            os.remove(f)
        open(f, 'w').close()

def write_to_file(filename, content):
    with open(filename, 'a') as f:
        f.write(content)
    print(f"Written to {filename}: {content}")  # Debugging line

def process_literal(lit_file, tmp_file):
    global LC
    pool = 0
    z = 0
    
    with open(lit_file, 'r') as lit, open(tmp_file, 'w') as tmp:
        for x in lit:
            if "**" in x:
                pool += 1
                if pool == 1:
                    pooltab.append(z)
                y = x.split()
                tmp.write(f"{y[0]}\t{LC}\n")
                LC += 1
            else:
                tmp.write(x)
            z += 1
    
    # Copy tmp back to lit
    with open(tmp_file, 'r') as tmp, open(lit_file, 'w') as lit:
        lit.write(tmp.read())

def END():
    write_to_file('inter_code.txt', "\t(AD,02)\n")
    process_literal('literals.txt', 'tmp.txt')

def LTORG():
    global LC
    with open('literals.txt', 'r') as lit:
        lines = lit.readlines()
    
    with open('inter_code.txt', 'a') as ifp, open('tmp.txt', 'w') as tmp:
        pool = 0
        z = 0
        for line in lines:
            if "**" in line:
                pool += 1
                if pool == 1:
                    pooltab.append(z)
                value = line.split("'")[1]
                ifp.write(f"\t(AD,05)\t(DL,02)(C,{value})\n")
                tmp.write(f"{line.split()[0]}\t{LC}\n")
                LC += 1
            else:
                tmp.write(line)
            z += 1
    
    with open('tmp.txt', 'r') as tmp, open('literals.txt', 'w') as lit:
        lit.write(tmp.read())

def ORIGIN(addr):
    global LC
    write_to_file('inter_code.txt', f"\t(AD,03)\t(C,{addr})\n")
    LC = int(addr)

def DS(size):
    global LC
    write_to_file('inter_code.txt', f"\t(DL,01)\t(C,{size})\n")
    LC += int(size)

def DC(value):
    global LC
    write_to_file('inter_code.txt', f"\t(DL,02)\t(C,{value})\n")
    LC += 1

def OTHERS(mnemonic, words, k):
    global LC, symindex
    z = MNEMONICS[mnemonic]
    output = [f"\t({z[1]},{z[0]})\t"]
    
    for i in range(1, z[2] + 1):
        operand = words[k + i].replace(",", "")
        if operand in REG:
            output.append(f"(RG,{REG[operand]})")
        elif "=" in operand:
            write_to_file('literals.txt', f"{operand}\t**\n")
            with open('literals.txt', 'r') as f:
                output.append(f"(L,{len(f.readlines())})")
        else:
            if operand not in symtab:
                symtab[operand] = ("**", symindex)
                output.append(f"(S,{symindex})")
                symindex += 1
            else:
                w = symtab[operand]
                output.append(f"(S,{w[1]})")
    
    write_to_file('inter_code.txt', ''.join(output) + '\n')
    LC += 1

def detect_mn(words, k):
    global LC
    
    if words[k] == 'START':
        LC = int(words[1])
        write_to_file('inter_code.txt', f"\t(AD,01)\t(C,{LC})\n")
    elif words[k] == 'END':
        END()
    elif words[k] == "LTORG":
        LTORG()
    elif words[k] == "ORIGIN":
        ORIGIN(words[k+1])
    elif words[k] == "DS":
        DS(words[k+1])
    elif words[k] == "DC":
        DC(words[k+1])
    else:
        OTHERS(words[k], words, k)

# Generate Machine Code from Intermediate Code
def generate_machine_code():
    with open('inter_code.txt', 'r') as file:
        lines = file.readlines()

    machine_code = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Handle machine code generation
        parts = line.split("\t")
        instruction = parts[0]
        operands = parts[1:] if len(parts) > 1 else []
        
        # Machine code formatting based on instruction type
        if instruction.startswith('('):
            parts = instruction[1:-1].split(",")
            if len(parts) == 2:
                code, value = parts
                machine_code.append(f"{code} {value}")
            elif len(parts) == 3:
                code, reg, value = parts
                machine_code.append(f"{code} {reg} {value}")
        else:
            machine_code.append(line)
    
    # Write to machine_code.txt
    with open('machine_code.txt', 'w') as f:
        for line in machine_code:
            f.write(line + '\n')

    print("Machine code generated.")

def main():
    global LC, symindex  # Added global declaration here
    init_files()
    
    try:
        with open("input.txt") as file:
            for line in file:
                words = line.split()
                if not words:
                    continue
                
                if LC > 0:
                    write_to_file('inter_code.txt', str(LC))
                
                k = 0
                if words[0] in MNEMONICS:
                    detect_mn(words, k)
                else:
                    if words[k] not in symtab:
                        symtab[words[k]] = (LC, symindex)
                        symindex += 1
                    else:
                        x = symtab[words[k]]
                        if x[0] == "**":
                            symtab[words[k]] = (LC, x[1])
                    detect_mn(words, 1)

        # Generate the machine code from the intermediate code
        generate_machine_code()

        # Write final output files
        with open("SymTab.txt", 'w') as sym:
            for x in symtab:
                sym.write(f"{x}\t{str(symtab[x][0])}\n")
        
        with open("PoolTab.txt", 'w') as pool:
            for x in pooltab:
                pool.write(f"{str(x)}\n")
        
        if os.path.exists("tmp.txt"):
            os.remove("tmp.txt")
    
    except FileNotFoundError:
        print("Error: input.txt not found.")

if __name__ == "__main__":
    main()
