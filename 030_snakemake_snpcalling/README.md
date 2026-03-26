Transformed the 010_manual_snpcall workflow to a snakemake file together with some unit tests

Explaining the tools used for sanity checks:
 - md5sum -c will check on the checksums for each file
 - seqkit stats is a command line that generates summarys for fastq files. It will only work if the file provided follows the specific fastq format
 -vcf-validator is a tool to ensure that vcf files strictly adhere to official specifications
