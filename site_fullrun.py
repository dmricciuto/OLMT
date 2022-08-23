#!/usr/bin/env python

import socket, getpass, os, sys, csv, math
from optparse import OptionParser
import subprocess
import numpy
import re


### Run options
parser = OptionParser();

# general OLMT options
parser.add_option("--no_submit", dest="no_submit", default=False, action="store_true", \
                  help = 'do NOT submit built model to queue, i.e. build only')
parser.add_option("--caseidprefix", dest="mycaseid", default="", \
                  help="Unique identifier to include as a prefix to the case name")
parser.add_option("--caseroot", dest="caseroot", default='', \
                  help = "case root directory, where submission scripts live (default = '', i.e., under model_root/scripts/)")
parser.add_option("--runroot", dest="runroot", default="", \
                  help="Directory where the run would be created")
parser.add_option("--exeroot", dest="exeroot", default="", \
                  help="Location of executable")
parser.add_option("--archiveroot", dest="archiveroot", default='', \
                  help = "archive root directory only for mesabi")
parser.add_option("--batch_build", action="store_true", default=False, \
                  help="Do build as part of submitted batch script")
parser.add_option("--constraints", dest="constraints", default="", \
                  help="Directory containing model constraints")
parser.add_option("--compare_cases", dest="compare", default='', \
                  help = 'caseidprefix(es) to compare')
parser.add_option("--ninst", dest="ninst", default=1, \
                  help = 'number of land model instances')
parser.add_option("--mc_ensemble", dest="mc_ensemble", default=-1, \
                  help = 'Monte Carlo ensemble (argument is # of simulations)')
parser.add_option("--ng", dest="ng", default=256, \
                  help = 'number of groups to run in ensemble mode')
parser.add_option("--parm_list", dest="parm_list", default='parm_list', \
                  help = 'File containing list of parameters to vary')
parser.add_option("--mod_parm_file", dest="mod_parm_file", default='', \
                  help = "adding the path to the modified parameter file")
parser.add_option("--mod_parm_file_P", dest="mod_parm_file_P", default='', \
                  help = "adding the path to the modified parameter file")
parser.add_option("--ensemble_file", dest="ensemble_file", default='', \
                  help = 'Parameter sample file to generate ensemble')
parser.add_option("--postproc_file", dest="postproc_file", default="postproc_vars", \
                  help = 'File for ensemble post processing')
parser.add_option("--nopftdyn", dest="nopftdyn", default=False, action="store_true", \
                  help='Do not use dynamic PFT file')

# general model build options
parser.add_option("--model_root", dest="csmdir", default='', \
                  help = "base CESM directory")
parser.add_option("--compiler", dest="compiler", default = '', \
                  help = "compiler to use (pgi*, gnu)")
parser.add_option("--mpilib", dest="mpilib", default="mpi-serial", \
                  help = "mpi library (openmpi, mpich, ibm, mpi-serial)")
parser.add_option("--debugq", dest="debug", default=False, action="store_true", \
                  help='Use debug queue and options')
parser.add_option("--clean_build", action="store_true", default=False, \
                  help="Perform a clean build")
parser.add_option("--cpl_bypass", dest = "cpl_bypass", default=False, action="store_true", \
                  help = "Bypass coupler")
parser.add_option("--machine", dest="machine", default = '', \
                  help = "machine to use")
parser.add_option("--np", dest="np", default=1, \
                  help = 'number of processors')
parser.add_option("--walltime", dest="walltime", default=6, \
                  help = "desired walltime for each job (hours)")
parser.add_option("--pio_version", dest="pio_version", default='2', \
                      help = "PIO version (1 or 2)")

# CASE options
parser.add_option("--nyears_ad_spinup", dest="ny_ad", default=250, \
                  help = 'number of years to run ad_spinup')
parser.add_option("--nyears_final_spinup", dest="nyears_final_spinup", default='200', \
                  help="base no. of years for final spinup")
parser.add_option("--nyears_transient", dest="nyears_transient", default=-1, \
                  help = 'number of years to run transient')
parser.add_option("--ad_Pinit", dest="ad_Pinit", default=False, action="store_true", \
                  help="Initialize AD spinup with P pools and use CNP mode")
parser.add_option("--noad", action="store_true", dest="noad", default=False, \
                  help='Do not perform ad spinup simulation')
parser.add_option("--nofnsp", action="store_true", dest="nofnsp", default=False, \
                  help='Do not perform final spinup simulation')
parser.add_option("--notrans", action="store_true", dest="notrans", default=False, \
                  help='Do not perform transient simulation (spinup only)')

# model input options
parser.add_option("--site", dest="site", default='', \
                  help = '6-character FLUXNET code to run (required)')
parser.add_option("--sitegroup", dest="sitegroup",default="AmeriFlux", \
                  help = "site group to use (default AmeriFlux)")
parser.add_option("--ccsm_input", dest="ccsm_input", default='', \
                  help = "input data directory for CESM (required)")
# metdata 
parser.add_option("--nopointdata", dest="nopointdata", default=False, action="store_true", \
                  help="Do NOT make point data (use data already created)")
parser.add_option("--metdir", dest="metdir", default="none", \
                  help = 'subdirectory for met data forcing')
parser.add_option("--metdata_dir", dest="metdata_dir", default='none', \
                  help = 'Directory containing cpl_bypass met data (site only)')
parser.add_option("--makemetdata", action="store_true", dest="makemet", default=False, \
                  help="generate site meteorology")
parser.add_option("--cruncep", dest="cruncep", default=False, action="store_true", \
                  help = 'Use CRU-NCEP meteorology')
parser.add_option("--cruncepv8", dest="cruncepv8", default=False, action="store_true", \
                  help = 'Use CRU-NCEP meteorology')
parser.add_option("--gswp3", dest="gswp3", default=False, action="store_true", \
                  help = 'Use GSWP3 meteorology')
parser.add_option("--gswp3_w5e5", dest="gswp3_w5e5", default=False, action="store_true", \
                  help = 'Use GSWP3 meteorology')
parser.add_option("--princeton", dest="princeton", default=False, action="store_true", \
                  help = 'Use Princeton meteorology')
parser.add_option("--co2_file", dest="co2_file", default="fco2_datm_rcp4.5_1765-2500_c130312.nc", \
                  help = 'co2 data filename')
parser.add_option("--eco2_file", dest="eco2_file", default="", \
                  help = 'elevated co2 data filename, will spawn three transient simulations, using this file for an elevated co2 sim')
parser.add_option("--add_co2", dest="addco2", default=0.0, \
                  help = 'CO2 (ppmv) to add to atmospheric forcing')
parser.add_option("--startdate_add_co2", dest="sd_addco2", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin addding CO2')
parser.add_option("--add_temperature", dest="addt", default=0.0, \
                  help = 'Temperature to add to atmospheric forcing')
parser.add_option("--startdate_add_temperature", dest="sd_addt", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin addding temperature')
parser.add_option("--scale_precipitation", dest="sclp", default=1.0, \
                  help = 'Scaling factor to apply to total precipitation in atmospheric forcing')
parser.add_option("--startdate_scale_precipitation", dest="sd_sclp", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin scaling total precipitation')
parser.add_option("--scale_rain", dest="sclr", default=1.0, \
                  help = 'Scaling factor to apply to rain in atmospheric forcing')
parser.add_option("--startdate_scale_rain", dest="sd_sclr", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin scaling rain')
parser.add_option("--scale_snow", dest="scls", default=1.0, \
                  help = 'Scaling factor to apply to snowfall in atmospheric forcing')
parser.add_option("--startdate_scale_snow", dest="sd_scls", default="99991231", \
                  help = 'Date (YYYYMMDD) to begin scaling snowfall')
# surface data
parser.add_option("--surfdata_grid", dest="surfdata_grid", default=False, action="store_true", \
                  help = 'Use gridded surface data instead of site data')
parser.add_option("--surffile", dest="surffile", default='', \
                  help = 'Use specified surface data file')
parser.add_option("--domainfile", dest="domainfile", default="", \
                  help = 'Domain file to use')
parser.add_option("--finitfile", dest="finitfile", default="", \
                  help = 'initial ELM data file to start/restart')
# parameters
parser.add_option("--pft", dest="mypft", default=-1, \
                  help = 'Use this PFT (override site default)')
parser.add_option("--siteparms",dest = "siteparms", default=False, action="store_true", \
                  help = 'Use default PFT parameters')
parser.add_option("--parm_file", dest="parm_file", default="", \
                  help = 'parameter file to use')
parser.add_option("--parm_file_P", dest="parm_file_P", default="", \
                  help = 'parameter file to use')
parser.add_option("--fates_paramfile", dest="fates_paramfile", default="", \
                  help = 'Fates parameter file to use')
parser.add_option("--parm_vals", dest="parm_vals", default="", \
                  help = 'User specified parameter values')

# model structural config options
parser.add_option("--namelist_file", dest="namelist_file", default='', \
                  help="File containing custom namelist options for user_nl_clm")
parser.add_option("--tstep", dest="tstep", default=0.5, \
                  help = 'CLM timestep (hours)')
parser.add_option("--SP", dest="sp", default=False, action="store_true", \
                  help = 'Use satellite phenology mode')
parser.add_option("--lai", dest="lai", default=-999, \
                  help = 'Set constant LAI (SP mode only)')
parser.add_option("--run_startyear", dest="run_startyear", default="1850", \
                  help="Starting year for simulation (SP mode only)")
parser.add_option("--crop", action="store_true", default=False, \
                  help="Perform a crop model simulation")
parser.add_option("--humhol", dest="humhol", default=False, action="store_true", \
                  help = 'Use hummock/hollow microtopography')
parser.add_option("--marsh", dest="marsh", default=False, \
                  help = 'Use marsh hydrology/elevation', action="store_true")
parser.add_option("--tide_components_file", dest="tide_components_file", default='', \
                    help = 'NOAA tide components file')
parser.add_option("--nofire", dest="nofire", default=False, action="store_true", \
                  help='Turn off fire algorithms')
parser.add_option("--C13", dest="C13", default=False, action="store_true", \
                  help = 'Switch to turn on C13')
parser.add_option("--C14", dest="C14", default=False, action="store_true", \
                  help = 'Use C14 as C13 (no decay)')
parser.add_option("--aero_rcp85",dest="aerorcp85", action="store_true", default=False,help="Use RCP8.5 aerosols")
parser.add_option("--ndep_rcp85",dest="ndeprcp85", action="store_true", default=False,help="Use RCP8.5 N dep")
parser.add_option("--harvmod", action="store_true", dest='harvmod', default=False, \
                  help="turn on harvest modification:  All harvest at first timestep")
parser.add_option("--no_dynroot", dest="no_dynroot", default=False, action="store_true", \
                  help = 'Turn off dynamic root distribution')
parser.add_option("--vertsoilc", dest="vsoilc", default=False, action="store_true", \
                  help = 'To turn on CN with multiple soil layers, excluding CENTURY C module (CLM4ME on as well)')
parser.add_option("--centbgc", dest="centbgc", default=False, action="store_true", \
                  help = 'To turn on CN with multiple soil layers, CENTURY C module (CLM4ME on as well)')
parser.add_option("--CH4", dest="CH4", default=False, action="store_true", \
                  help = 'To turn on CN with CLM4me')
parser.add_option("--fates", dest="fates", default=False, action="store_true", \
                  help = 'Use fates model')
parser.add_option("--fates_nutrient", dest="fates_nutrient", default="", \
                  help = 'Which version of fates_nutrient to use (RD or ECA)')
parser.add_option("--ECA", dest="eca", default=False, action="store_true", \
                  help = 'Use ECA compset')
parser.add_option("--c_only", dest="c_only", default=False, action ="store_true",  \
                  help='Carbon only (saturated N&P)')
parser.add_option("--cn_only", dest="cn_only", default=False, action ="store_true", \
                  help='Carbon/Nitrogen only (saturated P)') 
parser.add_option("--srcmods_loc", dest="srcmods_loc", default='', \
                  help = 'Copy sourcemods from this location')
parser.add_option("--daymet", dest="daymet", default=False, \
                  action="store_true", help = 'Use Daymet corrected meteorology')
parser.add_option("--daymet4", dest="daymet4", default=False, \
                  action="store_true", help = "Daymet v4 downscaled GSWP3-v2 forcing with user-provided domain and surface data)")
parser.add_option("--dailyvars", dest="dailyvars", default=False, \
                 action="store_true", help="Write daily ouptut variables")
parser.add_option("--var_soilthickness",dest="var_soilthickness", default=False, \
                  help = 'Use variable soil depth from surface data file',action='store_true')
parser.add_option("--no_budgets", dest="no_budgets", default=False, \
                  help = 'Turn off CNP budget calculations', action='store_true')
parser.add_option("--use_hydrstress", dest="use_hydrstress", default=False, \
                  help = 'Turn on hydraulic stress', action='store_true')
parser.add_option("--spruce_treatments", dest="spruce_treatments", default=False, \
                  help = 'Run SPRUCE treatment simulations (ensemble mode)', action='store_true')

# model output options
parser.add_option("--hist_vars", dest="hist_vars", default='', \
                  help = 'Output only selected variables in h0 file (comma delimited)')
parser.add_option("--diags", dest="diags", default=False, action="store_true", 
                  help="Write special outputs for diagnostics")
parser.add_option("--trans_varlist", dest = "trans_varlist", default='', \
                  help = "Transient outputs")
parser.add_option("--hist_mfilt_trans", dest="hist_mfilt", default="365", \
                  help = 'number of output timesteps per file (transient only)')
parser.add_option("--hist_nhtfrq_trans", dest="hist_nhtfrq", default="-24", \
                  help = 'output file timestep (transient only)')
parser.add_option("--spinup_vars", dest = "spinup_vars", default=False, action="store_true", \
                  help = "limit output variables for spinup")
parser.add_option("--hist_mfilt_spinup", dest="hist_mfilt_spinup", default="-999", \
                  help = 'number of output timesteps per file (spinup only)')
parser.add_option("--hist_nhtfrq_spinup", dest="hist_nhtfrq_spinup", default="-999", \
                  help = 'output file timestep (spinup only)')

#datasets for user-defined PFTs (by F-M Yuan, NGEE-Arctic)
parser.add_option("--maxpatch_pft", dest="maxpatch_pft", default=17, \
                  help = "user-defined max. patch PFT number, default is 17")
parser.add_option("--landusefile", dest="pftdynfile", default='', \
                  help='user-defined dynamic PFT file')

parser.add_option("--var_list_pft", dest="var_list_pft", default="",help='Comma-separated list of vars to output at PFT level')
parser.add_option("--dryrun",dest="dryrun",default=False,action="store_true",help="Do not execute commands")

#options for coupling with PFLOTRAN
parser.add_option("--clmpf_source_dir", dest="clmpf_source_dir", default='', \
                  help = 'pflotran-elm-interface source directory, blanked by default, otherwise build ELM with PFLOTRAN coupled')
parser.add_option("--clmpf_mode", dest="clmpf_mode", default=False, \
                  help = 'option to run CLM with pflotran coupled codes, off by default. NOTE that ELM must be built with pflotran-elm-interface', \
                   action="store_true")
parser.add_option("--clmpf_inputdir", dest="clmpf_inputdir", default='', \
                  help = 'pflotran input directory, by default it under lnd input directory. ONLY required if clmpf_mode ON')
parser.add_option("--clmpf_prefix", dest="clmpf_prefix", default='', \
                  help = 'pflotran.in customized, by default it "pflotran_clm" (.in ommitted) under lnd input directory. ONLY required if clmpf_mode ON')

(options, args) = parser.parse_args()

def runcmd(cmd,echo=True):
    if echo:
        print(cmd)
    if not options.dryrun:
        return os.system(cmd)
    else:
        return 0


#----------------------------------------------------------
# define function for pbs submission
def submit(fname, submit_type='qsub', job_depend=''):
    job_depend_flag = ' -W depend=afterok:'
    if ('sbatch' in submit_type):
        job_depend_flag = ' --dependency=afterok:'
    if (job_depend != '' and submit_type != ''):
        runcmd(submit_type+job_depend_flag+job_depend+' '+fname+' > temp/jobinfo')
    else:
      if (submit_type == ''):
        runcmd('chmod a+x '+fname)
        runcmd('./'+fname+' > temp/jobinfo')
      else:
        runcmd(submit_type+' '+fname+' > temp/jobinfo')
    if (submit_type != '' and not options.dryrun):
      myinput = open('temp/jobinfo')
      for s in myinput:
          thisjob = re.search('[0-9]+', s).group(0)
      myinput.close()
    else:
      thisjob="0"
      runcmd('rm temp/jobinfo')
    return thisjob


#----------------------------------------------------------
# Set default model root
if (options.csmdir == ''):
   if (os.path.exists('../E3SM')):
       options.csmdir = os.path.abspath('../E3SM')
       print('Model root not specified.  Defaulting to '+options.csmdir)
   else:
       print('Error:  Model root not specified.  Please set using --model_root')
       sys.exit(1)
elif (not os.path.exists(options.csmdir)):
     print('Error:  Model root '+options.csmdir+' does not exist.')
     sys.exit(1)

#check whether model named clm or elm
if (os.path.exists(options.csmdir+'/components/elm')):
  model_name='elm'
else:
  model_name='clm2'

#get machine info if not specified
npernode=32
if (options.machine == ''):
   hostname = socket.gethostname()
   print('')
   print('Machine not specified.  Using hostname '+hostname+' to determine machine')
   if ('or-slurm' in hostname):
       options.machine = 'cades'
       npernode=32
   elif ('cori' in hostname):
       print('Cori machine not specified.  Setting to cori-haswell')
       options.machine = 'cori-haswell'
       npernode=32
   elif ('blues' in hostname or 'blogin' in hostname):
       print('Hostname = '+hostname+' and machine not specified.  Assuming anvil')
       options.machine = 'anvil' 
       npernode=36
   elif ('compy' in hostname):
       options.machine = 'compy'
       npernode=40
   elif ('ubuntu' in hostname):
       options.machine = 'ubuntu'
       npernode = 8
   elif ('chrlogin' in hostname):
       options.machine = 'chrysalis'
       npernode = 64    
   else:
       print('ERROR in site_fullrun.py:  Machine not specified.  Aborting')
       sys.exit(1)

if (options.ccsm_input != ''):
    ccsm_input = options.ccsm_input
elif (options.machine == 'titan' or options.machine == 'eos'):
    ccsm_input = '/lustre/atlas/world-shared/cli900/cesm/inputdata'
elif (options.machine == 'cades'):
    ccsm_input = '/nfs/data/ccsi/proj-shared/E3SM/inputdata/'
elif (options.machine == 'edison' or 'cori' in options.machine):
    ccsm_input = '/project/projectdirs/acme/inputdata'
elif ('anvil' in options.machine or 'chrysalis' in options.machine):
    ccsm_input = '/home/ccsm-data/inputdata'
elif ('compy' in options.machine):
    ccsm_input = '/compyfs/inputdata/'

#if (options.compiler != ''):
#    if (options.machine == 'titan'):
#        options.compiler = 'pgi'
#    if (options.machine == 'eos' or options.machine == 'edison' or 'cori' in options.machine):
#        options.compiler = 'intel'
#    if (options.machine == 'cades'):
#        options.compiler = 'gnu'
    

mycaseid   = options.mycaseid
srcmods    = options.srcmods_loc
if (mycaseid == ''):
  myscriptsdir = 'none'
else:
  myscriptsdir = mycaseid


#get start and year of input meteorology from site data file
PTCLMfiledir = ccsm_input+'/lnd/clm2/PTCLM'
fname = PTCLMfiledir+'/'+options.sitegroup+'_sitedata.txt'
AFdatareader = csv.reader(open(fname, "rt"))

translen = int(options.nyears_transient)

csmdir = options.csmdir

#case run and case root directories
myproject='e3sm'
if (options.runroot == '' or (os.path.exists(options.runroot) == False)):
    myuser = getpass.getuser()
    if (options.machine == 'titan' or options.machine == 'eos'):
        myinput = open('/ccs/home/'+myuser+'/.cesm_proj','r')
        for s in myinput:
    	    myproject=s[:-1]
        runroot='/lustre/atlas/scratch/'+myuser+'/'+myproject
    elif (options.machine == 'cades'):
        runroot='/lustre/or-scratch/cades-ccsi/scratch/'+myuser
    elif ('cori' in options.machine):
        runroot='/global/cscratch1/sd/'+myuser
        myinput = open(os.environ.get('HOME')+'/.cesm_proj','r')
        for s in myinput:
           myproject=s[:-1] 
        print('Project = '+myproject)
    elif ('edison' in options.machine):
        runroot=os.environ.get('CSCRATCH')+'/acme_scratch/edison/'
    elif ('anvil' in options.machine or 'chrysalis' in options.machine):
        runroot="/lcrc/group/acme/"+myuser
        myproject='e3sm'
    elif ('compy' in options.machine):
        runroot='/compyfs/'+myuser+'/e3sm_scratch'
        myproject='e3sm'
    else:
        runroot = csmdir+'/run'
else:
    runroot = os.path.abspath(options.runroot)

if (options.caseroot == options.runroot):
    caseroot = os.path.abspath(options.caseroot)+'/cime_case_dirs'
    os.system('mkdir -p '+caseroot)
    runroot = os.path.abspath(options.caseroot)+'/cime_run_dirs'
    os.system('mkdir -p '+runroot)
elif (options.caseroot == '' or (os.path.exists(options.caseroot) == False)):
    caseroot = os.path.abspath(csmdir+'/cime/scripts')
else:
    caseroot = os.path.abspath(options.caseroot)


sitenum=0
# create ensemble file if requested (so that all cases use the same)
if (int(options.mc_ensemble) != -1):
    if (not(os.path.isfile(options.parm_list))):
        print('parm_list file does not exist')
        sys.exit()
    else:
        param_names=[]
        param_min=[]
        param_max=[]
        input = open(options.parm_list,'r')
        for s in input:
            if (s):
                param_names.append(s.split()[0])
                if (int(options.mc_ensemble) > 0):
                    if (len(s.split()) == 3):
                        param_min.append(float(s.split()[1]))
                        param_max.append(float(s.split()[2]))
                    else:
                        param_min.append(float(s.split()[2]))
                        param_max.append(float(s.split()[3]))
        input.close() 
        n_parameters = len(param_names)
    nsamples = int(options.mc_ensemble)
    samples=numpy.zeros((n_parameters,nsamples), dtype=float)
    for i in range(0,nsamples):
        for j in range(0,n_parameters):
            samples[j][i] = param_min[j]+(param_max[j]-param_min[j])*numpy.random.rand(1)
    numpy.savetxt('mcsamples_'+options.mycaseid+'_'+str(options.mc_ensemble)+'.txt', \
                  numpy.transpose(samples))
    options.ensemble_file = 'mcsamples_'+options.mycaseid+'_'+str(options.mc_ensemble)+'.txt'


mysites = options.site.split(',')

nnode=1
if(int(options.np)>1): #in case of a single site in name but with multiple unstructured gridcells
    npernode=min(int(npernode),int(options.np))
    nnode=-(int(options.np)//-int(npernode))
elif (not 'all' in mysites and (options.ensemble_file == '')):
    npernode = len(mysites)

for row in AFdatareader:
    if (row[0] in mysites) or ('all' in mysites and row[0] !='site_code' \
                                      and row[0] != ''):
        site      = row[0]
        if (sitenum == 0):
            firstsite=site
        site_lat  = row[4]
        site_lon  = row[3]
        if (options.cruncepv8 or options.cruncep or options.gswp3 or options.gswp3_w5e5 or options.princeton):
          startyear = 1901
          endyear = 1920
          if (options.cruncepv8):
            endyear_trans=2016
          elif (options.gswp3):
            endyear_trans=2014
          elif (options.gswp3_w5e5):
            endyear_trans=2019
          elif (options.princeton):
            endyear_trans=2012
          else:
            endyear_trans=2010
        else:
            startyear = int(row[6])
            endyear   = int(row[7])
        if (options.diags): 
            timezone = int(row[9])

        site_endyear = int(row[7])
        ncycle   = endyear-startyear+1   #number of years in met cycle
        ny_ad = options.ny_ad
        ny_fin = options.nyears_final_spinup

        #AD spinup and final spinup lengths must be multiples of met data cyle.
        if (int(options.ny_ad) % ncycle != 0):
          ny_ad = str(int(ny_ad) + ncycle - (int(ny_ad) % ncycle))
        # APW TCOFD
        #if (int(options.nyears_final_spinup) % ncycle !=0 and options.noad == False):
        if (int(options.nyears_final_spinup) % ncycle !=0):
          ny_fin = str(int(ny_fin) + ncycle - (int(ny_fin) % ncycle))

        if (options.nyears_transient == -1):
            translen = endyear-1850+1            # length of transient run
            if (options.eco2_file != ''):
                translen = translen - ncycle     # if experiment sim, stop first transient at exp start yr - 1
            if (options.cpl_bypass and (options.cruncep or options.gswp3 or \
                options.princeton or options.cruncepv8 or options.gswp3_w5e5)):
                print(endyear_trans, site_endyear)
                translen = min(site_endyear,endyear_trans)-1850+1

        fsplen = int(ny_fin)
 
        #get align_year
        year_align = (endyear-1850+1) % ncycle

        #use site parameter file if it exists
        if (options.siteparms):
            if (os.path.exists(PTCLMfiledir+'/parms_'+site)):
                print ('Using parameter file PTCLM_Files/parms_'+site)
                options.parm_file = PTCLMfiledir+'/parms_'+site
            else:
                options.parm_file = ''


#---------------- build base command for all calls to runcase.py -----------------------------

        #print year_align, fsplen
        basecmd = 'python runcase.py --site '+site+' --ccsm_input '+ \
            os.path.abspath(ccsm_input)+' --rmold --no_submit --sitegroup ' + \
            options.sitegroup
        if (options.machine != ''):
            basecmd = basecmd+' --machine '+options.machine
        if (options.csmdir != ''):
            basecmd = basecmd+' --model_root '+options.csmdir
        if (srcmods != ''):
            srcmods    = os.path.abspath(srcmods)
            basecmd = basecmd+' --srcmods_loc '+srcmods
        elif (options.ad_Pinit):
            srcmods    = os.path.abspath('srcmods_Pinit')
            basecmd = basecmd+' --srcmods_loc '+srcmods
        if (mycaseid != ''):
            basecmd = basecmd+' --caseidprefix '+mycaseid
        if (options.parm_file != ''):
            basecmd = basecmd+' --parm_file '+options.parm_file
        if (options.parm_file_P != ''):
            basecmd = basecmd+' --parm_file_P '+options.parm_file_P
        if (options.parm_vals != ''):
            basecmd = basecmd+' --parm_vals '+options.parm_vals
        if (options.clean_build):
            basecmd = basecmd+' --clean_build '
        if (options.namelist_file != ''):
            basecmd = basecmd+' --namelist_file '+options.namelist_file
        if (options.metdir !='none'):
            basecmd = basecmd+' --metdir '+options.metdir
        if (options.metdata_dir !='none'):
            basecmd = basecmd+' --metdata_dir '+options.metdata_dir
        if (options.C13):
            basecmd = basecmd+' --C13 '
        if (options.C14):
            basecmd = basecmd+' --C14 '
        if (options.debug):
            basecmd = basecmd+' --debugq'
        if (options.ninst > 1):
            basecmd = basecmd+' --ninst '+str(options.ninst)
        if (int(options.mypft) >= 0):
            basecmd = basecmd+' --pft '+str(options.mypft)
        if (options.nofire):
            basecmd = basecmd+' --nofire'
        if (options.harvmod):
            basecmd = basecmd+' --harvmod'
        if (options.humhol):
            basecmd = basecmd+' --humhol'
        if (options.marsh):
            basecmd = basecmd+' --marsh'
        if (options.tide_components_file != ''):
            basecmd = basecmd + ' --tide_components_file %s'%options.tide_components_file
        if (float(options.lai) >= 0):
            basecmd = basecmd+' --lai '+str(options.lai)
        if (options.nopftdyn):
            basecmd = basecmd+' --nopftdyn'
        if (options.no_dynroot):
            basecmd = basecmd+' --no_dynroot'
        if (options.vsoilc):
            basecmd = basecmd+' --vertsoilc'
        if (options.centbgc):
            basecmd = basecmd+' --centbgc'
        if (options.c_only):
            basecmd = basecmd+' --c_only'
        if (options.cn_only):
            basecmd = basecmd+' --cn_only'
        if (options.CH4):
            basecmd = basecmd+' --CH4'
        if (options.cruncep):
            basecmd = basecmd+' --cruncep'
        if (options.cruncepv8):
            basecmd = basecmd+' --cruncepv8'
        if (options.gswp3):
            basecmd = basecmd+' --gswp3'
        if (options.gswp3_w5e5):
            basecmd = basecmd+' --gswp3_w5e5'    
        if (options.princeton):
            basecmd = basecmd+' --princeton'
        if (options.daymet):
            basecmd = basecmd+' --daymet'
        if (options.daymet4): # gswp3 v2 spatially-downscaled by daymet v4, usually together with user-defined domain and surface data
            basecmd = basecmd+' --daymet4'
            if (not options.gswp3): basecmd = basecmd+' --gswp3'
        if (options.fates_paramfile != ''):
            basecmd = basecmd+ ' --fates_paramfile '+options.fates_paramfile
        if (options.fates_nutrient != ''):
            basecmd = basecmd+ ' --fates_nutrient '+options.fates_nutrient
        if (options.surfdata_grid):
            basecmd = basecmd+' --surfdata_grid'
        if (options.ensemble_file != ''):   
            basecmd = basecmd+' --ensemble_file '+options.ensemble_file
            basecmd = basecmd+' --parm_list '+options.parm_list
        if (options.archiveroot !=''):
            basecmd = basecmd+' --archiveroot '+options.archiveroot
        if (options.mod_parm_file !=''):
            basecmd = basecmd+' --mod_parm_file '+options.mod_parm_file
        if (options.mod_parm_file_P !=''):
            basecmd = basecmd+' --mod_parm_file_P '+options.mod_parm_file_P
        if (options.addt != 0):
            basecmd = basecmd+' --add_temperature '+str(options.addt)
            basecmd = basecmd+' --startdate_add_temperature '+str(options.sd_addt)
        if (options.sclp != 0):
            basecmd = basecmd+' --scale_precipitation '+str(options.sclp)
            basecmd = basecmd+' --startdate_scale_precipitation '+str(options.sd_sclp)
        if (options.sclr != 0):
            basecmd = basecmd+' --scale_rain '+str(options.sclr)
            basecmd = basecmd+' --startdate_scale_rain '+str(options.sd_sclr)
        if (options.scls != 0):
            basecmd = basecmd+' --scale_snow '+str(options.scls)
            basecmd = basecmd+' --startdate_scale_snow '+str(options.sd_scls)
        if (options.addco2 != 0):
            basecmd = basecmd+' --add_co2 '+str(options.addco2)
            basecmd = basecmd+' --startdate_add_co2 '+str(options.sd_addco2)
        if (options.surffile != ''):
            basecmd = basecmd+' --surffile '+options.surffile      
        basecmd = basecmd + ' --ng '+str(options.ng)
        basecmd = basecmd + ' --np '+str(options.np)
        basecmd = basecmd + ' --tstep '+str(options.tstep)
        basecmd = basecmd + ' --co2_file '+options.co2_file
        if (options.aerorcp85):
            basecmd = basecmd + ' --aero_rcp85'
        if (options.ndeprcp85):
            basecmd = basecmd + ' --ndep_rcp85'
        if (options.compiler != ''):
            basecmd = basecmd + ' --compiler '+options.compiler
        basecmd = basecmd + ' --mpilib '+options.mpilib
        basecmd = basecmd + ' --pio_version '+options.pio_version
        basecmd = basecmd+' --caseroot '+caseroot
        basecmd = basecmd+' --runroot '+runroot
        basecmd = basecmd+' --walltime '+str(options.walltime)
        if (options.constraints != ''):
          basecmd = basecmd+' --constraints '+options.constraints
        if (options.hist_vars != ''):
          basecmd = basecmd+' --hist_vars '+options.hist_vars

        if (options.maxpatch_pft!=17):
            basecmd = basecmd + ' --maxpatch_pft '+options.maxpatch_pft
        if (options.pftdynfile != ''):
            basecmd = basecmd + ' --landusefile '+options.pftdynfile

        if (options.var_soilthickness):
            basecmd = basecmd + ' --var_soilthickness'
        if (options.var_list_pft != ''):
            basecmd = basecmd + ' --var_list_pft '+options.var_list_pft
        if (options.no_budgets):
            basecmd = basecmd+' --no_budgets'
        if (options.use_hydrstress):
            basecmd = basecmd+' --use_hydrstress'
        if (options.spruce_treatments):
            basecmd = basecmd+' --spruce_treatments'
        if (myproject != ''):
          basecmd = basecmd+' --project '+myproject
        if (options.domainfile != ''):
          basecmd = basecmd+' --domainfile '+options.domainfile 
        if (options.finitfile != ''):
          basecmd = basecmd+' --finidat '+options.finitfile 

        if (options.clmpf_source_dir !=''):   # for coupling pflotran with elm
            basecmd = basecmd + ' --clmpf_source_dir '+options.clmpf_source_dir
        if (options.clmpf_mode):              # for coupling pflotran with elm
            basecmd = basecmd + ' --clmpf_mode '
            if (options.clmpf_inputdir!=''): 
                basecmd = basecmd + ' --clmpf_inputdir '+options.clmpf_inputdir             
            if (options.clmpf_prefix!=''): 
                basecmd = basecmd + ' --clmpf_prefix '+options.clmpf_prefix

#---------------- build commands for runcase.py -----------------------------

        # define compsets
        # C, CN, CNP
        if (options.c_only):
            nutrients = 'C'
        elif (options.cn_only):
            nutrients = 'CN'
        else: 
            nutrients = 'CNP'
        
        # CENTURY or CTC
        if (options.centbgc):
            decomp_model = 'CNT'
        else:
            decomp_model = 'CTC'

        # ECA or RD 
        if (options.eca):
            mycompset = nutrients+'ECA'+decomp_model
        else:
            mycompset = nutrients+'RD'+decomp_model+'BC'
        #note - RD / ECA in FATES handled with namelist options, not compsets
        if (options.fates):
            if (model_name == 'elm'):
              mycompset = 'ELMFATES'
            else:
              mycompset = 'CLM45ED'
        else:
            mycompset = nutrients+'RD'+decomp_model+'BC'

        # add P during initial spinup
        if (not options.ad_Pinit):
            mycompset_adsp = mycompset.replace('CNP','CN')
        else:
            mycompset_adsp = mycompset
        
        # crop model 
        if (options.crop):
            if (model_name == 'elm'):
              mycompset = 'ELMCNCROP'
            else:
              mycompset = 'CLM45CNCROP'
            mycompset_adsp = mycompset   
        
        # model executable E3SM / CESM 
        myexe = 'e3sm.exe'
        if ('clm5' in options.csmdir):
            mycompset = 'Clm50BgcGs'
            mycompset_adsp = 'Clm50BgcGs'
            myexe = 'cesm.exe'


        # develop calls to runcase.py

        # AD spinup
        cmd_adsp = basecmd+' --ad_spinup --nyears_ad_spinup '+ \
            str(ny_ad)+' --align_year '+str(year_align+1)
        if (int(options.hist_mfilt_spinup) == -999):
            cmd_adsp = cmd_adsp+' --hist_mfilt 1 --hist_nhtfrq -'+ \
            str((endyear-startyear+1)*8760)
        else:
            cmd_adsp = cmd_adsp+' --hist_mfilt '+str(options.hist_mfilt_spinup) \
                   +' --hist_nhtfrq '+str(options.hist_nhtfrq_spinup)
        if (sitenum == 0):
            if (options.exeroot != ''):
                if (os.path.isfile(options.exeroot+'/'+myexe) == False):
                    print('Error:  '+options.exeroot+' does not exist or does '+ \
                          'not contain an executable. Exiting')
                    sys.exit(1)
                else:
                    ad_exeroot = options.exeroot
                    cmd_adsp = cmd_adsp+' --exeroot '+ad_exeroot+' --no_build'
            elif options.batch_build:
                cmd_adsp = cmd_adsp+' --no_build'
        else:
            cmd_adsp = cmd_adsp+' --exeroot '+ad_exeroot+' --no_build'

        if (options.cpl_bypass):
            if (options.crop):
              cmd_adsp = cmd_adsp+' --compset ICB'+mycompset_adsp
              ad_case = site+'_ICB'+mycompset_adsp
            else:
              cmd_adsp = cmd_adsp+' --compset ICB1850'+mycompset_adsp
              ad_case = site+'_ICB1850'+mycompset_adsp
            if (options.sp):
              if (model_name == 'elm'):
                ad_case = site+'_ICBELMBC'
              else:
                ad_case = site+'_ICBCLM45BC'
        else:
            cmd_adsp = cmd_adsp+' --compset I1850'+mycompset_adsp
            ad_case = site+'_I1850'+mycompset_adsp

        if (options.noad == False):
            ad_case = ad_case+'_ad_spinup'
        if (options.makemet):
            cmd_adsp = cmd_adsp+' --makemetdat'
        if (options.spinup_vars):
            cmd_adsp = cmd_adsp+' --spinup_vars'
        if (mycaseid != ''):
            ad_case = mycaseid+'_'+ad_case
        if (sitenum == 0 and options.exeroot == ''):
            ad_exeroot = os.path.abspath(runroot+'/'+ad_case+'/bld')


        # final spinup
        if mycaseid !='':
            basecase=mycaseid+'_'+site
            if (options.cpl_bypass):
                if (options.crop):
                  basecase = basecase+'_ICB'+mycompset
                else:
                  basecase = basecase+'_ICB1850'+mycompset
            else: 
                basecase = basecase+'_I1850'+mycompset
        else:
            if (options.cpl_bypass):
                if (options.crop):
                  basecase = site+'_ICB'+mycompset
                else:
                  basecase=site+'_ICB1850'+mycompset
            else:
                basecase=site+'_I1850'+mycompset
            if (options.sp):
                if (model_name == 'elm'):
                  basecase=site+'_ICBELMBC'
                else:
                  basecase=site+'_ICBCLM45BC'

        if (options.noad):
            cmd_fnsp = basecmd+' --run_units nyears --run_n '+str(fsplen)+' --align_year '+ \
                       str(year_align+1)+' --coldstart'
            if (sitenum > 0):
                cmd_fnsp = cmd_fnsp+' --exeroot '+ad_exeroot+' --no_build'
            if (options.sp):
                cmd_fnsp = cmd_fnsp+' --run_startyear '+str(options.run_startyear)
            if (options.exeroot != ''):
              if (os.path.isfile(options.exeroot+'/'+myexe) == False):
                  print('Error:  '+options.exeroot+' does not exist or does '+ \
                        'not contain an executable. Exiting')
                  sys.exit(1)
              else:
                ad_exeroot=options.exeroot
                cmd_fnsp = cmd_fnsp+' --no_build --exeroot '+ad_exeroot
            elif options.batch_build:
                cmd_fnsp = cmd_fnsp+' --no_build'
        else:
            cmd_fnsp = basecmd+' --finidat_case '+ad_case+ \
                       ' --finidat_year '+str(int(ny_ad)+1)+' --run_units nyears --run_n '+ \
                       str(fsplen)+' --align_year '+str(year_align+1)+' --no_build' + \
                       ' --exeroot '+ad_exeroot+' --nopointdata'

        if (int(options.hist_mfilt_spinup) == -999):
            if (options.sp):
              cmd_fnsp = cmd_fnsp+' --hist_mfilt 365 --hist_nhtfrq -24'
            else:
              cmd_fnsp = cmd_fnsp+' --hist_mfilt 1 --hist_nhtfrq -'+ \
              str((endyear-startyear+1)*8760)
        else:
            cmd_fnsp = cmd_fnsp+' --hist_mfilt '+str(options.hist_mfilt_spinup) \
                   +' --hist_nhtfrq '+str(options.hist_nhtfrq_spinup)

        if (options.cpl_bypass):
            if (options.sp):
              if (model_name == 'elm'):
                cmd_fnsp = cmd_fnsp+' --compset ICBELMBC'
              else:
                cmd_fnsp = cmd_fnsp+' --compset ICBCLM45BC'
            else:
              if (options.crop):
                cmd_fnsp = cmd_fnsp+' --compset ICB'+mycompset
              else:
                cmd_fnsp = cmd_fnsp+' --compset ICB1850'+mycompset
        else:
            cmd_fnsp = cmd_fnsp+' --compset I1850'+mycompset

        if (options.spinup_vars):
                cmd_fnsp = cmd_fnsp+' --spinup_vars'
        #if (options.ensemble_file != '' and options.notrans):	
        #        cmd_fnsp = cmd_fnsp+' --spinup_vars'
        if (options.ensemble_file != '' and options.notrans and options.constraints == ''):	
                cmd_fnsp = cmd_fnsp + ' --postproc_file '+options.postproc_file


        #transient
        if(options.noad and options.exeroot==""):
            # if 'noad' is on, model exe root needs to be in spinup bld directory
            ad_exeroot = os.path.abspath(runroot)+'/'+basecase+'/bld'
        cmd_trns = basecmd+' --finidat_case '+basecase+ \
            ' --finidat_year '+str(fsplen+1)+' --run_units nyears' \
            +' --run_n '+str(translen)+' --align_year '+ \
            str(year_align+1850)+' --hist_nhtfrq '+ \
            options.hist_nhtfrq+' --hist_mfilt '+options.hist_mfilt+' --no_build' + \
            ' --exeroot '+ad_exeroot+' --nopointdata'
        
        if (options.cpl_bypass):
            if (options.crop or options.fates):
              cmd_trns = cmd_trns+' --istrans --compset ICB'+mycompset
            else:
              cmd_trns = cmd_trns+' --compset ICB20TR'+mycompset
        else:
            cmd_trns = cmd_trns+' --compset I20TR'+mycompset
        
        if (options.spinup_vars):
            cmd_trns = cmd_trns + ' --spinup_vars'
        if (options.trans_varlist != ''):
            cmd_trns = cmd_trns + ' --trans_varlist '+options.trans_varlist
        if (options.dailyvars):
            cmd_trns = cmd_trns + ' --dailyvars'
        if (options.ensemble_file != ''):  #Transient post-processing
            cmd_trns = cmd_trns + ' --postproc_file '+options.postproc_file
        if (options.diags):
            cmd_trns = cmd_trns + ' --diags'
        if (not options.nofire):
            #Turn wildfire off in transient simulations (disturbances are known)
            cmd_trns = cmd_trns + ' --nofire'


        #transient phase 2 
        #(CRU-NCEP only, without coupler bypass)
        if ((options.cruncep or options.cruncepv8 or options.gswp3 or options.princeton \
                or options.gswp3_w5e5) and not options.cpl_bypass):
            basecase=basecase.replace('1850','20TR')+'_phase1'
            thistranslen = site_endyear - 1921 + 1
            cmd_trns2 = basecmd+' --trans2 --finidat_case '+basecase+ \
                ' --finidat_year 1921 --run_units nyears --branch ' \
                +' --run_n '+str(thistranslen)+' --align_year 1921'+ \
                ' --hist_nhtfrq '+options.hist_nhtfrq+' --hist_mfilt '+ \
                options.hist_mfilt+' --no_build'+' --exeroot '+ad_exeroot + \
                ' --compset I20TR'+mycompset+' --nopointdata'
            #print(cmd_trns2)


        # experimental manipulation transients, without coupler bypass
        # APW: check align_year is correct, 
        # APW: do we want different outputs? Maybe the full set here and a reduced set for the initial transient?
        elif ((options.eco2_file != '') and not options.cpl_bypass):
            basecase=basecase.replace('1850','20TR')

            # ambient CO2 run 
            cmd_trns2 = basecmd+' --transtag aCO2 --finidat_case '+basecase+ \
                ' --finidat_year '+str(startyear)+' --run_startyear '+str(startyear)+' --run_units nyears ' \
                +' --run_n '+str(ncycle)+' --align_year '+str(startyear)+ \
                ' --hist_nhtfrq '+options.hist_nhtfrq+' --hist_mfilt '+ \
                options.hist_mfilt+' --no_build'+' --exeroot '+ad_exeroot + \
                ' --compset I20TR'+mycompset+' --nopointdata'
          
            # elevated CO2 run 
            basecmd_eco2=basecmd.replace(options.co2_file,options.eco2_file)
            cmd_trns3 = basecmd_eco2+' --transtag eCO2 --finidat_case '+basecase+ \
                ' --finidat_year '+str(startyear)+' --run_startyear '+str(startyear)+' --run_units nyears ' \
                +' --run_n '+str(ncycle)+' --align_year '+str(startyear)+ \
                ' --hist_nhtfrq '+options.hist_nhtfrq+' --hist_mfilt '+ \
                options.hist_mfilt+' --no_build'+' --exeroot '+ad_exeroot + \
                ' --compset I20TR'+mycompset+' --nopointdata'
          

#---------------------------------------------------------------------------------

        #set site environment variable
        os.environ['SITE']=site
        basecase = site
        if (mycaseid != ''):
                basecase = mycaseid+'_'+site
        runcmd('mkdir -p temp')
        runcmd('mkdir -p scripts/'+myscriptsdir)

        mymodel = 'ELM'
        if ('clm5' in csmdir):
            mymodel = 'CLM5'

        #If not the first site, create point data here
        if ((sitenum > 0) and not options.nopointdata):
                print('\n\nCreating point data for '+site+'\n')
                ptcmd = 'python makepointdata.py '+ \
                        ' --site '+site+' --sitegroup '+options.sitegroup+ \
                        ' --ccsm_input '+ccsm_input+' --model '+mymodel
                if (options.nopftdyn):
                    ptcmd = ptcmd+' --nopftdyn'
                if (int(options.mypft) >= 0):
                    ptcmd = ptcmd+' --pft '+str(options.mypft)
                if (options.humhol):
                    ptcmd = ptcmd+' --humhol'
                if (options.marsh):
                    ptcmd = ptcmd+' --marsh'
                result = runcmd(ptcmd)
                if (result > 0):
                    print('Site_fullrun:  Error creating point data for '+site)
                    sys.exit(1)

        #Build Cases
        if (options.noad == False):
            print('\n\nSetting up ad_spinup case\n')
            if (sitenum == 0):
                ad_case_firstsite = ad_case
                result = runcmd(cmd_adsp)
            else:
                ptcmd = 'python case_copy.py --runroot '+runroot+' --case_copy '+ \
                        ad_case_firstsite+' --site_orig '+firstsite +\
                        ' --site_new '+site+' --nyears '+str(ny_ad)+' --spin_cycle ' \
                        +str(endyear-startyear+1)
                result = runcmd(ptcmd)
            if (result > 0):
                print('Site_fullrun:  Error in runcase.py for ad_spinup ')
                sys.exit(1)
        else:
          if (sitenum == 0):
            ad_case_firstsite = ad_case


        if (options.nofnsp == False):
            print('\n\nSetting up final spinup case\n')
            if (sitenum == 0):
                fin_case_firstsite = ad_case_firstsite.replace('_ad_spinup','')
                if (nutrients == 'CNP' and not options.ad_Pinit):
                    fin_case_firstsite = fin_case_firstsite.replace('1850CN','1850CNP')
                print(cmd_fnsp+'\n')
                result = os.system(cmd_fnsp)
            else:
                ptcmd = 'python case_copy.py --runroot '+runroot+' --case_copy '+ \
                        fin_case_firstsite+' --site_orig '+firstsite +\
                        ' --site_new '+site+' --nyears '+str(ny_fin)
                if (not options.sp):
                  ptcmd = ptcmd+' --finidat_year ' \
                        +str(int(ny_ad)+1)+' --spin_cycle '+str(endyear-startyear+1)
                print(ptcmd)
                result = os.system(ptcmd)
                if (result > 0):
                    print('Site_fullrun:  Error in runcase.py final spinup')
                    sys.exit(1)
        else:
            fin_case_firstsite = ad_case_firstsite.replace('_ad_spinup','')
            if (nutrients == 'CNP' and not options.ad_Pinit):
                fin_case_firstsite = fin_case_firstsite.replace('1850CN','1850CNP')


        if (options.notrans == False):
            print('\n\nSetting up transient case\n')
            if (sitenum == 0):
                if (options.crop):
                  tr_case_firstsite = fin_case_firstsite+'_trans'
                else:
                  tr_case_firstsite = fin_case_firstsite.replace('1850','20TR')
                result = runcmd(cmd_trns)
            else:
                 ptcmd = 'python case_copy.py --runroot '+runroot+' --case_copy '+ \
                        tr_case_firstsite+' --site_orig '+firstsite +\
                        ' --site_new '+site+' --finidat_year '+str(int(ny_fin)+1)+ \
                        ' --nyears '+str(translen)
                 result = runcmd(ptcmd)
            if ((options.cruncep or options.cruncepv8 or options.gswp3 or options.princeton) and not options.cpl_bypass):
                 print('\nSetting up transient case phase 2\n')
                 result = runcmd(cmd_trns2)

            if (result > 0):
                print('Site_fullrun:  Error in runcase.py for transient')
                sys.exit(1)

            if ((options.cruncep or options.cruncepv8 or options.gswp3 or options.princeton) and not options.cpl_bypass):
                print('\n\nSetting up transient case phase 2\n')
                print(cmd_trns2)
                result = os.system(cmd_trns2)
                if (result > 0):
                    print('Site_fullrun:  Error in runcase.py for transient 2')
                    sys.exit(1)


            # experiment simulations
            if ((options.eco2_file != '') and not options.cpl_bypass):
                print('\n\nSetting up experiment transient case 2\n')
                result = os.system(cmd_trns2)
                print(cmd_trns2)
                if (result > 0):
                    print('Site_fullrun:  Error in runcase.py for transient 2')
                    sys.exit(1)
                print('\n\nSetting up experiment transient case 3\n')
                print(cmd_trns3)
                result = os.system(cmd_trns3)
                if (result > 0):
                    print('Site_fullrun:  Error in runcase.py for transient 3')
                    sys.exit(1)

                 
        # Create .pbs etc scripts for each case
        # build vector of case aliases 
        case_list = []
        if (options.noad == False):
            case_list.append('ad_spinup')
            if (not options.fates):
              case_list.append('iniadjust')
        if (options.nofnsp == False):
            case_list.append('fn_spinup')
        if (options.diags):
            case_list.append('spinup_diags')
        if (options.notrans == False):
            case_list.append('transient')
            if (options.eco2_file):
                case_list.append('trans_aCO2')
                case_list.append('trans_eCO2')
            if (options.diags):
                case_list.append('trans_diags')
        print('\n\nAliases of cases to be submitted:\n')
        print(case_list)
        print('')
        #sys.exit('temp stop pre submit script copy & edit')


        for c in case_list:
            mysubmit_type = 'qsub'
            groupnum = int(sitenum/npernode)
            if ('cades' in options.machine or 'anvil' in options.machine or 'chrysalis' in options.machine or \
                'compy' in options.machine or 'cori' in options.machine):
                mysubmit_type = 'sbatch'
            if ('ubuntu' in options.machine):
                mysubmit_type = ''
            if ('mymac' in options.machine):
                mysubmit_type = ''
            if ('wsl' in options.machine):
                mysubmit_type = ''
            if ('docker' in options.machine):
                mysubmit_type = ''
            if ((sitenum % npernode) == 0):
                if (os.path.isfile(caseroot+'/'+ad_case_firstsite+'/case.run')):
                    input = open(caseroot+'/'+ad_case_firstsite+'/case.run')
                elif (os.path.isfile(caseroot+'/'+ad_case_firstsite+'/.case.run')):
                    input = open(caseroot+'/'+ad_case_firstsite+'/.case.run')
                elif (os.path.isfile(caseroot+'/'+fin_case_firstsite+'/case.run')):
                    input = open(caseroot+'/'+fin_case_firstsite+'/case.run')
                elif (os.path.isfile(caseroot+'/'+fin_case_firstsite+'/.case.run')):
                    input = open(caseroot+'/'+fin_case_firstsite+'/.case.run')
                elif (os.path.isfile(caseroot+'/'+tr_case_firstsite+'/case.run')):
                    input = open(caseroot+'/'+tr_case_firstsite+'/case.run')
                elif (os.path.isfile(caseroot+'/'+tr_case_firstsite+'/.case.run')):
                    input = open(caseroot+'/'+tr_case_firstsite+'/.case.run')
                else:
                    print(caseroot+'/'+ad_case_firstsite+'/.case.run or /case.run not found.  Aborting')
                    sys.exit(1)
                output = open('./scripts/'+myscriptsdir+'/'+c+'_group'+str(groupnum)+'.pbs','w')
                for s in input:
                    if ("perl" in s or "python" in s):
                        if ('cades' in options.machine \
                            or 'mymac' in options.machine \
                            or 'wsl' in options.machine \
                            or 'docker' in options.machine):
                          output.write("#!/bin/bash -f\n")
                        else:
                          output.write("#!/bin/csh -f\n")
                        timestr=str(int(float(options.walltime)))+':'+str(int((float(options.walltime)- \
                                     int(float(options.walltime)))*60))+':00'
                        if (options.debug):
                            timestr = '00:30:00'
                            if ('compy' in options.machine):
                              timestr='02:00:00'
                            output.write('#SBATCH -p short\n')
                        if (mysubmit_type == 'qsub'):
                            output.write('#PBS -l walltime='+timestr+'\n')
                        elif (mysubmit_type == 'sbatch'):
                            output.write('#SBATCH --time='+timestr+'\n')
                            if ('anvil' in options.machine):
                                output.write('#SBATCH -A condo\n')
                                output.write('#SBATCH -p acme-small\n')
                            elif (myproject != ''):
                                output.write('#SBATCH -A '+myproject+'\n')
                            if ('edison' in options.machine or 'cori' in options.machine):
                                if (options.debug):
                                    output.write('#SBATCH --partition=debug\n')
                                else:
                                    output.write('#SBATCH --partition=regular\n')
                            if ('cades' in options.machine):
                                output.write('#SBATCH -A ccsi\n')
                                output.write('#SBATCH -p batch\n')
                                output.write('#SBATCH --mem='+str(npernode*2)+'G\n')
                                output.write('#SBATCH --ntasks-per-node '+str(npernode)+'\n')
                    elif ("#" in s and "ppn" in s):
                        if ('cades' in options.machine):
                            #if ('diags' in c or 'iniadjust' in c):
                            #    output.write("#PBS -l nodes=1:ppn=1\n")
                            #else:
                            output.write("#PBS -l nodes="+str(int(nnode))+":ppn="+str(int(npernode))+"\n")
                        else:
                            output.write("#PBS -l nodes="+str(int(nnode))+"\n")
                    elif ("#!" in s or "#PBS" in s or "#SBATCH" in s):
                        if ('exclusive' in s):
                          if (options.ensemble_file != ''):
                            output.write(s.replace(firstsite,site))
                        else:
                          output.write(s.replace(firstsite,site))
                input.close()
                output.write("\n")
        
                if (options.machine == 'eos'):
                    output.write('source $MODULESHOME/init/csh\n')
                    output.write('module load nco\n')
                    output.write('module unload python\n')
                    output.write('module load python/2.7.5\n')
                    output.write('module unload PrgEnv-intel\n')
                    output.write('module load PrgEnv-gnu\n')
                    output.write('module load python_numpy\n')
                    output.write('module load python_scipy\n')
                    output.write('module load python_mpi4py/2.0.0\n')
                    output.write('module unload PrgEnv-gnu\n')
                    output.write('module load PrgEnv-intel\n')
                if (options.machine == 'titan'):
                    output.write('source $MODULESHOME/init/csh\n')
                    output.write('module load nco\n')
                    output.write('module load python\n')
                    output.write('module load python_numpy/1.9.2\n')
                    output.write('module load python_scipy/0.15.1\n')
                    output.write('module load python_mpi4py/2.0.0\n')
                if (options.machine == 'edison' or 'cori' in options.machine):
                    output.write('source $MODULESHOME/init/csh\n')
                    output.write('module unload python\n')
                    output.write('module unload scipy\n')
                    output.write('module unload numpy\n')
                    output.write('module load python/2.7-anaconda\n')
                    output.write('module load nco\n')     
                if ('cades' in options.machine):
                    output.write('source $MODULESHOME/init/bash\n')
                    output.write('module unload python\n')
                    output.write('module load python/2.7.12\n')
            else:
                output = open('./scripts/'+myscriptsdir+'/'+c+'_group'+str(groupnum)+'.pbs','a')   
               
            # build full spin compset for writing to submit scripts
            modelst = 'I1850'+mycompset
            if (options.cpl_bypass):
                modelst = 'ICB1850'+mycompset
                if (options.sp):
                  if (model_name == 'elm'):
                    modelst = 'ICBELMBC'
                  else:
                    modelst = 'ICBCLM45BC'
                if (options.crop):
                  if (model_name == 'elm'):
                    modelst = 'ICBELMCNCROP'
                  else:
                    modelst = 'ICBCLM45CNCROP'

            basecase = site
            if (mycaseid != ''):
                basecase = mycaseid+'_'+site

            #Get the software environment for selected machines
            if (sitenum == 0 and ('ad_spinup' in c or (options.noad and 'fn_spinup' in c))):
                if ('ad_spinup' in c):
                  mycasedir=caseroot+'/'+basecase+'_'+modelst.replace('CNP','CN')+'_ad_spinup' 
                else:
                  mycasedir=caseroot+'/'+basecase+'_'+modelst
            if (sitenum % npernode == 0 and ('compy' in options.machine or 'anvil' in options.machine or 'chrysalis' in options.machine)):
              softenvfile = open(mycasedir+'/software_environment.txt','r')
              for line in softenvfile:
                if ('LD_LIBRARY_PATH' in line[0:20]):
                  output.write('setenv '+line.replace('=',' '))
              softenvfile.close()

            #Submission for first site, ad_spinup
            if (sitenum == 0 and 'ad_spinup' in c):
                if (options.ad_Pinit):
                    #output.write("cd "+caseroot+'/'+basecase+"_"+modelst+"_ad_spinup/\n")
                    simsubmitdir='/'+basecase+'_'+modelst+'_ad_spinup/'
                else:
                    #output.write("cd "+caseroot+'/'+basecase+"_"+modelst.replace('CNP','CN')+"_ad_spinup/\n")
                    simsubmitdir='/'+basecase+'_'+modelst.replace('CNP','CN')+'_ad_spinup'
                #if (caseroot == runroot):
                #    simsubmitdir=simsubmitdir+'/case'
                output.write("cd "+caseroot+'/'+simsubmitdir+'\n')

                if options.batch_build and options.exeroot == '':
                    output.write('./xmlchange BUILD_COMPLETE=FALSE\n')
                    output.write("./case.build || exit 1\n")
                output.write("./case.submit --no-batch &\n")
            #Submission for subsequent sites, ad spinup
            elif ('ad_spinup' in c):
                if (options.ad_Pinit):
                    output.write("cd "+runroot+'/'+basecase+"_"+modelst+"_ad_spinup/run\n")
                else:
                    output.write("cd "+runroot+'/'+basecase+"_"+modelst.replace('CNP','CN')+"_ad_spinup/run\n")
                output.write(ad_exeroot+'/'+myexe+' &\n')

            if ('iniadjust' in c):
                output.write("cd "+os.path.abspath(".")+'\n')
                if (options.centbgc):
                    output.write("python adjust_restart.py --rundir "+os.path.abspath(runroot)+ \
                                 '/'+ad_case+'/run/ --casename '+ ad_case+' --restart_year '+ \
                                 str(int(ny_ad)+1)+' --BGC --model_name '+model_name+'\n')
                else:
                    output.write("python adjust_restart.py --rundir "+os.path.abspath(runroot)+ \
                                 '/'+ad_case+'/run/ --casename '+ad_case+' --restart_year '+ \
                                 str(int(ny_ad)+1)+' --model_name '+model_name+'\n')

            if ('spinup_diags' in c):
                 if (options.cpl_bypass):
                     mycompsetcb = 'ICB1850'+mycompset
                 else:
                     mycompsetcb = 'I1850'+mycompset
                 output.write("cd "+os.path.abspath(".")+'\n')
                 plotcmd = "python plotcase.py --site "+site+" --spinup --compset "+mycompsetcb \
                               +" --csmdir "+os.path.abspath(runroot)+" --pdf --yend "+str(int(ny_ad)+30)
                 if (options.compare != ''):
                     plotcmd = plotcmd + ' --case '+mycaseid+','+options.compare
                 else:
                     plotcmd = plotcmd + ' --case '+mycaseid
                 if (options.ad_Pinit):
                     plotcmd = plotcmd + ' --ad_Pinit'
                 output.write(plotcmd+' --vars NEE --ylog\n')
                 output.write(plotcmd+' --vars TLAI,NPP,GPP,TOTVEGC,TOTSOMC\n') 
                 if (options.machine == 'cades'):
                     output.write("scp -r ./plots/"+mycaseid+" acme-webserver.ornl.gov:~/www/single_point/plots\n")

            if (sitenum == 0 and 'fn_spinup' in c):
                output.write("cd "+caseroot+'/'+basecase+"_"+modelst+"\n")
                output.write('./case.submit --no-batch &\n')
            elif ('fn_spinup' in c):
                output.write("cd "+runroot+'/'+basecase+"_"+modelst+"/run\n")
                output.write(ad_exeroot+'/'+myexe+' &\n')

            if (sitenum == 0 and 'transient' in c):
                if (options.crop):
                  output.write("cd "+caseroot+'/'+basecase+"_"+modelst+"_trans\n")
#                elif (options.fates):
#                  output.write("cd "+caseroot+'/'+basecase+"_"+modelst.replace('1850','')+"_trans\n")
                else:
                  output.write("cd "+caseroot+'/'+basecase+"_"+modelst.replace('1850','20TR')+"\n")
                output.write('./case.submit --no-batch &\n')
            elif ('transient' in c):
                if (options.crop):
                  output.write("cd "+runroot+'/'+basecase+"_"+modelst+"_trans/run\n")
#                elif (options.fates):
#                  output.write("cd "+runroot+'/'+basecase+"_"+modelst.replace('1850','')+"_trans/run\n")
                else:
                  output.write("cd "+runroot+'/'+basecase+"_"+modelst.replace('1850','20TR')+"/run\n")
                output.write(ad_exeroot+'/'+myexe+' &\n')

            # APW: possible alternative structure for these if statements, could help simplfy
            elif ('trans_' in c and c != 'trans_diags'):
                if (sitenum == 0):
                    simroot=caseroot
                    simsuffix=''
                    simsubmit='./case.submit --no-batch &\n'
                else: 
                    simroot=runroot
                    simsuffix='/run'
                    simsubmit=runroot+'/'+ad_case_firstsite+'/bld/'+myexe+' &\n'
                if (options.crop):
                  output.write("cd "+simroot+'/'+basecase+"_"+modelst+"_"+c+simsuffix+"\n")
                else:
                  output.write("cd "+simroot+'/'+basecase+"_"+modelst.replace('1850','20TR')+c.replace('trans','')+simsuffix+"\n")
                output.write(simsubmit) 

            if ('trans_diags' in c):
                 if (options.cpl_bypass):
                     if (options.crop or options.fates):
                       mycompsetcb = 'ICB'+mycompset+'_trans'
                     else:
                       mycompsetcb = 'ICB20TR'+mycompset
                 else:
                     mycompsetcb = 'I20TR'+mycompset
                 output2 = open('./scripts/'+myscriptsdir+'/transdiag_'+site+'.csh','w')
                 output.write("cd "+os.path.abspath(".")+'\n')
                 output2.write("cd "+os.path.abspath(".")+'\n')
                 plotcmd = "python plotcase.py --site "+site+" --compset "+mycompsetcb \
                          +" --csmdir "+os.path.abspath(runroot)+" --pdf --yend "+str(site_endyear)
                 if (options.compare != ''):
                     plotcmd = plotcmd + ' --case '+mycaseid+','+options.compare
                 else:
                     plotcmd = plotcmd + ' --case '+mycaseid
                 #average seasonal cycle
                 output2.write(plotcmd+' --vars NEE,GPP,EFLX_LH_TOT,FSH,FPG,FPG_P,FPI,FPI_P,NPP,'+ \
                                    'QOVER --seasonal --obs\n')
                 #seasonal diurnal cycles
                 diurnalvars='NEE,GPP,EFLX_LH_TOT,FSH'
                 output2.write(plotcmd+' --vars '+diurnalvars+' --obs --diurnal --dstart 1 --dend 59 --h1\n')
                 output2.write(plotcmd+' --vars '+diurnalvars+' --obs --diurnal --dstart 60 --dend 151 --h1\n')
                 output2.write(plotcmd+' --vars '+diurnalvars+' --obs --diurnal --dstart 152 --dend 243 --h1\n')
                 output2.write(plotcmd+' --vars '+diurnalvars+' --obs --diurnal --dstart 244 --dend 334 --h1\n')
                 #Interannual variability
                 output2.write(plotcmd+' --vars NEE,GPP,EFLX_LH_TOT,FSH --obs --h4\n')
                 #monthly data
                 output2.write(plotcmd+' --vars NEE,GPP,EFLX_LH_TOT,FSH,FPG,FPG_P,FPI,FPI_P,NPP,QOVER --obs\n')
                 #1850-present
                 output2.write(plotcmd+' --vars TOTLITC,CWDC,TOTVEGC,TOTSOMC --ystart 1850 --h4\n')
                 output2.close()
                 os.system('chmod u+x '+'./scripts/'+myscriptsdir+'/transdiag_'+site+'.csh')
                 output.write('./scripts/'+myscriptsdir+'/transdiag_'+site+'.csh &\n')
            output.write('sleep 5\n')
            output.close()


#sys.exit('temp stop pre-submit')
# submit jobs created by runcase.py 
#======================================================#

        #if ensemble simulations requested, submit jobs created by runcase.py in correct order
        if (options.no_submit == False and options.ensemble_file != ''):
            cases=[]
            #build list of cases for fullrun
            if (options.noad == False):
                 if (options.ad_Pinit):
                    cases.append(basecase+'_'+modelst+'_ad_spinup')
                 else:
                    cases.append(basecase+'_'+modelst.replace('CNP','CN')+'_ad_spinup')

            if (options.nofnsp == False):
                 cases.append(basecase+'_'+modelst)

            if (options.notrans == False):
                #if (options.crop or options.fates):
                if (options.crop):
                  cases.append(basecase+'_'+modelst+'_trans')
                else:
                  cases.append(basecase+'_'+modelst.replace('1850','20TR'))

            job_depend_run=''    
            if (len(cases) > 1 and options.constraints != ''):
              cases=[]    #QPSO will run all cases
              #if (options.crop or options.fates):
              if (options.crop):
                cases.append(basecase+'_'+modelst+'_trans')
              else:
                cases.append(basecase+'_'+modelst.replace('1850','20TR'))
            for thiscase in cases:
                job_depend_run = submit('scripts/'+myscriptsdir+'/ensemble_run_'+thiscase+'.pbs',job_depend= \
                                        job_depend_run, submit_type=mysubmit_type)
        #else:  #submit single job
        #    job_fullrun = submit('temp/site_fullrun.pbs', submit_type=mysubmit_type)
        sitenum = sitenum+1


# Submit PBS scripts for single/multi-site simulations on 1 node
if (options.no_submit == False and options.ensemble_file == ''):
    for g in range(0,int(groupnum)+1):
        job_depend_run=''
        for thiscase in case_list:
            output = open('./scripts/'+myscriptsdir+'/'+thiscase+'_group'+str(g)+'.pbs','a')
            output.write('wait\n')
            if ('trans_diags' in thiscase and options.machine == 'cades'):
                output.write("scp -r ./plots/"+mycaseid+" acme-webserver.ornl.gov:~/www/single_point/plots\n")
            output.close()
            if not options.no_submit:
                if (mysubmit_type == ''):
                    os.system('chmod u+x ./scripts/'+myscriptsdir+'/'+thiscase+'_group'+str(g)+'.pbs')
                    os.system('./scripts/'+myscriptsdir+'/'+thiscase+'_group'+str(g)+'.pbs')
                else:
                    job_depend_run = submit('scripts/'+myscriptsdir+'/'+thiscase+'_group'+str(g)+'.pbs',job_depend= \
                                    job_depend_run, submit_type=mysubmit_type)



# END
