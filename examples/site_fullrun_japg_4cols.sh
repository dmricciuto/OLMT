#!/bin/sh -f

# Metting from 10/28/2024 
#--metdir /gpfs/wolf2/cades/cli185/proj-shared/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_US-GC03-GRID/cpl_bypass_full \

# Wetland_pftdata => /gpfs/wolf2/cades/cli185/world-shared/e3sm/inputdata/lnd/clm2/PTCLM

### Corresponding elevations for Goodwin Island sites:
      # Upland          = 1.032942653
      # Transition      = 0.790806055
      # Wetland         = 0.679172575
      # Open Water      = 0.000000000

### Input file:

MYROOT=/gpfs/wolf2/cades/cli185/
MYMACH=cades-baseline

nsite_codes="US-TREE,US-TREE,US-TREE,US-TREE"                                           # No space between the variable, the =, and the values inside the " "
# nsite_codes="US-GC4,US-GC4,US-GC4,US-GC4"    
# nsite_codes="US-GC3,US-GC3,US-GC3,US-GC3,US-GC3,US-GC3,US-GC3,US-GC3,US-GC3"        # 9 columns 

# lat_coordinates=(37.219244 37.219244 37.219244 37.219244)           # [japg] => Benchmark Coordinates to test code
lat_coordinates=(37.219244 37.219377 37.218901 37.21806)          # [japg] => Goodwin Island Coordinates
lat_coordinates_str=$(IFS=','; echo "${lat_coordinates[*]}")

# lon_coordinates=(-76.408673 -76.408673 -76.408673 -76.408673)           # [japg] => Benchmark Coordinates to test code
lon_coordinates=(-76.408673 -76.409241 -76.410094 -76.41228)          # [japg] => Goodwin Island Coordinates
lon_coordinates_str=$(IFS=','; echo "${lon_coordinates[*]}")


# Extract first site code for --site argument
IFS=',' read -r first_site_code _ <<< "$nsite_codes"

python ./site_fullrun.py \
      --sitegroup Wetland --caseidprefix test_c4 \
      --nyears_ad_spinup 200 --nyears_final_spinup 400 --tstep 1 \
      --cpl_bypass --machine $MYMACH --compiler gnu --mpilib openmpi \
      --model_root /ccsopen/home/ji8/ELM_4Cols/E3SM_baseline \
      --caseroot /ccsopen/home/ji8/ELM_4Cols/cases \
      --ccsm_input $MYROOT/world-shared/e3sm/inputdata \
      --runroot $MYROOT/scratch/$USER \
      --spinup_vars \
      --np 1 \
      --nyears_transient 176 \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3 --daymet \
      --metdir /gpfs/wolf2/cades/cli185/proj-shared/japg/mymetdir/cpl_bypass_full \
      --tide_components_file /ccsopen/home/ji8/ELM_4Cols/E3SM_baseline/OLMT_coastal/harmonic_Annapolis.csv \
      --tide_forcing_file /ccsopen/home/ji8/ELM_4Cols/OLMT_baseline/Annapolis_elev_sal_35yrs_MSL.nc \
      --parm_file /ccsopen/home/ji8/ELM_4Cols/OLMT_baseline/parm_TREE \
      --parm_file_2nd /ccsopen/home/ji8/ELM_4Cols/OLMT_baseline/parm_short_GC3_12 \
      --site "$first_site_code" \
      --nsite_codes "$nsite_codes" \
      --lat_coordinates "$lat_coordinates_str" \
      --lon_coordinates "$lon_coordinates_str" \
      --nopftdyn \
      #--nopointdata  
      

      

