#!/bin/bash -f
#SBATCH --time 24:00:00
#SBATCH -A ccsi
#SBATCH -p batch
#SBATCH --mem=125G
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --ntasks-per-node 1
#SBATCH --job-name=makepointonly
#SBATCH -o ./%j-output.txt
#SBATCH -e ./%j-error.txt
#SBATCH  --exclusive 

source $MODULESHOME/init/bash
source ~/.bashrc

ZONING_FILE=daymet_zone_mappings.txt

cwd=$(pwd)

if python ./makepointdata.py \
  --ccsm_input /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/ACME_inputdata \
  --keep_duplicates \
  --lat_bounds -999,-999 --lon_bounds -999,-999 \
  --mysimyr 1850 \
  --model ELM \
  --surfdata_grid --res hcru_hcru \
  --point_list ${ZONING_FILE} \
  --point_area_kmxkm 1.0 & sleep 10

then
  wait

  echo "DONE making point data for point_list ${ZONING_FILE} !"

else
  exit &?
fi

cd ${cwd}

