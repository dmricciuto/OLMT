#!/bin/sh -f

# Metting from 10/28/2024 
#--metdir /gpfs/wolf2/cades/cli185/proj-shared/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_US-GC03-GRID/cpl_bypass_full \

MYROOT=/gpfs/wolf2/cades/cli185/
MYMACH=cades-baseline

nsite_codes="US-GC3,US-GC3,US-GC4,US-GC3"   # No space between the variable, the =, and the values inside the " "

lat_coordinates=(38.874076 38.874473 38.874957)
lat_coordinates_str=$(IFS=','; echo "${lat_coordinates[*]}")

lon_coordinates=(-76.549978 -76.551469 -76.552129)
lon_coordinates_str=$(IFS=','; echo "${lon_coordinates[*]}")

python ./site_fullrun.py \
      --sitegroup Wetland --caseidprefix C4p \
      --nyears_ad_spinup 20 --nyears_final_spinup 40 --tstep 1 \
      --cpl_bypass --machine $MYMACH --compiler gnu --mpilib openmpi \
      --model_root /ccsopen/home/ji8/E3SM_baseline \
      --caseroot /ccsopen/home/ji8/cases \
      --ccsm_input $MYROOT/world-shared/e3sm/inputdata \
      --runroot $MYROOT/scratch/$USER \
      --spinup_vars \
      --np 1 \
      --nyears_transient 10 \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3 --daymet \
      --metdir /gpfs/wolf2/cades/cli185/proj-shared/japg/mymetdir/cpl_bypass_full \
      --tide_components_file /ccsopen/home/ji8/E3SM_baseline/OLMT_coastal/harmonic_Annapolis.csv \
      --tide_forcing_file /ccsopen/home/ji8/OLMT_baseline/Annapolis_elev_sal_35yrs_MSL.nc \
      --parm_file /ccsopen/home/ji8/OLMT_baseline/parm_GC4_9 \
      --parm_file_2nd /ccsopen/home/ji8/OLMT_baseline/parm_short_GC3_12 \
      --col3rd \
      --site3rd US-GC4 \
      --site US-GC3 \
      --nsite_codes "$nsite_codes" \
      --lat_coordinates "$lat_coordinates_str" \
      --lon_coordinates "$lon_coordinates_str"
      #--nopointdata --nopftdyn 
      

      

