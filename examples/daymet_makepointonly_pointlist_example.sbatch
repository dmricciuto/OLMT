#!/bin/bash -f
#SBATCH --time 02:00:00
#SBATCH -A ccsi
#SBATCH -p batch
#SBATCH --mem=125G
#SBATCH -N 2
#SBATCH -n 32
#SBATCH --ntasks-per-node 16
#SBATCH --job-name=makepointonly
#SBATCH -o ./%j-output.txt
#SBATCH -e ./%j-error.txt
#SBATCH  --exclusive 

source $MODULESHOME/init/bash
source ~/.bashrc

ZONING_FILE=daymet_elm_mappings.txt

cwd=$(pwd)

# NOTE: if '-np' over 16 per node, may have memory issue??? 

# if extracting user-provided PCT_NAT_PFT data, do as following:
#  --usersurfnc=/nfs/data/ccsi/f9y/GSWP3_daymet/high_res_data/Tesfa_pnnl_PFT_0.05_MODIS_nwh201201.nc \
#  --usersurfvar='PCT_PFT' \

if mpiexec -np 32 python ./makepointdata.py \
  --ccsm_input /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/e3sm_inputdata \
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

