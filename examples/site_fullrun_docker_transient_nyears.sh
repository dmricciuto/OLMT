#!/bin/sh -f

cwd=$(pwd)


# =======================================================================================
# Get the input options from the command line
for i in "$@"
do
case $i in
    -sn=*|--site_name=*)
    site_name="${i#*=}"
    shift # past argument=value
    ;;
    -finit=*|--init_ncfile=*)  # must be full-path and file name
    ncfile_init="${i#*=}"
    shift # past argument=value
    ;;
    -trsy=*|--transient_years=*)
    transient_years="${i#*=}"
    shift # past argument=value
    ;;
    *)
        # unknown option
    ;;
esac
done

# =======================================================================================
# Set defaults and print the selected options back to the screen before running
site_name="${site_name:-kougarok}"
transient_years="${transient_years:-10}"
ncfile_init="${ncfile_init:-/tools/OLMT/examples/site_fullrun_docker_tr_demo_fini.nc}"


# =======================================================================================
# Set site codes for OLMT
if [ ${site_name} = beo ]; then
  site_code="AK-BEOG"
elif [ ${site_name} = council ]; then
  site_code="AK-CLG"
elif [ ${site_name} = kougarok ]; then
  site_code="AK-K64G"
elif [ ${site_name} = teller ]; then
  site_code="AK-TLG"
else
  echo " "
  echo "**** WARNING ****"
  echo "Select a Site Name other than beo, council, kougarok, teller. ELM may not have input data!"
  echo "Make sure you have all data, Otherwise ELM will crash!!!"
  echo " "
fi

# =======================================================================================
# use the system temporary user data folder for editing if any
#mkdir -p $HOME/elm_user_data  # permission issue when access from host
ELM_USER_DATA=/tmp/${site_name}             # this system root tmp folder, accessible across containers/volumes
if [ ! -d ${ELM_USER_DATA} ]; then
  mkdir ${ELM_USER_DATA}
  chmod 777 ${ELM_USER_DATA}
fi
cd ${ELM_USER_DATA}

if [ ${ncfile_init} = /tools/OLMT/examples/site_fullrun_docker_tr_demo_fini.nc ]; then
  if [ ! ${site_name} = kougarok ] ; then
     # this file in OLMT/examples/ is specifically for kougarok site only
     echo " "
     echo "**** EXECUTION HALTED ****"
     echo "NO existed initial restart *.elm.r.????-01-01-00000.nc for transient-only run at Site : ${site_name}"
     exit 0
     echo " "
  fi
fi
cp ${ncfile_init} ${ELM_USER_DATA}/OLMT_${site_code}_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc  # assuming the initial restart file are after 600 years spinup.

# allow user edit ascii files, which either in ascii or 'ncdump' generated from netcdf files
if [ ! -f ${ELM_USER_DATA}/user_nl_elm ]; then
  cp /tools/OLMT/examples/user_nl_elm_example user_nl_elm
fi

if [ ! -f ${ELM_USER_DATA}/domain.txt ]; then
  ncdump /inputdata/share/domains/domain.clm/domain.lnd.1x1pt_${site_name}-GRID_navy.nc>&domain.txt
fi
ncgen -o domain.nc domain.txt

if [ ! -f ${ELM_USER_DATA}/surfdata.txt ]; then
  ncdump /inputdata/lnd/clm2/surfdata_map/surfdata_1x1pt_${site_name}-GRID_simyr1850_c360x720_c171002.nc>&surfdata.txt
fi
ncgen -o surfdata.nc surfdata.txt

if [ ! -f ${ELM_USER_DATA}/surfdata.pftdyn.txt ]; then
  ncdump /inputdata/lnd/clm2/surfdata_map/landuse.timeseries_1x1pt_${site_name}-GRID_simyr1850-2015_c180423.nc>&surfdata.pftdyn.txt
fi
ncgen -o surfdata.pftdyn.nc surfdata.pftdyn.txt


if [ ! -f ${ELM_USER_DATA}/clm_params.txt ]; then
  ncdump /inputdata/lnd/clm2/paramdata/clm_params_c180524.nc>&clm_params.txt
fi
ncgen -o clm_params.nc clm_params.txt

chmod 777 *.txt
chmod 777 *.nc
chmod 777 user_nl_elm

#
cd /tools/OLMT

if python3 ./site_fullrun.py \
      --site ${site_code} --sitegroup NGEEArctic --caseidprefix My \
      --noad --nofnsp --nyears_transient ${transient_years} --tstep 1 \
      --machine docker --compiler gnu --mpilib openmpi \
      --cpl_bypass --gswp3 \
      --model_root /E3SM \
      --caseroot /output \
      --ccsm_input /inputdata \
      --runroot /output \
      --nopointdata \
      --metdir /inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_NGEE-Grid/cpl_bypass_${site_name}-Grid \
      --mod_parm_file $ELM_USER_DATA/clm_params.nc \
      --namelist_file $ELM_USER_DATA/user_nl_elm \
      --domainfile $ELM_USER_DATA/domain.nc \
      --surffile $ELM_USER_DATA/surfdata.nc \
      --landusefile $ELM_USER_DATA/surfdata.pftdyn.nc \
      --finitfile $ELM_USER_DATA/OLMT_${site_code}_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc \
      & sleep 10

then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi

#
cd /output/cime_run_dirs/My_${site_code}_ICB20TRCNPRDCTCBC/run
ncrcat --ovr *.elm.h0.*.nc ELM_output.nc
chmod 777 ELM_output.nc
ncrcat --ovr *.elm.h1.*.nc ELM_output_PFT.nc
chmod 777 ELM_output_PFT.nc

cd ${cwd}


