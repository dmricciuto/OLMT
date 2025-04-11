#!/bin/sh -f

# Metting from 10/28/2024 
#--metdir /gpfs/wolf2/cades/cli185/proj-shared/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_US-GC03-GRID/cpl_bypass_full \

MYROOT=/gpfs/wolf2/cades/cli185/
MYMACH=cades-baseline

python ./site_fullrun.py \
<<<<<<< HEAD
      --site US-GC3 --sitegroup Wetland --caseidprefix C3s \
=======
      --site US-GC3 --sitegroup Wetland --caseidprefix C3t \
>>>>>>> dc7279889e18311c6c2aa6281eee6e7ae6fc7c12
      --nyears_ad_spinup 20 --nyears_final_spinup 40 --tstep 1 \
      --cpl_bypass --machine $MYMACH --compiler gnu --mpilib openmpi \
      --model_root /ccsopen/home/ji8/E3SM_baseline \
      --caseroot /ccsopen/home/ji8/cases \
      --ccsm_input $MYROOT/world-shared/e3sm/inputdata \
      --runroot $MYROOT/scratch/$USER \
      --spinup_vars \
      --np 1 \
      --nopointdata \
      --col3rd \
      --tide_forcing_file /ccsopen/home/ji8/OLMT_baseline/Annapolis_elev_sal_35yrs_MSL.nc \
      --parm_file /ccsopen/home/ji8/OLMT_baseline/parm_GC4_9 \
      --parm_file_2nd /ccsopen/home/ji8/OLMT_baseline/parm_short_GC3_12 \
      --site3rd US-GC3 \
      --nyears_transient 10 \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3 --daymet \
      --nopftdyn \
      --metdir /gpfs/wolf2/cades/cli185/proj-shared/japg/mymetdir/cpl_bypass_full \
      --tide_components_file /ccsopen/home/ji8/E3SM_baseline/OLMT_coastal/harmonic_Annapolis.csv \
      --number_of_columns 3 
      

      

