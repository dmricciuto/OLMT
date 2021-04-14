#!/bin/sh -f

# PFLOTRAN-ELM coupled source directory, by default taking it from ~/.bashrc (if defined)
CLM_PFLOTRAN_SOURCE_DIR=/lustre/or-hydra/cades-ccsi/proj-shared/models/pflotran-elm-interface/src/pflotran-elm-interface

# (1) for building ELM wiht pflotran library, it's required to provide option '--clmpf_source_dir '
# (2) built ELM from (1) can be either running without activating pflotran, 
#    OR, to run coupled model, provide options '--clmpf_mode' and/or '--clmpf_inputdir', '--clmpf_prefix'.
#        By default, '--clmpf_inputdir' is '$e3sm_inputdata/lnd/clm2/pflotran', and '--clmpf_prefix' is 'pflotran-clm'

python ./site_fullrun.py \
      --site US-GC3 --sitegroup Wetland --caseidprefix TestCoastalPF \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 \
      --cpl_bypass --machine cades --compiler gnu --mpilib openmpi --gswp3 \
      --model_root /lustre/or-hydra/cades-ccsi/proj-shared/models/E3SM-Coastal \
      --caseroot /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cases \
      --ccsm_input /nfs/data/ccsi/proj-shared/E3SM/inputdata \
      --runroot /lustre/or-hydra/cades-ccsi/scratch/f9y \
      --spinup_vars \
      --humhol \
      --clmpf_source_dir $CLM_PFLOTRAN_SOURCE_DIR \
      --clmpf_mode \
      --clmpf_inputdir $CLM_PFLOTRAN_SOURCE_DIR \
      --clmpf_prefix pflotran_clm_c-sgrid-colx15_v3.11 \
      --np 1 \
      --nopointdata \
      --domainfile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/share/domains/domain.clm/domain.lnd.2x1pt_US-GC3_navy_vji.nc \
      --surffile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/surfdata_2x1pt_US-GC3_simyr1850.nc \
      --landusefile /lustre/or-hydra/cades-ccsi/proj-shared/project_acme/cesminput_ngee/lnd/clm2/surfdata_map/surfdata.pftdyn_2x1pt_US-GC3_simyr1850-2015.nc

