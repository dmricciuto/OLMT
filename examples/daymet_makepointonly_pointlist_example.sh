#!/bin/bash -f

source ~/.zshrc_gnu

#ZONING_FILE=zone_mappings.txt
ZONING_FILE=daymet_elm_mappings.txt 

cwd=$(pwd)

if mpirun -np 1 python3 ../makepointdata.py \
  --ccsm_input /Users/f9y/e3sm_inputdata \
  --keep_duplicates \
  --lat_bounds -999,-999 --lon_bounds -999,-999 \
  --mysimyr 1850 \
  --model ELM \
  --surfdata_grid --res hcru_hcru \
  --point_list ${ZONING_FILE} \
  --usersurfnc=/Users/f9y/e3sm_inputdata/lnd/clm2/surfdata_map/high_res/surfdata_urb_lake_glacier_avedtb_natpft_0.05x0.05_nwh.c20220725.nc \
  --usersurfvar='PCT_URBAN,PCT_GLACIER,PCT_LAKE,aveDTB,PCT_NAT_PFT' \
  --nco_path='/usr/local/gcc-x/nco_pacakge/nco-5.2.x/bin' \
  --point_area_kmxkm 1.0 & sleep 10


#  --usersurfnc=/Users/f9y/e3sm_inputdata/lnd/clm2/surfdata_map/high_res/surfdata_urb_lake_glacier_avedtb_natpft_0.05x0.05_nwh.c20220725.nc \
#  --usersurfvar='PCT_URBAN,PCT_LAKE,aveDTB,PCT_PFT' 
#  --usersurfnc=/Users/f9y/e3sm_inputdata/lnd/clm2/surfdata_map/high_res/Tesfa_pnnl_PFT_0.05_MODIS_nwh201201.nc \
#  --usersurfvar='PCT_PFT' \


then
  wait

  echo "DONE making point data for point_list ${ZONING_FILE} !"

else
  exit &?
fi

cd ${cwd}

