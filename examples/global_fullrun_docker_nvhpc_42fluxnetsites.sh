#!/bin/sh -f

cwd=$(pwd)

## 
# =======================================================================================
# Get the input options from the command line
for i in "$@"
do
case $i in
    -cp=*|--case_prefix=*)
    case_prefix="${i#*=}"
    shift # past argument=value
    ;;
    -cc=*|--compiler=*)
    compiler="${i#*=}"
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
    *)
        # unknown option
    ;;
esac
done
# =======================================================================================


## default

case_prefix="${case_prefix:-ELMcpu}"
compiler="${compiler:-nvidia}"
ad_spinup_years="${ad_spinup_years:-200}"
final_spinup_years="${final_spinup_years:-600}"
transient_years="${transient_years:--1}"
# -1 is the default to run all years from 1850
timestep="${timestep:-1}"

if [ ${transient_years} != -1 ]; then
  sim_years="--nyears_ad_spinup ${ad_spinup_years} --nyears_final_spinup ${final_spinup_years} \
  --nyears_transient ${transient_years}"
elif [ ${transient_years} == 0 ]; then
  sim_years="--nyears_ad_spinup ${ad_spinup_years} --nyears_final_spinup ${final_spinup_years} \
  --notrans"

  if [ ${transient_years} == 0 ]; then
    sim_years="--nyears_ad_spinup ${ad_spinup_years} --nyears_final_spinup ${final_spinup_years} \
  --nofn --notrans"
  fi

else
  sim_years="--nyears_ad_spinup ${ad_spinup_years} --nyears_final_spinup ${final_spinup_years}"
fi

cd /tools/OLMT

mkdir -p /output/cime_case_dirs

if python3 ./global_fullrun.py \
      --caseidprefix ${case_prefix} \
      ${sim_years} --tstep ${timestep} \
      --machine docker --compiler ${compiler} --mpilib openmpi \
      --cpl_bypass --gswp3 \
      --model_root /E3SM \
      --caseroot /output/cime_case_dirs \
      --ccsm_input /inputdata \
      --runroot /output/cime_run_dirs \
      --np 2 \
      --walltime 48 \
      --spinup_vars \
      --nopointdata \
      --metdir /inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716_42FLUXNETSITES/cpl_bypass_full \
      --domainfile /inputdata/share/domains/domain.clm/domain_42_FLUXNETSITES_simyr1850_c170912.nc \
      --surffile /inputdata/lnd/clm2/surfdata_map/surfdata_42_FLUXNETSITES_simyr1850_c170912.nc \
      --landusefile /inputdata/lnd/clm2/surfdata_map/surfdata.pftdyn_42_FLUXNETSITES_rcp8.5_simyr1850-2100_c181106.nc \
      & sleep 10

then
  wait

  echo "DONE docker ELM runs !"

else
  exit &?
fi

cd ${cwd}



