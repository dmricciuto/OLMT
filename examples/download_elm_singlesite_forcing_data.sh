#!/bin/bash

# =======================================================================================
#  Download ELM singe-site driver files
#  Source: GitHub
#  Source URL: https://github.com/fmyuan/pt-e3sm-inputdata
#  Source Data URL: https://github.com/fmyuan/pt-e3sm-inputdata/archive/refs/heads/master.zip
# =======================================================================================

# =======================================================================================
# How to use this with the Docker container, run:
# docker run -t -i --hostname=docker --user modeluser -v VolELM_inputs:/inputdata \
# yuanfornl/elm_docker:nvhpc2023 /bin/sh -c 'cd /scripts && bash ./download_elm_singlesite_forcing_data.sh'
#
# =======================================================================================

# =======================================================================================
# USER OPTIONS
# path to "single_site" directory within main CESM data directory located on the host
# machine
cesm_data_dir=/inputdata
mkdir -p ${cesm_data_dir}
# =======================================================================================

# =======================================================================================
echo "*** Downloading and extracting forcing data ***"

cd ${cesm_data_dir}
# remove any old files before downloading updated met data
rm -rf *
# download the met data
wget https://github.com/fmyuan/pt-e3sm-inputdata/archive/refs/heads/master.zip
unzip master.zip
cd pt-e3sm-inputdata-master
mv * ../
cd ..

echo "*** Removing zip file ***"
rm -rf pt-e3sm-inputdata-master
#rm -f ${cesm_data_dir}/master.zip
rm -f master.zip

# go in and extract remaining tar files
cd ${cesm_data_dir}/lnd/clm2/firedata
tar -zxvf clmforc.Li_2012_hdm_0.5x0.5_AVHRR_simyr1850-2010_c130401.nc.tar.gz
cd ${cesm_data_dir}/atm/datm7/NASA_LIS
tar -zxvf clmforc.Li_2012_climo1995-2011.T62.lnfm_c130327.nc.tar.gz
tar -zxvf clmforc.Li_2012_climo1995-2011.T62.lnfm_Total_c140423.nc.tar.gz
# =======================================================================================

# =======================================================================================
# done
echo "*** DONE ***"
# =======================================================================================
