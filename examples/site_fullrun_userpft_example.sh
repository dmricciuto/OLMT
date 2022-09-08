#!/bin/sh -f

cwd=$(pwd)
OLMT_DIR=/Users/f9y/mygithub/OLMT

cd ${OLMT_DIR}

if python ./site_fullrun.py \
      --site AK-K64 --sitegroup NGEEArctic --caseidprefix TestOMLT \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --machine mymac --compiler gnu --mpilib openmpi \
      --cpl_bypass --gswp3 --daymet4 \
      --model_root /Users/f9y/mygithub/E3SM \
      --caseroot /Users/f9y/project_acme/cases \
      --runroot /Users/f9y/project_acme/scratch \
      --ccsm_input /Users/f9y/mygithub/pt-e3sm-inputdata \
      --spinup_vars \
      --nopointdata \
      --nopftdyn \
      --np 2 \
      --maxpatch_pft 12 \
      --metdir /Users/f9y/mygithub/pt-e3sm-inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_kougarok \
      --domainfile /Users/f9y/mygithub/pt-e3sm-inputdata/share/domains/domain.clm/domain.lnd.51x63pt_kougarok-NGEE_TransA_navy.nc \
      --surffile /Users/f9y/mygithub/pt-e3sm-inputdata/lnd/clm2/surfdata_map/surfdata_51x63pt_kougarok-NGEE_TransA_simyr1850_c190604-sub12.nc \
      --mod_parm_file /Users/f9y/mygithub/pt-e3sm-inputdata/lnd/clm2/paramdata/clm_params_c180524-sub12.nc \
      & sleep 10

then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi

cd ${cwd}


