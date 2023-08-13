#!/bin/sh -f

python ./site_fullrun.py \
      --site US-GC4 --site3rd US-GC3 --sitegroup Wetland --caseidprefix ADDS03 \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --nyears_transient 169 --tstep 1 \
      --cpl_bypass --machine cades --compiler gnu --mpilib openmpi \
      --walltime 9 \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --hist_vars SALINITY \
      --gswp3_w5e5 \
      --model_root /home/whuang611/E3SM_WH \
      --caseroot /home/whuang611/work/cases \
      --ccsm_input /nfs/data/ccsi/proj-shared/E3SM/inputdata \
      --runroot /lustre/or-scratch/cades-ccsi/scratch/whuang611 \
      --spinup_vars \
      --nopftdyn \
      --col3rd \
      --np 1 \
      --tide_forcing_file /home/whuang611/inputs/Annapolis_WT6_1_schism_salinity20172018plus2_35yrs_MSL.nc \
      --tide_components_file /home/whuang611/inputs/harmonic_tides_8575512.csv \
      --parm_file /home/whuang611/inputs/parm_GC4_10 \
      --parm_file_2nd /home/whuang611/inputs/parm_short_GC3_12 \
