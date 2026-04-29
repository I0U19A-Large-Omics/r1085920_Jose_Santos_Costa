import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns 
import sys
from pathlib import Path

DB = "150.db/snps.sqlite"
def number_of_snps_plot(db,output):
    with sqlite3.connect(db) as conn:
        query = """
        SELECT 
            CALLS.s_name, 
            EFFECTS.mod as impact, 
            COUNT(DISTINCT SNPS.pos) as snp_count
        FROM 
            SNPS
        JOIN 
            EFFECTS ON SNPS.id = EFFECTS.id
        JOIN 
            CALLS ON SNPS.id = CALLS.id
        WHERE 
            CALLS.genotype NOT IN ('0/0', '0|0', '0', './.', '0/.')
        GROUP BY 
            CALLS.s_name, 
            EFFECTS.mod;
        """
        df = pd.read_sql_query(query, conn)

    impact_order = ['HIGH', 'MODERATE', 'LOW', 'MODIFIER']
    df['impact'] = pd.Categorical(df['impact'], categories=impact_order, ordered=True)
    df = df.sort_values('impact')
    name_mapping = {
        'bam_output/TLE66_N.bam': 'Normal',
        'bam_output/TLE66_T.bam': 'Tumour' 
    }
    df['s_name'] = df['s_name'].replace(name_mapping)

    plt.figure(figsize=(8, 6))

    sns.barplot(data=df, x='impact', y='snp_count', hue='s_name', palette='colorblind',legend='auto')

    plt.title('SNP Impact Severity per Sample')
    plt.xlabel('Impact Category')
    plt.ylabel('Number of SNPs')
    plt.ylim(0) 
    plt.legend()

    Path(output).mkdir(exist_ok=True)
    plt.savefig(f"{output}/fig1_impact_severity.svg")
    plt.close()

def snp_quality_scores_plot(db,output):
    with sqlite3.connect(db) as con:
        query = """
        SELECT 
            EFFECTS.mod as impact, 
            SNPS.qual 
        FROM 
            SNPS 
        JOIN 
            EFFECTS ON SNPS.id = EFFECTS.id;
        """
        df = pd.read_sql_query(query,con)
    
    impact_order = ['HIGH', 'MODERATE', 'LOW', 'MODIFIER']
    df['impact'] = pd.Categorical(df['impact'], categories=impact_order, ordered=True)
    df = df.sort_values('impact')

    sns.boxplot(data=df,x='impact',y='qual',palette='colorblind')
    plt.xlabel('Each category of impact')
    plt.ylabel('Quality of each snps')
    plt.title('Distribuition of snp quality scores across impact categories')

    Path(output).mkdir(exist_ok=True)
    plt.savefig(f"{output}/fig2_snp_quality_scores.svg")
    plt.close()


if __name__ == "__main__":
    db = sys.argv[1]
    output = sys.argv[2]
    number_of_snps_plot(db,output)
    snp_quality_scores_plot(db,output)
