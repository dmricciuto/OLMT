#!/bin/sh -f

cwd=$(pwd)

cd /tools/OLMT

if python3 ./site_fullrun.py \
      --site AK-K64 --sitegroup NGEEArctic --caseidprefix NGEE \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --machine docker --compiler gnu --mpilib openmpi \
      --model_root /E3SM \
      --ccsm_input /inputdata \
      --caseroot /output \
      --runroot /output \
      --nopointdata \
      --spinup_vars \
      --nopftdyn \
      --np 2 \
      --ppn 2 \
      --maxpatch_pft 12 \
      --cpl_bypass --gswp3 --daymet4 \
      --metdir /inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_kougarok \
      --domainfile /inputdata/share/domains/domain.clm/domain.lnd.51x63pt_kougarok-NGEE_TransA_navy.nc \
      --surffile /inputdata/lnd/clm2/surfdata_map/surfdata_51x63pt_kougarok-NGEE_TransA_simyr1850_c190604-sub12.nc \
      --mod_parm_file /inputdata/lnd/clm2/paramdata/clm_params_c180524-sub12.nc \
      & sleep 10

then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi

cd ${cwd}
