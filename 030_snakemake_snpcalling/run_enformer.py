#!/usr/bin/env python3
import sys
import time
import asyncio
import os

# Ensure the course environment can locate fake_enformer if initialized oddly
try:
    from fake_enformer import async_predict
except ImportError:
    print("Error: fake_enformer package not found in current environment.")
    print("Please ensure you are running this within the course conda environment.")
    sys.exit(1)

# ==============================================================================
# APPROACH & RATIONALE (Assignment Grading Requirement)
# ==============================================================================
"""
APPROACH: 
An asynchronous I/O paradigm using Python's native `asyncio` engine coupled with 
`fake_enformer.async_predict`.

RATIONALE:
The computational bottleneck in this pipeline is a simulated network/hardware latency 
(an artificial 5-20 second sleep penalty per call). Since this workload is strictly 
I/O-bound rather than CPU-bound, native cooperative multitasking via async/await allows 
our script to maximize efficiency. Instead of waiting idly for a single response, 
the script yields execution control back to the event loop, spinning up multiple tasks 
concurrently.

OPTIMIZATIONS & SAFEGUARDS:
1. Deduplication (Set Caching): Coordinates are deduplicated in memory prior to calling 
   the engine, completely avoiding repetitive execution lag on duplicate genomic loci.
2. Semaphore Throttle: An asyncio.Semaphore caps concurrent tasks at 30. This fulfills 
   the "considerate neighbor" guideline on shared infrastructure, preventing heavy packet bursts.
3. Variant Filtering: Multi-base structural variants (INDELs) are dynamically isolated 
   and bypassed to conform strictly to the single-character genomic format (A,C,G,T).
"""

async def fetch_score(coordinate, semaphore):
    """Executes a single prediction query bounded by a concurrency semaphore."""
    async with semaphore:
        try:
            score = await async_predict(coordinate)
            return coordinate, score
        except Exception as e:
            return coordinate, f"ERROR: {str(e)}"

def parse_vcf(vcf_path, build="hg38"):
    """Parses VCF line-by-line, filtering and formatting valid SNP coordinates."""
    unique_coordinates = set()
    skipped_indels = 0

    with open(vcf_path, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue
                
            fields = line.strip().split('\t')
            if len(fields) < 5:
                continue
                
            chrom = fields[0]   
            pos = fields[1]     
            ref = fields[3]     
            alt = fields[4]     
            valid_bases = {'A', 'C', 'G', 'T'}
            if len(ref) == 1 and len(alt) == 1 and ref in valid_bases and alt in valid_bases:
                coordinate_string = f"{build}:{chrom}:{pos}:{ref}:{alt}"
                unique_coordinates.add(coordinate_string)
            else:
                skipped_indels += 1

    if skipped_indels > 0:
        print(f"Filtered out {skipped_indels} complex structural variants/INDELs.")
        
    return unique_coordinates

async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_enformer.py <path_to_vcf_file>")
        sys.exit(1)
        
    vcf_input_path = sys.argv[1]
    
    if not os.path.exists(vcf_input_path):
        print(f"Error: The file path '{vcf_input_path}' does not exist.")
        sys.exit(1)
        
    print(f"Analyzing and parsing structural input: {vcf_input_path}")
    coordinates_to_process = parse_vcf(vcf_input_path, build="hg38")
    print(f"Identified {len(coordinates_to_process)} distinct unique SNPs for scoring.")

    if not coordinates_to_process:
        print("No valid single-nucleotide variants found to process.")
        sys.exit(0)

    MAX_CONCURRENT_REQUESTS = 30 
    print(f"Launching concurrency engine (Capped Limit: {MAX_CONCURRENT_REQUESTS} parallel jobs)...")
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    start_wall_time = time.perf_counter()
    
    task_pool = [fetch_score(coord, semaphore) for coord in coordinates_to_process]
    compiled_results = await asyncio.gather(*task_pool)
    
    end_wall_time = time.perf_counter()
    total_execution_duration = end_wall_time - start_wall_time
    
    print("\n" + "="*50)
    print(f"PERFORMANCE PROFILE METRIC:")
    print(f"Successfully evaluated {len(compiled_results)} coordinates.")
    print(f"Total processing execution wall-clock time: {total_execution_duration:.2f} seconds.")
    print("="*50 + "\n")

    output_filename = "enformer_predictions.tsv"
    with open(output_filename, 'w') as output_file:
        output_file.write("coordinate\tscore\n")
        for coordinate, score in compiled_results:
            output_file.write(f"{coordinate}\t{score}\n")
            
    print(f"Output safely written to file path target: {output_filename}")

if __name__ == "__main__":
    asyncio.run(main())