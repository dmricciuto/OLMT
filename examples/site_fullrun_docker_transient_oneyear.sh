#!/bin/sh -f

cwd=$(pwd)

# use the system temporary user data folder for editing if any
#mkdir -p $HOME/elm_user_data  # permission issue when access from host
ELM_USER_DATA=/tmp             # this system root tmp folder, accessible across containers/volumes
cd $ELM_USER_DATA

cp /tools/OLMT/examples/site_fullrun_docker_tr_demo_fini.nc /tmp/OLMT_AK-K64G_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc

# allow user edit ascii files, which either in ascii or 'ncdump' generated from netcdf files
if [ ! -f /tmp/user_nl_elm ]; then 
  cp /tools/OLMT/examples/user_nl_elm_example /tmp/user_nl_elm
fi

if [ ! -f /tmp/domain.txt ]; then 
  ncdump /inputdata/share/domains/domain.clm/domain.lnd.1x1pt_kougarok-GRID_navy.nc>&/tmp/domain.txt
fi
ncgen -o domain.nc domain.txt

if [ ! -f /tmp/surfdata.txt ]; then 
  ncdump /inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_kougarok-GRID_simyr1850_c360x720_c171002.nc>&/tmp/surfdata.txt
fi
ncgen -o surfdata.nc surfdata.txt

if [ ! -f /tmp/surfdata.pftdyn.txt ]; then 
  ncdump /inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_kougarok-GRID_simyr1850-2015_c180423.nc>&/tmp/surfdata.pftdyn.txt
fi
ncgen -o surfdata.pftdyn.nc surfdata.pftdyn.txt


if [ ! -f /tmp/clm_params.txt ]; then 
  ncdump /inputdata/lnd/clm2/paramdata/clm_params_c180524.nc>&/tmp/clm_params.txt
fi
ncgen -o clm_params.nc clm_params.txt

chmod 777 /tmp/*.txt
chmod 777 /tmp/*.nc

#
cd /tools/OLMT

if python3 ./site_fullrun.py \
      --site AK-K64G --sitegroup NGEEArctic --caseidprefix My \
      --noad --nofnsp --nyears_transient 1 --tstep 1 \
      --machine docker --compiler gnu --mpilib openmpi \
      --cpl_bypass --gswp3 \
      --model_root /E3SM \
      --caseroot /output \
      --ccsm_input /inputdata \
      --runroot /output \
      --nopointdata \
      --metdir /inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_NGEE-Grid/cpl_bypass_kougarok-Grid \
      --mod_parm_file $ELM_USER_DATA/clm_params.nc \
      --namelist_file $ELM_USER_DATA/user_nl_elm \
      --domainfile $ELM_USER_DATA/domain.nc \
      --surffile $ELM_USER_DATA/surfdata.nc \
      --landusefile $ELM_USER_DATA/surfdata.pftdyn.nc \
      --finitfile $ELM_USER_DATA/OLMT_AK-K64G_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc \
      & sleep 10

then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi

cd ${cwd}


