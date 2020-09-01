#!/bin/sh -f

python ./global_fullrun.py \
 --caseidprefix TESTdaymet --point_list daymet_zone_mappings.txt \
 --point_area_kmxkm 1.0 \
 --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
 --machine mymac --compiler gnu --mpilib mpich \
 --cpl_bypass --spinup_vars \
 --gswp3 \
 --model_root /Users/f9y/mygithub/E3SM \
 --caseroot /Users/f9y//project_acme/cases \
 --runroot /Users/f9y//project_acme/scratch \
 --ccsm_input /Users/f9y/clm4_5_inputdata \
 --np 1

#### --point_area_kmxkm 1.0 \

