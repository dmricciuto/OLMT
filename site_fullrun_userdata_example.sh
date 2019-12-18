#!/bin/sh -f

python ./site_fullrun.py \
      --site AK-K64G --sitegroup NGEEArctic --caseidprefix TestOMLT \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --cpl_bypass --machine mymac --compiler gnu --mpilib mpich --gswp3 \
      --model_root /Users/f9y/mygithub/e3sm \
      --caseroot /Users/f9y/project_acme/cases \
      --ccsm_input /Users/f9y/mygithub/pt-e3sm-inputdata \
      --runroot /Users/f9y/project_acme/scratch \
      --spinup_vars \
      --nopointdata \
      --domainfile /Users/f9y/mygithub/pt-e3sm-inputdata/share/domains/domain.clm/domain.lnd.1x1pt_kougarok-GRID_navy.nc \
      --surffile /Users/f9y/mygithub/pt-e3sm-inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_kougarok-GRID_simyr1850_c360x720_171002.nc \
      --landusefile /Users/f9y/mygithub/pt-e3sm-inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_kougarok-GRID_simyr1850-2015_c180423.nc

