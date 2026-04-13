# Variant Calling and Annotation Pipeline

This Snakemake pipeline automates the process of aligning raw genomic reads, calling Single Nucleotide Polymorphisms (SNPs), filtering/cleaning the variants, and annotating them. The pipeline is designed for robustness, with built-in validation steps at almost every stage to ensure data integrity and catch errors early.

## Overview

The pipeline takes raw `.fastq` files, aligns them to a human reference genome (hg38), calls variants using `bcftools`, cleans the variants using `vt`, and annotates their functional impact using `SnpEff`. The final output is a clean, tab-separated values (TSV) file containing annotated SNP data.

## Dependencies

To run this pipeline, you must have Snakemake installed, along with the following bioinformatics tools available in your system's `PATH`:

- **Standard Linux tools:** `md5sum`, `head`, `grep`, `sed`
- **FastQC:** For quality control of sequencing reads.
- **BWA:** For aligning reads to the reference genome.
- **Samtools:** For sorting, indexing, and validating BAM files.
- **Bcftools:** For variant calling (`mpileup`), generating statistics, and extracting data (`query`).
- **vt:** For variant decomposition, normalization, and filtering.
- **Java:** Required to run SnpEff.
- **SnpEff:** For functional annotation of variants (specifically version 5.4.0a-0 with the `hg38` database).

## Configuration and Input Data

Currently, the configuration is defined directly at the top of the `Snakefile`:

- **SAMPLES**: A list of sample names (e.g., `["TLE66_N", "TLE66_T"]`). The pipeline expects corresponding `{sample}.fastq` files in the working directory.
- **DB**: Path to the reference genome FASTA file (`/staging/leuven/stg_00079/teaching/hg38_9/chr9.fa`). Note: This reference should be indexed for BWA before running the pipeline.
- **SNPEFF_JAR**: Path to the SnpEff Java executable.
- **SnpEff Database**: The pipeline uses a local SnpEff data directory located at `/staging/leuven/stg_00079/teaching/snpeff_db`.
- **Checksums**: The pipeline expects a file named `checksums.md5` in the working directory to verify the integrity of the raw `.fastq` files.

## Pipeline Steps (Rules)

The workflow consists of the following sequential steps, including strict validation checkpoints:

1. **`checksum_fastq`**: Verifies the MD5 checksums of the input FASTQ files.
2. **`validate_fastq`**: Ensures the input files are structurally valid FASTQ files.
3. **`run_fastqc`**: Generates HTML quality control reports for the raw reads.
4. **`align_reads`**: Aligns reads to the reference genome using `bwa mem` and sorts the output into BAM format using `samtools`.
5. **`validate_bam` / `create_index`**: Verifies the BAM files aren't corrupted and creates `.bai` indices.
6. **`snp_calling`**: Uses `bcftools mpileup` and `bcftools call` to identify variants and generate a raw VCF.
7. **`validate_vcf`**: Generates stats on the raw VCF and ensures it is readable.
8. **`snp_cleaning`**: Uses `vt` to decompose multi-allelic variants, normalize indels against the reference, remove duplicates, and filter for Quality > 20.
9. **`validate_clean_vcf`**: Validates the filtered VCF file.
10. **`snp_annotation`**: Annotates the genetic impact of the variants using SnpEff against the `hg38` database.
11. **`validate_annotated_vcf`**: Strict validation step that parses the annotated VCF to ensure SnpEff successfully added the `ANN=` (annotation) field.
12. **`create_annotated_tsv`**: Extracts the Chromosome, Position, Reference allele, Alternate allele, Quality, Annotation, and Genotype into a highly readable final TSV file.

## Usage

To execute the pipeline, navigate to the directory containing the `Snakefile`, the `.fastq` files, and the `checksums.md5` file, then run:

```bash
# Run the pipeline (replace '4' with the number of CPU cores you want to use)
snakemake --cores 4
```
To perform a "dry run" to see which rules will be executed without actually running them:
```bash
snakemake -n
```
## Outputs and Directory Structure

The pipeline generates several directories to keep the workspace organized:

- **validated/**: Contains `.flag` and `.ok` files proving that intermediate validation checks passed.  
- **fastqc_output/**: Contains the `.zip` and `.html` QC reports from FastQC.  
- **bam_output/**: Contains the sorted alignment `.bam` files and their `.bai` indices.  
- **vcf/**: Contains intermediate VCF files (`raw_snps.vcf`, `clean_snps.vcf`, `annotated_snps.vcf`) and their associated stats/reports.  
- **100.final/**: Contains the final output file: `snps.annotated.tsv`.

## Testing Strategy

Each rule in the pipeline was tested individually using the built-in testing utilities provided by :contentReference[oaicite:0]{index=0}. This approach follows the official Snakemake testing framework guidelines to ensure that every step (from FASTQ validation to final annotation) behaves correctly in isolation before integrating into the full workflow.