#!/usr/bin/env bash
#SBATCH --job-name=cp
#SBATCH --output=/mnt/beegfs/userdata/q_blampey/.jobs_outputs/%j
#SBATCH --mem=16G
#SBATCH --partition=shortq

# Load necessary modules
module purge
module load anaconda3/2020-11

source activate sopa

cd /mnt/beegfs/userdata/q_blampey/sopa_benchmark

DEFAULT_LENGTH=8192
LENGTH=${1:-$DEFAULT_LENGTH}
echo Running with LENGTH=$LENGTH

WIDTH=4000
MODE="sopa"

python -u -m sopa_benchmark.cellpose_run -l $LENGTH -m $MODE -pw $WIDTH