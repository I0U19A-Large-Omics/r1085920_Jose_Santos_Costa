import sys
import sqlite3
db = sys.argv[1]
con = sqlite3.connect(db)
cur = con.cursor()
print('Total SNPs:', cur.execute('SELECT COUNT(*) FROM SNPS').fetchone()[0])
print('Orphaned Effects:', cur.execute('SELECT COUNT(*) FROM EFFECTS WHERE id NOT IN (SELECT id FROM SNPS)').fetchone()[0])
for row in cur.execute('SELECT genotype, COUNT(*) FROM CALLS GROUP BY genotype').fetchall():
    print('Genotype:', row[0], 'Count:', row[1])
con.close()