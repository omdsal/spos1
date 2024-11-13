import os

# Define paths to files for both passes
opfile = os.path.join('.', 'p.py', 'OUTPUT.txt')  # Output file for Pass 2
icfile = os.path.join('.', 'p.py', 'IC.txt')     # Intermediate Code from Pass 1
mdtfile = os.path.join('.', 'p.py', 'MDT.txt')   # Macro Definition Table from Pass 1
mntfile = os.path.join('.', 'p.py', 'MNT.txt')   # Macro Name Table from Pass 1

# Step 1: Macro Pass 1 - Generate MDT, MNT, and IC

# Open the input file (for Pass 1)
input_file = os.path.join('.', 'p.py', 'Input.txt')

# Initialize variables for Pass 1
mnt = open(mntfile, "w")
mdt = open(mdtfile, "w")
ic = open(icfile, "w")
flag = 0
mdpt = 1  # MDT starting index
ala = []
param_no = 1  # Parameter number counter

# Open the input file for reading
with open(input_file, "r") as f:
    file = f.readlines()
    
    # Process each line in the input file
    for line in file:
        line = line.strip()
        
        # If a macro definition starts
        if line == "MACRO":
            flag = 1
        elif line == "MEND":
            mdt.write(line + "\n")  # End of macro definition
            mdpt += 1
            flag = 0
        elif flag == 1:  # Inside macro definition
            mdt.write(line + "\n")
            temp = line.split()
            mnt.write(temp[0] + " " + str(mdpt) + "\n")  # Write macro name and MDT position in MNT
            ala = temp[1].split(",")  # Parameters list
            mdpt += 1
            param_no += len(ala)  # Update parameter count
        elif flag > 1:  # Inside macro body
            temp = line.split()
            part2 = temp[1].split(",")  # Split parameters
            
            mdt.write(temp[0] + " ")
            # Process parameters in the macro body
            for i in part2:
                for j in range(len(ala)):
                    t = ala[j].split("=")
                    if t[0] == i:
                        mdt.write("#" + str(j) + ",")  # Replace parameter with index
            mdt.write("\n")
            mdpt += 1
        else:
            ic.write(line + "\n")  # Write non-macro lines to IC

# Close files after Pass 1
mnt.close()
mdt.close()
ic.close()

print("Macro Pass 1 Processing done. :)")

# Step 2: Macro Pass 2 - Macro Expansion

# Read the intermediate code (IC), MDT, and MNT for Pass 2
with open(icfile, "r") as ic, open(mntfile, "r") as mnt, open(mdtfile, "r") as mdt:
    ic_lines = ic.readlines()
    mnt_lines = mnt.readlines()
    mdt_lines = mdt.readlines()

# Open the output file to write the expanded code
with open(opfile, "w") as output:
    # Iterate over each line in the intermediate code (IC)
    for line in ic_lines:
        flag = 0
        temp = line.strip().split()  # Split the IC line into words
        
        # Check if the current line matches any macro name in the MNT
        for mnt_line in mnt_lines:
            t = mnt_line.strip().split()
            if t[0] == temp[0]:  # Macro call found in IC
                flag = 1
                mdpt = int(t[1])  # Get the starting index for MDT expansion
                break
        
        if flag == 1:  # If a macro call is found
            ala = temp[1].split(",") if len(temp) > 1 else []  # Get arguments passed to the macro
            
            # Collect MDT lines corresponding to the macro definition
            macro_body = []
            for line_idx in range(mdpt, len(mdt_lines)):
                st = mdt_lines[line_idx].strip()
                if st == "MEND":
                    break
                macro_body.append(st)
            
            # Parse the macro definition arguments from the first line in the macro body
            if macro_body:
                mdt_args = macro_body[0].split()[1].split(",")
            
            # Process and expand each line in the macro body
            for item in macro_body:
                instr_parts = item.split()
                if instr_parts[0] != "MEND":  # Don't process MEND, it's just the end of the macro
                    # Replace parameters in the macro instruction
                    instruction = instr_parts[0]
                    operands = instr_parts[1].split(",") if len(instr_parts) > 1 else []
                    expanded_operands = []
                    
                    for op in operands:
                        if op.startswith("#"):  # Parameter placeholder
                            idx = int(op[1:])  # Extract index of the parameter
                            if idx < len(ala):
                                expanded_operands.append(ala[idx])  # Replace with actual argument
                            elif "=" in mdt_args[idx]:  # Default value in MDT
                                expanded_operands.append(mdt_args[idx].split("=")[1])
                        else:
                            expanded_operands.append(op)
                    
                    # Write the expanded instruction to the output file
                    output.write(f"{instruction} {','.join(expanded_operands)}\n")
        else:
            # Write non-macro lines directly to the output
            output.write(line)

print("Macro Pass 2 Processing done. :)")
