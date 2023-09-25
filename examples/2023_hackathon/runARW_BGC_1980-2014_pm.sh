#!/bin/bash

export inputdata=/global/cfs/cdirs/e3sm/inputdata              #location of input data directory
export model_root=/pscratch/sd/r/ricciuto/e3sm_scratch/E3SM    #location of model code (E3SM directory)
export run_root=/pscratch/sd/r/ricciuto/e3sm_scratch           #desired location of model output (scratch)
export metdir=$inputdata/atm/datm7/TILES_AmericanRiverWatershed/cpl_bypass_full/

cd ../..
python global_fullrun.py --walltime 6 --machine pm-cpu --mpilib mpich --np 128 \
	--surffile $inputdata/lnd/clm2/surfdata_map/surfdata_1175x1_sparse_grid_American_230201_update1k.nc \
	--domainfile $inputdata/share/domains/domain.clm/domain_1175x1_sparse_grid_American_230201.nc \
	--ccsm_input $inputdata --model_root $model_root --runroot $run_root \
       	--tstep 1 --gswp3 --daymet4 --metdir $metdir --cpl_bypass --nopftdyn --dailyrunoff \
	--noad --nofn --run_startyear 1980 --nyears_transient 35 \
	--finidat /pscratch/sd/r/ricciuto/e3sm_scratch/20230315_hcru_hcru_ICB20TRCNPRDCTCBC/run/20230315_hcru_hcru_ICB20TRCNPRDCTCBC.elm.r.1980-01-01-00000.nc  \
	--caseidprefix 20230403_ini --project e3sm 

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
#--noad         Do not perform accelerated decomposition spinup
#--nofn         Do not perform final spinup
#--run_startyear         Model year to begin simulation
#--nyears_transient      Length of transient simulation
#--finidat               Absolute path of restart file to initialize the simulation
#--caseidprefix          Identifier used to name the case
#--project               Project/allocation to use for this run
