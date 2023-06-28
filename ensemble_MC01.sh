#!/bin/sh -f

python ./site_fullrun.py \
      --site US-GC4 --sitegroup Wetland --caseidprefix EM01 \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --nyears_transient 169 --tstep 1 \
      --cpl_bypass --machine cades --compiler gnu --mpilib mpi-serial \
      --pio_version 2 \
      --walltime 9 \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3_w5e5 \
      --marsh \
      --model_root /home/whf/E3SM/E3SM_Salinity_3rd \
      --caseroot /home/whf/work/cases \
      --ccsm_input /nfs/data/ccsi/proj-shared/E3SM/inputdata \
      --runroot /lustre/or-scratch/cades-ccsi/scratch/whf \
      --spinup_vars \
      --nopftdyn \
      --ng 3 \
      --mc_ensemble 30 \
      --parm_list /home/whf/E3SM/inputs/parm_list_MC1 \
      --parm_file /home/whf/E3SM/inputs/parm_short_GC3_6 \
      --tide_components_file /home/whf/E3SM/inputs/harmonic_tides_8575512.csv \
      --tide_forcing_file /home/whf/E3SM/inputs/Annapolis_elev_sal_35yrs_tides.nc \
