#!/bin/sh -f

python ./global_fullrun.py \
 --caseidprefix TestOMLT6pt --point_list pointlist_example \
 --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
 --machine cades --compiler gnu --mpilib openmpi \
 --cpl_bypass --spinup_vars \
 --gswp3 \
 --model_root /lustre/or-hydra/cades-ccsi/proj-shared/models/e3sm \
 --caseroot /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cases \
 --np 6
