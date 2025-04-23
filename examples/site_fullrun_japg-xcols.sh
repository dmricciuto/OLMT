#!/bin/sh -f

# Metting from 10/28/2024 
#MYROOT=/gpfs/wolf2/cades/cli185/
#METDIR=$MYROOT/world-shared/e3sm/inputdata
#MYMACH=cades-baseline
#MPILIB=openmpi

# MYROOT=/Users/f9y
# MYMACH=mymac
# MPILIB=mpich
# METDIR=$MYROOT/mygithub/E3SM_REPOS/pt-e3sm-inputdata
# MODEL_ROOT=$MYROOT/mygithub/E3SM_REPOS/E3SM_ORNL_IM


MYROOT=/gpfs/wolf2/cades/cli185/
MYMACH=cades-baseline
METDIR=$MYROOT/world-shared/e3sm/inputdata
MPILIB=openmpi

# 3-cols
# DOMAIN_FILE=$METDIR/share/domains/domain.clm/domain.lnd.3x1pt_US-GC3_navy.nc
# SURF_FILE=$METDIR/lnd/clm2/surfdata_map/surfdata_3x1pt_US-GC3_simyr1850.nc

# 4-cols
DOMAIN_FILE=/gpfs/wolf2/cades/cli185/proj-shared/pt-e3sm-inputdata/share/domains/domain.clm/domain.lnd.4x1pt_US-GC3_TEMPEST_navy.nc
SURF_FILE=/gpfs/wolf2/cades/cli185/proj-shared/pt-e3sm-inputdata/lnd/clm2/surfdata_map/surfdata_4x1pt_US-GC3_TEMPEST_simyr1850.nc

python ./site_fullrun.py \
      --site US-GC4 --sitegroup Wetland --caseidprefix C4j \
      --nyears_ad_spinup 20 --nyears_final_spinup 40 --nyears_transient 165 --tstep 1 \
      --machine $MYMACH --compiler gnu --mpilib $MPILIB \
      --model_root /ccsopen/home/ji8/ModelELM_japg/E3SM_japg \
      --caseroot /ccsopen/home/ji8/ModelELM_japg/cases \
      --ccsm_input $MYROOT/world-shared/e3sm/inputdata \
      --runroot $MYROOT/scratch/$USER \
      --spinup_vars \
      --np 1 \
      --nopointdata --nopftdyn \
      --domainfile $DOMAIN_FILE --surffile $SURF_FILE \
      --hist_nhtfrq_trans -1 \
      --hist_mfilt_trans 8760 \
      --gswp3 --cpl_bypass \
      --metdir /gpfs/wolf2/cades/cli185/proj-shared/japg/mymetdir/cpl_bypass_full \
      --tai_xcols 4 \
      --parm_file /ccsopen/home/ji8/ModelELM_japg/OLMT/examples/tai_tidedata_examples/parm_GC4_13 \
      --parm_file_2nd /ccsopen/home/ji8/ModelELM_japg/OLMT/examples/tai_tidedata_examples/parm_short_GC3_12 \
      --tide_components_file /ccsopen/home/ji8/ModelELM_japg/OLMT/examples/tai_tidedata_examples/harmonic_Annapolis.csv
      