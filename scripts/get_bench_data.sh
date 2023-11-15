#!/usr/bin/env bash
#SBATCH --job-name=gen
#SBATCH --output=/mnt/beegfs/userdata/q_blampey/.jobs_outputs/%j
#SBATCH --mem=512G
#SBATCH --partition=mediumq

# Load necessary modules
module purge
module load anaconda3/2020-11

source activate sopa

cd /mnt/beegfs/userdata/q_blampey/sopa_benchmark

python -m sopa_benchmark.get_all_benchmark_data