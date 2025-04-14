#!/bin/sh -f

# Metting from 10/28/2024 
#MYROOT=/gpfs/wolf2/cades/cli185/
#METDIR=$MYROOT/world-shared/e3sm/inputdata
#MYMACH=cades-baseline
#MPILIB=openmpi

MYROOT=/Users/f9y
MYMACH=mymac
MPILIB=mpich
METDIR=$MYROOT/mygithub/E3SM_REPOS/pt-e3sm-inputdata
MODEL_ROOT=$MYROOT/mygithub/E3SM_REPOS/E3SM_ORNL_IM

# 3-cols
DOMAIN_FILE=$METDIR/share/domains/domain.clm/domain.lnd.3x1pt_US-GC3_navy.nc
SURF_FILE=$METDIR/lnd/clm2/surfdata_map/surfdata_3x1pt_US-GC3_simyr1850.nc

# 4-cols
#DOMAIN_FILE=$METDIR/share/domains/domain.clm/domain.lnd.4x1pt_US-GC3_TEMPEST_navy.nc
#SURF_FILE=$METDIR/lnd/clm2/surfdata_map/surfdata_4x1pt_US-GC3_TEMPEST_simyr1850.nc

OLMT_SRC=/Users/f9y/mygithub/E3SM_REPOS/OLMT


python ./site_fullrun.py \
      --site US-GC4 --sitegroup Wetland --caseidprefix C4p \
      --nyears_ad_spinup 200 --nyears_final_spinup 600 --nyears_transient 165 --tstep 1 \
      --machine $MYMACH --compiler gnu --mpilib $MPILIB \
      --model_root $MODEL_ROOT \
      --caseroot $MYROOT/project_e3sm/cases \
      --ccsm_input $METDIR \
      --runroot $MYROOT/project_e3sm/scratch \
      --spinup_vars \
      --np 1 \
      --nopointdata --nopftdyn \
      --domainfile $DOMAIN_FILE --surffile $SURF_FILE \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3 --cpl_bypass \
      --metdir $METDIR/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_US-GC03-GRID/cpl_bypass_full \
      --tai_xcols 3 \
      --parm_file $OLMT_SRC/examples/tai_tidedata_examples/parm_GC4_13 \
      --parm_file_2nd $OLMT_SRC/examples/tai_tidedata_examples/parm_short_GC3_12 \
      --tide_components_file $OLMT_SRC/examples/tai_tidedata_examples/harmonic_Annapolis.csv


