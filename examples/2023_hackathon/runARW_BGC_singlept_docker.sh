#!/bin/bash

export inputdata=/inputdata                                    #location of input data directory
export model_root=/E3SM                                   #location of model code (E3SM directory)
export run_root=/output/cime_run_dirs                          #desired location of model output (scratch)
export case_root=/output/cime_case_dirs                        #Location of model case directories
export np=1                                                    #Number of processors
export metdir=$inputdata/atm/datm7/cpl_bypass_AmericanRiverWatershed/

#Create single point surface and domain files using the first gridcell index (index can be changed if desired)
ncks -d gridcell,0,0 $inputdata/lnd/clm2/surfdata_map/surfdata_1175x1_sparse_grid_American_230201_update1k.nc surfdata_1pttest.nc
ncks -d ni,0,0 $inputdata/share/domains/domain.clm/domain_1175x1_sparse_grid_American_230201.nc domaindata_1pttest.nc

cd ../..
#Now we can change the surface and domain files to run only this point. Because this is much faster, we will do the entire 
#simulation (ad_spinup, spinup and transient).  No initial file is used.
python global_fullrun.py --walltime 6 --machine docker --mpilib openmpi --np $np \
	--surffile /tools/OLMT/examples/2023_hackathon/surfdata_1pttest.nc \
	--domainfile /tools/OLMT/examples/2023_hackathon/domaindata_1pttest.nc \
	--ccsm_input $inputdata --caseroot $case_root --model_root $model_root --runroot $run_root \
       	--tstep 1 --gswp3 --daymet4 --metdir $metdir --cpl_bypass --nopftdyn --dailyrunoff \
	--nyears_ad_spinup 200 --nyears_final_spinup 200 --srcmods_loc /tools/OLMT/examples/2023_hackathon/srcmods \
	--caseidprefix $(date '+%Y%m%d')1pt

#Explanation of options:
#--walltime     Walltime in hours to assign to this job
#--machine      Machine to run on
#--mpilib       Mpi library to use
#--np           Number of processors for this job
#--surffile     Surface data file to use (contains PFT, soil info, etc.)
#--domainfile   Domain file defining region to use
#--tstep 1      Model timestep in hours
#--gswp3        Use GSWP3 reanalysis meteorological forcing data
#--daymet4      Use Daymet reanalysis (uses gswp3 for temporal downscaling)
#--metdir       Directory containing meteorological forcing (if non-default location)
#--cpl_bypass   Use couplee bypass enabled version of ELM (avoids using DATM)
#--nopftdyn     Don't use dynamic PFT information
#--dailyrunoff  Add an h1 history file containing daily outputs associated with runoff
#--nyears_ad_spinup      Length of accelerated decomposition spinup phase
#--nyears_final_spinup   Length of final spinup phase
#--caseidprefix          Identifier used to name the case
