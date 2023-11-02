#!/usr/bin/env bash
#SBATCH --job-name=write
#SBATCH --output=/mnt/beegfs/userdata/q_blampey/.jobs_outputs/%j
#SBATCH --mem=128G
#SBATCH --partition=shortq

# Load necessary modules
module purge
module load anaconda3/2020-11

source activate spatial

cd /mnt/beegfs/userdata/q_blampey/sopa_benchmark

SDATA="/mnt/beegfs/merfish/data/liver/public/patient_1.zarr"
WIDTH=10000
MODE="normal"

python -m sopa_benchmark.image_writing --path $IMAGE -w $WIDTH -m $MODE