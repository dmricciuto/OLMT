#!/bin/sh -f

#NOTE that the following diretories are assumed:
#  (1) this script is running under OLMT root directory;
#  (2) E3SM model: $HOME/mygithub/E3SM, cloned from https://github.com/E3SM-Project/E3SM.git,
#       branch: fmyuan/WSL-machine-settings
#  (3) point-mode ELM offline inputdata: $HOME/pt-e3sm-inputdata, cloned from https://github.com/fmyuan/pt-e3sm-inputdata.git
#     Addtionally, after data downloading, there are 3 tarred data files need to be decompressed (otherwise missing input error when running):
#        1 file under lnd/clm2/firedata/; 2 files under atm/datm7/NASA_LIS/
#  (4) Cases, cases/, and Runs, scratch/, root directory: $HOME/project_e3sm/

python ./site_fullrun.py \
      --site AK-K64G --sitegroup NGEEArctic --caseidprefix TestOMLT \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --machine wsl --compiler gnu --mpilib mpich \
      --cpl_bypass --gswp3 \
      --no_budgets \
      --model_root $HOME/mygithub/E3SM \
      --caseroot $HOME/project_e3sm/cases \
      --ccsm_input $HOME/pt-e3sm-inputdata \
      --runroot $HOME/project_e3sm/scratch \
      --spinup_vars \
      --nopointdata \
      --metdir $HOME/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_kougarok-Grid/cpl_bypass_full \
      --domainfile $HOME/pt-e3sm-inputdata/share/domains/domain.clm/domain.lnd.1x1pt_kougarok-GRID_navy.nc \
      --surffile $HOME/pt-e3sm-inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_kougarok-GRID_simyr1850_c360x720_171002.nc \
      --landusefile $HOME/pt-e3sm-inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_kougarok-GRID_simyr1850-2015_c180423.nc

# for grid-cell gswp3 v2 (1901-2014)
#      --cpl_bypass --gswp3 \

# for daymet corrected gswp3 v1 ( 1980 - 2010, CONUS only)
#      --cpl_bypass --gswp3 --daymet \

# for daymet4 corrected gswp3 v2 ( 1980 - 2014, Northern America only, 1km resolution, unstructured-grid)
#      --cpl_bypass --gswp3 --daymet4 \

# user-provided cpl_bypass data
#      --metdir /Users/f9y/mygithub/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3_daymet.1x1pt_kougarok-NGEE/cpl_bypass_full \

# If for ELM after June-2021, turning off 'do_budgets'
#     --no_budgets \


