#!/usr/bin/env bash
#SBATCH --job-name=baysor
#SBATCH --output=/mnt/beegfs/userdata/q_blampey/.jobs_outputs/%j
#SBATCH --mem=16G
#SBATCH --partition=shortq

# Load necessary modules
module purge

DEFAULT_LENGTH=8192
LENGTH=${1:-$DEFAULT_LENGTH}
echo Running with LENGTH=$LENGTH

WIDTH=9000

cd /mnt/beegfs/userdata/q_blampey/sopa_benchmark/data/baysor_dirs/sopa_${LENGTH}_$WIDTH/0

time /mnt/beegfs/merfish/bin/baysor/bin/baysor run --save-polygons GeoJSON -c config.toml transcripts.csv