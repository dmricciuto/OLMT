#!/bin/sh -f

python ./site_fullrun.py \
      --site AK-K64G --sitegroup NGEEArctic --caseidprefix TestOLMT \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --machine mymac --compiler gnu --mpilib mpich \
      --cpl_bypass --gswp3 \
      --model_root /Users/f9y/mygithub/e3sm \
      --caseroot /Users/f9y/project_acme/cases \
      --ccsm_input /Users/f9y/mygithub/pt-e3sm-inputdata \
      --runroot /Users/f9y/project_acme/scratch \
      --spinup_vars \
      --nopointdata \
      --metdir /Users/f9y/mygithub/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_kougarok-Grid/cpl_bypass_full \
      --domainfile /Users/f9y/mygithub/pt-e3sm-inputdata/share/domains/domain.clm/domain.lnd.1x1pt_kougarok-GRID_navy.nc \
      --surffile /Users/f9y/mygithub/pt-e3sm-inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_kougarok-GRID_simyr1850_c360x720_171002.nc \
      --landusefile /Users/f9y/mygithub/pt-e3sm-inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_kougarok-GRID_simyr1850-2015_c180423.nc

# for grid-cell gswp3 v2 (1901-2014)
#      --cpl_bypass --gswp3 \

# for daymet corrected gswp3 v1 ( 1980 - 2010, CONUS only)
#      --cpl_bypass --gswp3 --daymet \

# for daymet4 corrected gswp3 v2 ( 1980 - 2014, Northern America only, 1km resolution, unstructured-grid)
#      --cpl_bypass --gswp3 --daymet4 \

# user-provided cpl_bypass data
#      --metdir /Users/f9y/mygithub/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3_daymet.1x1pt_kougarok-NGEE/cpl_bypass_full \

# If for ELM after June-2021, turning off 'do_budgets'
#     --no_dobudgets \


