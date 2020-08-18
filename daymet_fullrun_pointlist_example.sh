#!/bin/sh -f

#SBATCH --time 4:00:00
#SBATCH -A ccsi
#SBATCH -p batch
#SBATCH --mem=125G
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --ntasks-per-node 1
#SBATCH --job-name=runwithdaymet
#SBATCH -o ./%j-output.txt
#SBATCH -e ./%j-error.txt
#SBATCH  --exclusive 

source $MODULESHOME/init/bash
source ~/.bashrc

ZONING_FILE=daymet_zone_mappings.txt

cwd=$(pwd)

if python ./global_fullrun.py \
  --caseidprefix Test_daymet --point_list ${ZONING_FILE} \
  --makepointdata_only --point_area_kmxkm 1.0 \
  --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
  --machine cades --compiler gnu --mpilib openmpi \
  --cpl_bypass --spinup_vars \
  --gswp3 \
  --model_root /lustre/or-hydra/cades-ccsi/f9y/models/E3SM \
  --caseroot /lustre/or-hydra/cades-ccsi/f9y/cases &
sleep 10
then
  wait

  echo "DONE making point data for point_list ${ZONING_FILE} !"

else
  exit &?
fi

cd ${cwd}

