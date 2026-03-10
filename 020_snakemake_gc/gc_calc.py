import sys

input_file = sys.argv[1]
output_file = sys.argv[2]
seq = ""
GC = 0
seq_id = ""
valid_bases = {'A','T','C','G'}
try:
    with open(input_file) as f, open(output_file,'w') as out:
        lines = [line.strip() for line in f.readlines()]
        if lines == []:
            raise ValueError("The file is empty")
        if not lines[0].startswith(">"):
            raise ValueError("File does not start with a FASTA header")
        seq_id = lines[0][1:]
        seq = "".join(lines[1:])
        for base in seq:
            if base not in valid_bases:
                raise ValueError(f"Invalid base found:{base}")
        for n in seq:
            if n == 'C' or n == 'G':
                GC += 1
        try:
            GC = str(GC/len(seq))
        except ZeroDivisionError:
            print("The sequence is empty so its not possible to find the GC%")
        out.write('Sequence_id\tGC_percentage\n')
        out.write(f'{seq_id}\t{GC}\n')
except FileNotFoundError:
    print(FileNotFoundError)
    print("We cannot load the files provided")



    




