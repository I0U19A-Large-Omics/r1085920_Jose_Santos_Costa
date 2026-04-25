import vcfpy
import pandas as pd
import sqlite3
import sys
from pathlib import Path

def main(vcf,db):


    snps = []
    effects = []
    calls = []


    reader = vcfpy.Reader.from_path(vcf)

    for snp_id, record in enumerate(reader):
        chrom = record.CHROM
        pos = record.POS
        ref = record.REF
        alt = "".join(alt_aux.value for alt_aux in record.ALT)
        qual = record.QUAL

        snps.append({
            "id":snp_id,
            "chrom":chrom,
            "pos":pos,
            "ref":ref,
            "alt":alt,
            "qual":qual
        })
        # Example ANN format: Allele(T) | Annotation(intron_variant) | Impact(MODIFIER) | GeneName(NIBAN2) | GeneID(NIBAN2) | FeatureType(transcript) | FeatureID(NM_001035534.3) | BioType(protein_coding) | Rank(1/13) | HGVS.c(c.16+106G>A)
        for info in record.INFO['ANN']:
            info_list = info.split('|')
            effects.append({
                "id":snp_id,
                "ann":info_list[1],
                "mod":info_list[2],
                "g_name":info_list[3],
                "g_id":info_list[4]
            })
        
        for call in record.calls:
            calls.append({
                "id":snp_id,
                "s_name":call.sample,
                "genotype":call.data.get('GT')
            })
    
    df_snps = pd.DataFrame(snps)
    df_effects = pd.DataFrame(effects)
    df_calls = pd.DataFrame(calls)
    
    Path.mkdir("150.db",exist_ok=True)
    with sqlite3.connect(db) as con:
        df_snps.to_sql("SNPS",con,if_exists='replace')
        df_effects.to_sql("EFFECTS",con,if_exists='replace')
        df_calls.to_sql("CALLS",con,if_exists='replace')

if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2])





    




   