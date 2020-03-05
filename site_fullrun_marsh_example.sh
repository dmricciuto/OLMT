#!/bin/sh -f

python ./site_fullrun.py \
      --site US-GC3 --sitegroup Wetland --caseidprefix Test2Col \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --cpl_bypass --machine cades --compiler gnu --mpilib openmpi --gswp3 \
      --model_root /lustre/or-hydra/cades-ccsi/f9y/models/E3SM \
      --caseroot /lustre/or-hydra/cades-ccsi/f9y/cases \
      --ccsm_input /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/ACME_inputdata \
      --runroot /lustre/or-hydra/cades-ccsi/scratch/f9y \
      --spinup_vars \
      --marsh \
      --np 2 \
      --nopointdata \
      --domainfile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/share/domains/domain.clm/domain.lnd.2x1pt_US-GC3_navy_vji.nc \
      --surffile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/surfdata_2x1pt_US-GC3_simyr1850.nc \
      --landusefile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/surfdata.pftdyn_2x1pt_US-GC3_simyr1850-2015.nc

