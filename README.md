# Management of Large-Scale Omics Data

**Author:** José Santos Costa

This repository contains assignments and hands-on exercises for the Management of Large-Scale Omics Data course. 

## Project Structure

* **`010_manual_snpcall/`** First hands-on workflow using a Jupyter Notebook to explore manual SNP (Single Nucleotide Polymorphism) calling.
* **`020_snakemake_gc/`** An introductory hands-on assignment using the Snakemake workflow management tool to calculate GC content.
* **`030_snakemake_snpcalling/`** A comprehensive, automated Snakemake pipeline for variant calling. This workflow aligns raw reads, calls SNPs, cleans and annotates the variants (using `bcftools`, `vt`, and `SnpEff`), and loads the final data into an SQLite database.
