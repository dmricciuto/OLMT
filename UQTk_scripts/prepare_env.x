#!/bin/bash 

export UQTK_INS=/home/dmricciuto/models/Uncertainty-Quantification/Param-UQ-Workflow/UQTk_v3.0.2-install

if [[ $HOSTNAME == *"titan"* ]] ; then

	printf "Seems to be on Titan: loading python_anaconda/2.3.0, gcc, cmake/2.8.11.2 \n"
	module load python_anaconda/2.3.0
	module load gcc
 	module load cmake/2.8.11.2

elif [[ $HOSTNAME == "eos"* ]] ; then


  	printf "Seems to be on Eos: loading python_anaconda/2.3.0, gcc, cmake/2.8.11.2 \n"
	module load python_anaconda/2.3.0
	module load gcc
 	module load cmake/2.8.11.2


elif [[ $HOSTNAME == "arsenal" ]]; then

	echo "Setting up arsenal"
        

elif [[ $HOSTNAME == "lofty" ]]; then

	echo "Setting up lofty"


fi
