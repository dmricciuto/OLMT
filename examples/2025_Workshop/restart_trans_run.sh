#!/bin/sh -f

cwd=$(pwd)


# =======================================================================================
# Get the input options from the command line
for i in "$@"
do
case $i in
    -prefix=*|--case_prefix=*)
    case_prefix="${i#*=}"
    shift # past argument=value
    ;;
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
case_prefix="${case_prefix:-My}"
site_name="${site_name:-USARM}"
transient_years="${transient_years:-10}"
ncfile_init="${ncfile_init:-/tools/OLMT/examples/2025_Workshop/full_run_US-ARM_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc}"


# =======================================================================================
# Set site codes for OLMT
if [ ${site_name} = USARM ]; then
  site_code="US-ARM"
elif [ ${site_name} = BRSa1 ]; then
  site_code="BR-Sa1"
elif [ ${site_name} = USHa1 ]; then
  site_code="US-Ha1"
elif [ ${site_name} = USSyv ]; then
  site_code="US-Syv"
else 
  echo " "
  echo "**** EXECUTION HALTED ****"
  echo "Please select a Site Name from USARM, BRSa1, USHa1, USSyv"
  exit 0
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

#copy saved resart files: 
# (1)   # copy 'restart' data packages, usually include: *.elm.r.yyyy-mm-dd-todss.nc, *.cpl.r.yyyy-mm-dd-todss.nc
#         *.elm.rh0.yyyy-mm-dd-todss.nc, *.elm.h0.yyyy-mm-dd-todss.nc, 
cp /tools/OLMT/examples/2025_Workshop/full_run_${site_code}*.r.* ${ELM_USER_DATA}/
cp /tools/OLMT/examples/2025_Workshop/full_run_${site_code}*.rh?.* ${ELM_USER_DATA}/
# (2) copy 2 (sometime 3) 'rpointer.*' ascii files, in which initial data files will point to.
cp /tools/OLMT/examples/2025_Workshop/${site_code}_rpointer.lnd ${ELM_USER_DATA}/rpointer.lnd
cp /tools/OLMT/examples/2025_Workshop/${site_code}_rpointer.drv ${ELM_USER_DATA}/rpointer.drv

# in case we still need 'finidat'
cp ${ncfile_init} ${ELM_USER_DATA}/full_run_${site_code}_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc  # assuming the initial restart file are after 600 years spinup.


# allow user edit ascii files, which either in ascii or 'ncdump' generated from netcdf files
if [ ! -f ${ELM_USER_DATA}/user_nl_elm ]; then
  cp /tools/OLMT/examples/user_nl_elm_example user_nl_elm
fi
 
if [ ! -f ${ELM_USER_DATA}/domain.txt ]; then
  ncdump /inputdata/share/domains/domain.clm/domain_${site_code}_simyr1850_c170912.nc>&domain.txt
fi
ncgen -o domain.nc domain.txt

if [ ! -f ${ELM_USER_DATA}/surfdata.txt ]; then
  ncdump /inputdata/lnd/clm2/surfdata_map/surfdata_${site_code}_simyr1850_c170912.nc>&surfdata.txt
fi
ncgen -o surfdata.nc surfdata.txt

#if [ ! -f ${ELM_USER_DATA}/surfdata.pftdyn.txt ]; then
#  ncdump /inputdata/lnd/clm2/surfdata_map/landuse.timeseries_${site_code}_simyr1850_c170912.nc>&surfdata.pftdyn.txt
#fi
#ncgen -o surfdata.pftdyn.nc surfdata.pftdyn.txt

if [ ! -f ${ELM_USER_DATA}/clm_params.txt ]; then
  ncdump /inputdata/lnd/clm2/paramdata/clm_params_c180524.nc>&clm_params.txt
fi
ncgen -o clm_params.nc clm_params.txt

if [ ! -f ${ELM_USER_DATA}/CNP_parameters.txt ]; then
  ncdump /inputdata/lnd/clm2/paramdata/CNP_parameters_c180529.nc>&CNP_parameters.txt
fi
ncgen -o CNP_parameters.nc CNP_parameters.txt

chmod 777 *.txt
chmod 777 *.nc
chmod 777 user_nl_elm

#
cd /tools/OLMT

# setup/build transient case using OLMT, but NO run (--no_submit)
if python3 ./site_fullrun.py \
      --site ${site_code} --sitegroup Workshop --caseidprefix ${case_prefix} \
      --noad --nofnsp --nyears_transient ${transient_years} --tstep 1 \
      --machine docker --compiler gnu --mpilib openmpi \
      --cpl_bypass --gswp3 \
      --model_root /E3SM \
      --caseroot /output \
      --ccsm_input /inputdata \
      --runroot /output \
      --nopointdata \
      --metdir /inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_Workshop/cpl_bypass_${site_code} \
      --namelist_file $ELM_USER_DATA/user_nl_elm \
      --domainfile $ELM_USER_DATA/domain.nc \
      --surffile $ELM_USER_DATA/surfdata.nc \
      --nopftdyn \
      --no_submit \
      & sleep 10

# the following line is needed to insert into above, if run normally
#      --finitfile $ELM_USER_DATA/full_run_${site_code}_ICB1850CNPRDCTCBC.elm.r.0601-01-01-00000.nc \
      
  # access CASE directory to copy 2 parameter files.
  cd /output/cime_case_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC

  # OLMT options '--mod_param_file' not works in this setup (TODO checking).
  cp $ELM_USER_DATA/clm_params.nc \
     /output/cime_run_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC/run

  cp $ELM_USER_DATA/CNP_parameters.nc \
     /output/cime_run_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC/run
    
then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi

# Above OLMT call actually set up a TR20 case, based on its final spinup case
# we need to change that   
cd /output/cime_case_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC
./xmlchange RUN_TYPE=branch 
./xmlchange RUN_REFDIR=$ELM_USER_DATA
./xmlchange RUN_REFCASE=full_run_${site_code}_ICB20TRCNPRDCTCBC
./xmlchange RUN_REFDATE=2000-01-01
./xmlchange GET_REFCASE=TRUE

# submit model run
./case.submit


#
cd /output/cime_run_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC/run
ncrcat --ovr *.elm.h0.*.nc ELM_output.nc
chmod 777 ELM_output.nc
ncrcat --ovr *.elm.h1.*.nc ELM_output_PFT.nc
chmod 777 ELM_output_PFT.nc

cd ${cwd}


