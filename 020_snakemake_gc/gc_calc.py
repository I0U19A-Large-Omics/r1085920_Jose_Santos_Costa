import sys

input_file = sys.argv[1]
output_file = sys.argv[2]
seq = ""
GC = 0
seq_id = ""
with open(input_file) as f, open(output_file,'w') as out:
    lines = [line.strip() for line in f.readlines()]
    seq_id = lines[0][1:]
    seq = "".join(lines[1:])
    print(seq)
    for n in seq:
        if n == 'C' or n == 'G':
            GC += 1
    GC = str(GC/len(seq))
    out.write('Sequence_id\tGC_percentage\n')
    out.write(f'{seq_id}\t{GC}\n')


    




