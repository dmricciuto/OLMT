#!/bin/sh -f

MYROOT=/home/$USER
MYMACH=docker
MPILIB=openmpi
METDIR=$MYROOT/inputdata
MODEL_ROOT=$MYROOT/models/E3SM_tai

CASES_ROOT=$MYROOT/output/cases
mkdir -p $CASES_ROOT
RUNS_ROOT=$MYROOT/output/scratchs
mkdir -p $RUNS_ROOT

# 3-cols
XCOLS=3
DOMAIN_FILE=$METDIR/share/domains/domain.clm/domain.lnd.3x1pt_US-GC3_navy.nc
SURF_FILE=$METDIR/lnd/clm2/surfdata_map/surfdata_3x1pt_US-GC3_simyr1850.nc

# 4-cols
#XCOLS=4
#DOMAIN_FILE=$METDIR/share/domains/domain.clm/domain.lnd.4x1pt_US-GC3_TEMPEST_navy.nc
#SURF_FILE=$METDIR/lnd/clm2/surfdata_map/surfdata_4x1pt_US-GC3_TEMPEST_simyr1850.nc

OLMT_SRC=${PWD}


python ./site_fullrun.py \
      --site US-GC3 --sitegroup Wetland --caseidprefix xcol3 \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --nyears_transient 165 --tstep 1 \
      --machine $MYMACH --compiler gnu --mpilib $MPILIB \
      --model_root $MODEL_ROOT \
      --caseroot $CASES_ROOT \
      --ccsm_input $METDIR \
      --runroot $RUNS_ROOT \
      --spinup_vars \
      --np 1 \
      --nopointdata --nopftdyn \
      --domainfile $DOMAIN_FILE --surffile $SURF_FILE \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3 --cpl_bypass \
      --metdir $METDIR/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_US-GC03-GRID/cpl_bypass_full \
      --tai_xcols $XCOLS \
      --parm_file $OLMT_SRC/examples/tai_tidedata_examples/parm_GC4_13 \
      --parm_file_2nd $OLMT_SRC/examples/tai_tidedata_examples/parm_short_GC3_12 \
      --tide_components_file $OLMT_SRC/examples/tai_tidedata_examples/harmonic_Annapolis.csv


