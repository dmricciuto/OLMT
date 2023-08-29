machine=compy
inputdata=/compyfs/inputdata
codedir=~/E3SMv2/code/20221110/

python global_fullrun.py --cpl_bypass --res r05_r05 --machine $machine --use_hydrstress \
	 --lon_bounds 34.75,34.75 --lat_bounds -14.25,-14.25 \
	 --caseidprefix 20230829_phssinglecell \
	 --model_root $codedir \
         --runroot /compyfs/$USER/e3sm_scratch \
         --mod_parm_file $inputdata/lnd/clm2/paramdata/clm_params_c180524_phs.nc \
 	 --metdir $inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716/cpl_bypass_full/ \
         --ccsm_input $inputdata \
	 --project e3sm --np 1 --compiler intel --mpilib impi --gswp3 --tstep 1

