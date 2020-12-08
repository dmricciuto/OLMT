#!/bin/bash -f

source ~/.bashrc

#ZONING_FILE=zone_mappings.txt
ZONING_FILE=daymet_elm_mappings.txt 

cwd=$(pwd)

if python3 ./makepointdata.py \
  --ccsm_input /Users/f9y/clm4_5_inputdata \
  --keep_duplicates \
  --lat_bounds -999,-999 --lon_bounds -999,-999 \
  --mysimyr 1850 \
  --model ELM \
  --surfdata_grid --res hcru_hcru \
  --point_list ${ZONING_FILE} \
  --usersurfnc=/Users/f9y/clm4_5_inputdata/lnd/clm2/surfdata_map/high_res/Tesfa_pnnl_PFT_0.05_MODIS_nwh201201.nc \
  --usersurfvar='PCT_PFT' \
  --point_area_kmxkm 1.0 & sleep 10

then
  wait

  echo "DONE making point data for point_list ${ZONING_FILE} !"

else
  exit &?
fi

cd ${cwd}

