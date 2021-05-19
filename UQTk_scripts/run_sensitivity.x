#!/bin/bash -e

###############################################################################################################
# Set necessary paths and variables
###############################################################################################################
UQSCRIPTS_PATH=`dirname "$0"`

if [ ! -f prepare_env.x ]; then
	echo "=== Sourcing ${UQSCRIPTS_PATH}/prepare_env.x "
	echo "=== please edit for your computer-specific paths."
	source ${UQSCRIPTS_PATH}/prepare_env.x
else
	echo "Sourcing ./prepare_env.x : please edit for your computer-specific paths."
	source ./prepare_env.x
fi


## Set other relevant paths and variable
#export UQTKv2_PATH=${PWD}/UQTk_v2.2/src_cpp
#export UQTK_INS=${UQTKv2_PATH}
export UQTK_BIN=${UQTK_INS}/bin
export UQPC=${UQTK_INS}/examples/uqpc

###############################################################################################################
# Hardwired parameters to play with
###############################################################################################################

# Directory where ensemble is run
# Expects files param_range.txt, ptrain.dat, ytrain.dat, pval.dat, yval.dat in this directory
PRERUN_DIR=${UQSCRIPTS_PATH}/data #alm_5d_example or alm_5d_example_nz, or create your own folder with prerun data

# Surrogate construction method
# Options are lsq (least-squares) or bcs (Bayesian compressive sensing)
METHOD=bcs

# Select the order of the surrogate
ORDER=4

# Number of cores
NCORES=1

###############################################################################################################
# Sanity checks
###############################################################################################################

# Sanity check on method
if [[ "$METHOD" != "lsq" && "$METHOD" != "bcs" ]]; then
	echo "METHOD=$METHOD is not recognized (choose lsq or bcs)"
	exit
fi

###############################################################################################################
# Copy from previous runs
###############################################################################################################

echo "Getting the simulation results from ${PRERUN_DIR}"
for file in ${PRERUN_DIR}/*; do
	rm -f `basename $file`
	cp $file .
done

# Scale
${UQPC}/scale.x ptrain.dat from param_range.txt qtrain.dat
${UQPC}/scale.x pval.dat from param_range.txt qval.dat

NTRAIN=`awk 'END{print NR}' ptrain.dat`
NVAL=`awk 'END{print NR}' pval.dat`
SAMPLING=rand
# Number of outputs
NOUT=`awk 'NR==1{print NF}' ytrain.dat`
echo "Number of output QoIs : $NOUT "


###############################################################################################################
# Compute the surrogate 
###############################################################################################################

rm -rf results.pk

if [ "$NCORES" -eq "1" ];	then
	echo "Running in a serial mode"
	${UQPC}/uq_pc.py -r offline_post -p param_range.txt -m $METHOD -s $SAMPLING -n $NTRAIN -v $NVAL -t $ORDER

else
	echo "Running in parallel on $NCORES cores"
	echo "Creating tasks file"
	echo -n"" > tasks
	rm -rf task_*
	for ((outid=1;outid<=$NOUT;outid++)); do
		mkdir task_$outid
		for f in *train.dat *val.dat param_range.txt; do 
			ln -sf ../$f task_$outid/$f
		done
		let outidd=$NOUT+1-$outid #$outid 
		echo "${UQPC}/uq_pc.py out.log -a $outidd -r offline_post -p param_range.txt -m $METHOD -s $SAMPLING -n $NTRAIN -v $NVAL -t $ORDER" >> tasks
	done
	echo "Running tasks in task_* folders"
	${UQTK_INS}/PyUQTk/multirun/multirun.py tasks $NCORES > uqmulti.log

	${UQPC}/join_results.py
fi

if [ -f results.pk ]; then
	echo "Results are packed into results.pk"
else
	echo "Something is wrong. The file results.pk not found."
fi

###############################################################################################################
# Plot results 
###############################################################################################################

# Plot data-versus-model for surrogate accuracy assessment
${UQPC}/plot.py dm training  validation 

# Plot runId versus data and model for surrogate accuracy assessment
${UQPC}/plot.py idm training  
${UQPC}/plot.py idm validation  

# Plot sensitivities (multi-output bars)
${UQPC}/plot.py sens main
${UQPC}/plot.py sens total

# Plot total sensitivities (matrix plots for all outputs and most relevant inputs)
${UQPC}/plot.py sensmat total

# Plot main and joint sensitivities for all outputs (circular plots)
${UQPC}/plot.py senscirc

# Plot high-d representation of multiindex
${UQPC}/plot.py mindex

# Compute and plot output PDFs
if [[ "$METHOD" != "bcs" ]]; then # requires full multiindex to work, therefore won't compute it with bcs
	${UQPC}/plot.py pdf
fi

###############################################################################################################
# Cleanup
###############################################################################################################

# Save the input-outputs/sensitivities and logs just in case 
tar -czf logs.tar $(ls -d *.log 2>/dev/null)
tar -czf inouts_sens.tar *train.dat *val.dat *sens*dat mindex_output*dat pcf_output*dat 

# Clean the rest
rm -rf tmp cfs *.dat *.log pcf *.txt





