#!/usr/bin/env bash
#SBATCH --job-name=count
#SBATCH --output=/mnt/beegfs/userdata/q_blampey/.jobs_outputs/%j
#SBATCH --mem=32G
#SBATCH --partition=shortq

# Load necessary modules
module purge
module load anaconda3/2020-11

source activate sopa

cd /mnt/beegfs/userdata/q_blampey/sopa_benchmark

LENGTH=8192
MODE="normal"

python -m sopa_benchmark.transcripts_counts -l $LENGTH -m $MODE