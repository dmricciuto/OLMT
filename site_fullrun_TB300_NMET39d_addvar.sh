#!/bin/sh -f

python ./site_fullrun.py \
      --site US-GC4 --site3rd US-GC3 --sitegroup Wetland --caseidprefix NMTB39d \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --nyears_transient 169 --tstep 1 \
      --cpl_bypass --machine cades --compiler gnu --mpilib openmpi \
      --walltime 9 \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3_w5e5 \
      --model_root /home/whf/E3SM/E3SM_Salinity_3rd \
      --caseroot /home/whf/work/cases \
      --ccsm_input /nfs/data/ccsi/proj-shared/E3SM/inputdata \
      --runroot /lustre/or-scratch/cades-ccsi/scratch/whf \
      --spinup_vars \
      --nopftdyn \
      --col3rd \
      --np 1 \
      --tide_forcing_file /home/whf/E3SM/inputs/Annapolis_WT6_1_schism_salinity20172018plus2_35yrs_MSL.nc \
      --tide_components_file /home/whf/E3SM/inputs/harmonic_tides_8575512.csv \
      --parm_file /home/whf/E3SM/inputs/parm_GC4_10 \
      --parm_file_2nd /home/whf/E3SM/inputs/parm_short_GC3_12 \
