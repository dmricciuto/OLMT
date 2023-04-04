#!/bin/bash

export inputdata=/global/cfs/cdirs/e3sm/inputdata              #location of input data directory
export model_root=/pscratch/sd/r/ricciuto/e3sm_scratch/E3SM    #location of model code (E3SM directory)
export run_root=/pscratch/sd/r/ricciuto/e3sm_scratch           #desired location of model output (scratch)
export metdir=$inputdata/atm/datm7/TILES_AmericanRiverWatershed/cpl_bypass_full/

python global_fullrun.py --walltime 6 --machine pm-cpu --mpilib mpich --np 128 \
	--surffile $inputdata/lnd/clm2/surfdata_map/surfdata_1175x1_sparse_grid_American_230201_update1k.nc \
	--domainfile $inputdata/share/domains/domain.clm/domain_1175x1_sparse_grid_American_230201.nc \
	--ccsm_input $inputdata --model_root $model_root --runroot $run_root \
       	--tstep 1 --gswp3 --daymet4 --metdir $metdir --cpl_bypass --nopftdyn --dailyrunoff \
	--noad --nofn --run_startyear 1980 --nyears_transient 35 \
	--finidat /pscratch/sd/r/ricciuto/e3sm_scratch/20230315_hcru_hcru_ICB20TRCNPRDCTCBC/run/20230315_hcru_hcru_ICB20TRCNPRDCTCBC.elm.r.1970-01-01-00000.nc  \
	--caseidprefix 20230403_ini --exeroot /pscratch/sd/r/ricciuto/e3sm_scratch/hcru_hcru_ICB1850CNRDCTCBC_ad_spinup/bld/
