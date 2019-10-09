#!/bin/sh -f

python ./site_fullrun.py \
      --site AK-KM64 --sitegroup NGEEArctic --caseidprefix TestOMLT \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --cpl_bypass --machine cades --compiler gnu --mpilib openmpi --gswp3 \
      --model_root /lustre/or-hydra/cades-ccsi/proj-shared/models/e3sm \
      --caseroot /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cases \
      --surfdata_grid \
      --spinup_vars \
      --nopftdyn \
      --np 6 \
      --maxpatch_pft 12 \
      --domainfile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/share/domains/domain.clm/domain.lnd.51x63pt_kougarok-NGEE_TransA_navy.nc \
      --surffile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/surfdata_51x63pt_kougarok-NGEE_TransA_simyr1850_c190604-sub12.nc \
      --mod_parm_file /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/paramdata/clm_params_c180524-sub12.nc
