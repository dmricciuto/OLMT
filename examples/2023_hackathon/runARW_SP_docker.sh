#!/bin/bash

export inputdata=/inputdata                                    #location of input data directory
export model_root=/E3SM                                        #location of model code (E3SM directory)
export run_root=/output/cime_run_dirs                          #desired location of model output (scratch)
export case_root=/output/cime_case_dirs                        #directory in which to create cases
export metdir=/inputdata/atm/datm7/cpl_bypass_AmericanRiverWatershed/
export np=4                                                    #Number of processors

cd ../../
python global_fullrun.py --walltime 6 --machine docker --mpilib openmpi --np $np \
	--surffile $inputdata/lnd/clm2/surfdata_map/surfdata_1175x1_sparse_grid_American_230201_update1k.nc \
	--domainfile $inputdata/share/domains/domain.clm/domain_1175x1_sparse_grid_American_230201.nc \
	--ccsm_input $inputdata --caseroot $case_root --model_root $model_root --runroot $run_root \
       	--tstep 1 --gswp3 --daymet4 --metdir $metdir --cpl_bypass --nopftdyn --dailyrunoff \
	--SP --notrans --noad --run_startyear 1945 --nyears_final_spinup 70 \
	--hist_mfilt_spinup 1 --hist_nhtfrq_spinup 0 \
	--caseidprefix 20230403 --project e3sm

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
#--SP           Run in satellite phenology (SP) mode
#--notrans      Do not perform transient simulation
#--noad         Do not ffperform accelerated decomposition spinup
#--run_startyear         Model year to begin simulation
#--nyears_final_spinup   Length of simulation
#--hist_mfilt_spinup     number of output timesteps in the history file
#--hist_nhtfrq_spinup    Frequency of output (0 = monthly, -1 = hourly, -24 = daily)
#--caseidprefix          Identifier used to name the case
