#!/bin/sh
# =======================================================================================
# Setup and run an ELM OLMT simulation for a FLUXNET site
#
#
# availible site names: USARM, BRSa1, USHa1, USSyv
# =======================================================================================

cwd=$(pwd)
cd /tools/OLMT

# =======================================================================================
# Get the input options from the command line
for i in "$@"
do
case $i in
    -sn=*|--site_name=*)
    site_name="${i#*=}"
    shift # past argument=value
    ;;
    -sg=*|--site_group=*)
    site_group="${i#*=}"
    shift # past argument=value
    ;;
    -cp=*|--case_prefix=*)
    case_prefix="${i#*=}"
    shift # past argument=value
    ;;
    -adsy=*|--ad_spinup_years=*)
    ad_spinup_years="${i#*=}"
    shift # past argument=value
    ;;
    -fsy=*|--final_spinup_years=*)
    final_spinup_years="${i#*=}"
    shift # past argument=value
    ;;
    -trsy=*|--transient_years=*)
    transient_years="${i#*=}"
    shift # past argument=value
    ;;
    -tsp=*|--timestep=*)
    timestep="${i#*=}"
    shift # past argument=value
    ;;
    -addt=*|--add_temperature=*)
    add_temperature="${i#*=}"
    shift # past argument=value
    ;;
    -sdaddt=*|--startdate_add_temperature=*)
    startdate_add_temperature="${i#*=}"
    shift # past argument=value
    ;;    
    -addco2=*|--add_co2=*)
    add_co2="${i#*=}"
    shift # past argument=value
    ;;
    -sdaddco2=*|--startdate_add_co2=*)
    startdate_add_co2="${i#*=}"
    shift # past argument=value
    ;;    
    -sclr=*|--scale_rain=*)
    scale_rain="${i#*=}"
    shift # past argument=value
    ;;
    -sdsclr=*|--startdate_scale_rain=*)
    startdate_scale_rain="${i#*=}"
    shift # past argument=value
    ;;    
    -scls=*|--scale_snow=*)
    scale_snow="${i#*=}"
    shift # past argument=value
    ;;
    -sdscls=*|--startdate_scale_snow=*)
    startdate_scale_snow="${i#*=}"
    shift # past argument=value
    ;;
    -scln=*|--scale_ndep=*)
    scale_ndep="${i#*=}"
    shift # past argument=value
    ;;
    -sdscln=*|--startdate_scale_ndep=*)
    startdate_scale_ndep="${i#*=}"
    shift # past argument=value
    ;;
    -sclp=*|--scale_pdep=*)
    scale_pdep="${i#*=}"
    shift # past argument=value
    ;;
    -sdsclp=*|--startdate_scale_pdep=*)
    startdate_scale_pdep="${i#*=}"
    shift # past argument=value
    ;;
    *)
        # unknown option
    ;;
esac
done
# =======================================================================================

# =======================================================================================
# Set defaults and print the selected options back to the screen before running
site_name="${site_name:-USARM}"
site_group="${site_group:-Workshop}"
case_prefix="${case_prefix:-OLMT}"
ad_spinup_years="${ad_spinup_years:-200}"
final_spinup_years="${final_spinup_years:-600}"
transient_years="${transient_years:--1}"
# -1 is the default to run all years from 1850
timestep="${timestep:-1}"
# temp and co2 additions:
add_temperature="${add_temperature:-0.0}"
add_co2="${add_co2:-0.0}"
startdate_add_temperature="${startdate_add_temperature:-99991231}"
startdate_add_co2="${startdate_add_co2:-99991231}"
# precipitation scaling defaults
scale_rain="${scale_rain:-1.0}"
scale_snow="${scale_snow:-1.0}"
startdate_scale_rain="${startdate_scale_rain:-99991231}"
startdate_scale_snow="${startdate_scale_snow:-99991231}"
# N/P dep scaling
scale_ndep="${scale_ndep:-1.0}"
startdate_scale_ndep="${startdate_scale_ndep:-99991231}"
scale_pdep="${scale_pdep:-1.0}"
startdate_scale_pdep="${startdate_scale_pdep:-99991231}"

# print back selected or set options to the user
echo " "
echo " "
echo "*************************** OLMT run options ***************************"
echo "Site Name = ${site_name}"
echo "Site Group = ${site_group}"
echo "Case Prefix = ${case_prefix}"
echo "Number of AD Spinup Simulation Years = ${ad_spinup_years}"
echo "Number of Final Spinup Simulation Years = ${final_spinup_years}"
echo "Number of Transient Simulation Years = ${transient_years}"
echo "Model Timestep = ${timestep}"
if [ ${add_temperature} != 0.0 ]; then
  echo "Adding ${add_temperature} degreesC to forcing temperature starting on ${startdate_add_temperature}"
  scaling_args="--add_temperature ${add_temperature} --startdate_add_temperature ${startdate_add_temperature}"
fi
if [ ${add_co2} != 0.0 ]; then
  echo "Adding ${add_co2} ppm to forcing CO2 starting on ${startdate_add_co2}"
  scaling_args="$scaling_args --add_co2 ${add_co2} --startdate_add_co2 ${startdate_add_co2}"
fi
if [ ${scale_rain} != 1.0 ]; then
  echo "Forcing rainfall scaled by factor of ${scale_rain} starting on ${startdate_scale_rain}"
  scaling_args="$scaling_args --scale_rain ${scale_rain} --startdate_scale_rain ${startdate_scale_rain}"
fi
if [ ${scale_snow} != 1.0 ]; then
  echo "Forcing snowfall scaled by factor of ${scale_snow} starting on ${startdate_scale_snow}"
  scaling_args="$scaling_args  --scale_snow ${scale_snow} --startdate_scale_snow ${startdate_scale_snow}"
fi
if [ ${scale_ndep} != 1.0 ]; then
  echo "N deposition scaled by factor of ${scale_ndep} starting on ${startdate_scale_ndep}"
  scaling_args="$scaling_args --scale_ndep ${scale_ndep} --startdate_scale_ndep ${startdate_scale_ndep}"
fi 
if [ ${scale_pdep} != 1.0 ]; then
  echo "P deposition scaled by factor of ${scale_pdep} starting on ${startdate_scale_pdep}"
  scaling_args="$scaling_args --scale_pdep ${scale_pdep} --startdate_scale_pdep ${startdate_scale_pdep}"
fi
if [ ${transient_years} != -1 ]; then
  sim_years="--nyears_ad_spinup ${ad_spinup_years} --nyears_final_spinup ${final_spinup_years} \
  --nyears_transient ${transient_years}"
else
  sim_years="--nyears_ad_spinup ${ad_spinup_years} --nyears_final_spinup ${final_spinup_years}"
fi
echo " "
# =======================================================================================

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
echo "OLMT Site Code: ${site_code}"
# =======================================================================================

# =======================================================================================
# pause to show options before continuing
sleep 3
echo " "
echo " "
# =======================================================================================

# =======================================================================================
# create the OLMT run command
echo " "
echo "**** User OLMT run command: "
runcmd="python3 ./site_fullrun.py \
      --site ${site_code} --sitegroup ${site_group} --caseidprefix ${case_prefix} \
      ${sim_years} --tstep ${timestep} --machine docker \
      --compiler gnu --mpilib openmpi \
      --cpl_bypass --gswp3 \
      --model_root /E3SM \
      --caseroot /output \
      --ccsm_input /inputdata \
      --runroot /output \
      --spinup_vars \
      --nopointdata \
      --metdir /inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_Workshop/cpl_bypass_${site_code} \
      --domainfile /inputdata/share/domains/domain.clm/domain_${site_code}_simyr1850_c170912.nc \
      --surffile /inputdata/lnd/clm2/surfdata_map/surfdata_${site_code}_simyr1850_c170912.nc \
      --nopftdyn \
      ${scaling_args} \
      & sleep 10"
echo ${runcmd}
echo " "
echo " "

echo "**** Running OLMT: "
if python3 ./site_fullrun.py \
      --site ${site_code} --sitegroup ${site_group} --caseidprefix ${case_prefix} \
      ${sim_years} --tstep ${timestep} --machine docker \
      --compiler gnu --mpilib openmpi \
      --cpl_bypass --gswp3 \
      --model_root /E3SM \
      --caseroot /output \
      --ccsm_input /inputdata \
      --runroot /output \
      --spinup_vars \
      --nopointdata \
      --metdir /inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_Workshop/cpl_bypass_${site_code} \
      --domainfile /inputdata/share/domains/domain.clm/domain_${site_code}_simyr1850_c170912.nc \
      --surffile /inputdata/lnd/clm2/surfdata_map/surfdata_${site_code}_simyr1850_c170912.nc \
      --nopftdyn \
      ${scaling_args} \
      & sleep 10

then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi
# =======================================================================================

# =======================================================================================
#### Postprocess
### Collapse transient simulation output into a single netCDF file
echo " "
echo " "
echo " "
echo "**** Postprocessing ELM output in: "
echo "/output/cime_run_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC/run"
echo " "
echo " "
cd /output/cime_run_dirs/${case_prefix}_${site_code}_ICB20TRCNPRDCTCBC/run
echo "**** Concatenating netCDF output - Hang tight this can take awhile ****"
ncrcat --ovr *.h0.*.nc ELM_output.nc
chmod 777 ELM_output.nc
echo "**** Concatenating netCDF output: DONE ****"
sleep 2
# =======================================================================================
