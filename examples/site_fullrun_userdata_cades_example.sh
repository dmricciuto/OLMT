#!/bin/sh -f

python ./site_fullrun.py \
      --site AK-K64G --sitegroup NGEEArctic --caseidprefix TestOLMT \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --machine cades --compiler gnu --mpilib mpi-serial \
      --cpl_bypass --gswp3 \
      --model_root $HOME/models/E3SM \
      --caseroot /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cases \
      --ccsm_input /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cesminput_ngee \
      --spinup_vars \
      --nopointdata \
      --metdir /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cesminput_ngee/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_kougarok-Grid/cpl_bypass_full \
      --domainfile /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cesminput_ngee/share/domains/domain.clm/domain.lnd.1x1pt_kougarok-GRID_navy.nc \
      --surffile /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/surfdata_1x1pt_kougarok-GRID_simyr1850_c360x720_171002.nc \
      --landusefile /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_kougarok-GRID_simyr1850-2015_c180423.nc

# for grid-cell gswp3 v2 (1901-2014)
#      --cpl_bypass --gswp3 \

# for daymet corrected gswp3 v1 ( 1980 - 2010, CONUS only)
#      --cpl_bypass --gswp3 --daymet \

# for daymet4 corrected gswp3 v2 ( 1980 - 2014, Northern America only, 1km resolution, unstructured-grid)
#      --cpl_bypass --gswp3 --daymet4 \

# user-provided cpl_bypass data
#      --metdir /Users/f9y/mygithub/pt-e3sm-inputdata/atm/datm7/atm_forcing.datm7.GSWP3_daymet.1x1pt_kougarok-NGEE/cpl_bypass_full \
#      --metdir /lustre/or-scratch/cades-ccsi/proj-shared/project_acme/cesminput_ngee/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_kougarok-Grid/cpl_bypass_full \

# If for ELM after June-2021, turning off 'do_budgets'
#     --no_budgets \


