#!/usr/bin/env python

import os, sys, csv, time, math
import numpy as np
import datetime

#Read the parameter list file
def read_parm_list(self, parm_list=''):
    os.chdir(self.OLMTdir)
    if (os.path.exists(parm_list)):
        myfile = open(parm_list,'r')
        self.ensemble_parms=[]
        self.ensemble_pfts=[]
        self.ensemble_pmin=[]
        self.ensemble_pmax=[]
        for s in myfile:
            if (not '#' in s[0:3]):
              vals = s.split()
              self.ensemble_parms.append(vals[0].strip())
              self.ensemble_pfts.append(int(vals[1].strip()))
              self.ensemble_pmin.append(float(vals[2].strip()))
              self.ensemble_pmax.append(float(vals[3].strip()))
        myfile.close()
    else:
        print('parm_list file '+parm_list+' does not exist.  Exiting')
        sys.exit(1)
    self.nparms_ensemble = len(self.ensemble_parms)

#def get_default_parms(self):
#    parm_file = Dataset(self.parm_file,'r')
#    parms_def=[]
#    for p in self.ensemble_parms:
#        parms_def.append(parm_file[p][
    

#Create the samples file
def create_samples(self,sampletype='monte_carlo',nsamples=100,parm_list=''):
    self.nsamples=nsamples
    self.samples=np.zeros((self.nparms_ensemble,self.nsamples), float)
    for i in range(0,self.nsamples):
        for j in range(0,self.nparms_ensemble):
            self.samples[j,i] = self.ensemble_pmin[j]+(self.ensemble_pmax[j]- \
                    self.ensemble_pmin[j])*np.random.rand(1)
    self.ensemble_file = 'parm_samples/mcsamples_'+self.caseid+'_'+str(self.nsamples)+'.txt'
    os.system('mkdir -p parm_samples')
    np.savetxt(self.ensemble_file,np.transpose(self.samples))

def create_ensemble_script(self, walltime=24):
    #Create the PBS script we will submit to run the ensemble
    os.chdir(self.casedir)
    #Get the LD_LIBRARY_PATH from software environment
    softenv = open('software_environment.txt','r')
    for s in softenv:
        if s.split('=')[0].strip() == 'LD_LIBRARY_PATH':
            ldpath = s.split('=')[1].strip()
    softenv.close()
    self.npernode=int(self.xmlquery('MAX_TASKS_PER_NODE'))
    nnodes = int(np.ceil((self.np_ensemble*self.np)/self.npernode))
    myfile = open('case.submit_ensemble','w')
    myfile.write('#!/bin/bash -e\n\n')
    if (self.queue == 'debug'):
        walltime=2
    myfile.write('#SBATCH -t '+str(walltime)+':00:00\n')
    myfile.write('#SBATCH -J '+self.casename+'\n')
    myfile.write('#SBATCH --nodes='+str(nnodes)+'\n')  
    if (self.project != ''):
        myfile.write('#SBATCH -A '+self.project+'\n')
    myfile.write('#SBATCH -p '+self.queue+'\n')
    myfile.write('cd '+self.caseroot+'/'+self.casename+'\n')
    myfile.write('export LD_LIBRARY_PATH='+ldpath+'\n\n')
    myfile.write('./preview_namelists\n\n')
    myfile.write('ulimit -n '+str(self.nsamples+1024)+'\n')
    myfile.write('cd '+self.OLMTdir+'\n')
    myfile.write('./manage_ensemble.py --case '+self.casename+'\n')
    myfile.close()  
    os.system('chmod u+x case.submit_ensemble')
    self.rundir_UQ = self.runroot+'/UQ/'+self.casename

def create_multisite_script(self,sites,scriptdir, walltime=24):
    #Create the PBS script we will submit to run multiple sites
    os.chdir(self.casedir)
    #Get the LD_LIBRARY_PATH from software environment
    softenv = open('software_environment.txt','r')
    for s in softenv:
        if s.split('=')[0].strip() == 'LD_LIBRARY_PATH':
            ldpath = s.split('=')[1].strip()
    softenv.close()
    self.npernode=int(self.xmlquery('MAX_TASKS_PER_NODE'))
    if sites[0] != '':
        nnodes = int(np.ceil(len(sites)/self.npernode))
    else:
        nnodes = int(np.ceil(self.np/self.npernode))
    fname = self.casename.replace('_'+self.site,'')+'.sh'
    myfile = open(fname,'w')
    myfile.write('#!/bin/bash -e\n\n')
    if (self.queue == 'debug'):
        walltime=2
    myfile.write('#SBATCH -t '+str(walltime)+':00:00\n')
    myfile.write('#SBATCH -J '+self.casename.replace('_'+self.site,'')+'\n')
    myfile.write('#SBATCH --nodes='+str(nnodes)+'\n')
    if (self.project != ''):
        myfile.write('#SBATCH -A '+self.project+'\n')
    myfile.write('#SBATCH -p '+self.queue+'\n')
    myfile.write('cd '+self.caseroot+'/'+self.casename+'\n')
    myfile.write('export LD_LIBRARY_PATH='+ldpath+'\n\n')
    for s in sites:
      myfile.write('cd '+self.caseroot+'/'+self.casename.replace(sites[0],s)+'\n')
      myfile.write('./preview_namelists\n')
      myfile.write('cd '+self.runroot+'/'+self.casename.replace(sites[0],s)+'/run\n')
      myfile.write('mkdir -p timing/checkpoints\n')
      #restart file options
      for key in self.case_options.keys():
        if ('restart_' in key):
            var   = key[8:]
            value = str(self.case_options[key])
            if ('*' in value or '+' in value):
                operator=value[0]
                value=value[1:]
                myfile.write('python '+self.OLMTdir+'/modify_netcdf.py --filename '+ \
                    self.finidat+' --var '+var+' --val '+value+ \
                    ' --operator "'+operator+'"\n')
            else:
                myfile.write('python '+self.OLMTdir+'/modify_netcdf.py --filename '+ \
                    self.finidat+' --var '+var+' --val '+value+'\n')
      if (self.noslurm):
        myfile.write(self.exeroot+'/e3sm.exe > e3sm_log.txt &\n\n')
      else:
        myfile.write('srun -n '+str(self.np)+' -c 1 '+self.exeroot+'/e3sm.exe > e3sm_log.txt &\n\n')
    myfile.write('wait\n')
    myfile.close()
    os.system('chmod u+x '+fname)
    return os.path.abspath('./'+fname)

def ensemble_copy(self, ens_num):

  gst=str(100000+int(ens_num))

  # create ensemble directory from original case 
  orig_dir = str(os.path.abspath(self.runroot)+'/'+self.casename+'/run')
  ens_dir  = str(os.path.abspath(self.runroot)+'/UQ/'+self.casename+'/g'+gst[1:])
		
  os.system('mkdir -p '+ens_dir+'/timing/checkpoints')
  os.system('rm -f '+ens_dir+'/*.log.* '+ens_dir+'/*.nc '+ens_dir+'/rpointer*')
  os.system('cp  '+orig_dir+'/*_in* '+ens_dir)
  os.system('cp  '+orig_dir+'/*nml '+ens_dir)
  if (not ('CB' in self.casename)):
    os.system('cp  '+orig_dir+'/*stream* '+ens_dir)
  os.system('cp  '+orig_dir+'/*.rc '+ens_dir)
  os.system('cp  '+orig_dir+'/surf*.nc '+ens_dir)
  os.system('cp  '+orig_dir+'/domain*.nc '+ens_dir)
  os.system('cp  '+orig_dir+'/*para*.nc '+ens_dir)


  # loop through all filenames, change directories in namelists, change parameter values
  for f in os.listdir(ens_dir):
    if (os.path.isfile(ens_dir+'/'+f) and (f[-2:] == 'in' or f[-3:] == 'nml' or 'streams' in f)):
        myinput=open(ens_dir+'/'+f)
        myoutput=open(ens_dir+'/'+f+'.tmp','w')
        for s in myinput:
            if ('fates_paramfile' in s):
                paramfile_orig = ((s.split()[2]).strip("'"))
                if (paramfile_orig[0:2] == './'):
                  paramfile_orig = orig_dir+'/'+paramfile_orig[2:]
                paramfile_new  = ens_dir+'/fates_params_'+gst[1:]+'.nc'
                os.system('cp '+paramfile_orig+' '+paramfile_new)
                os.system('nccopy -3 '+paramfile_new+' '+paramfile_new+'_tmp')
                os.system('mv '+paramfile_new+'_tmp '+paramfile_new)
                myoutput.write(" fates_paramfile = '"+paramfile_new+"'\n")
                fates_paramfile = ens_dir+'/fates_params_'+gst[1:]+'.nc'
            elif ('paramfile' in s and not 'erw' in s):
                paramfile_orig = ((s.split()[2]).strip("'"))
                if (paramfile_orig[0:2] == './'):
                   paramfile_orig = orig_dir+'/'+paramfile_orig[2:]
                paramfile_new  = ens_dir+'/clm_params_'+gst[1:]+'.nc'
                os.system('cp '+paramfile_orig+' '+paramfile_new)
                os.system('nccopy -3 '+paramfile_new+' '+paramfile_new+'_tmp')
                os.system('mv '+paramfile_new+'_tmp '+paramfile_new)
                myoutput.write(" paramfile = '"+paramfile_new+"'\n")
                pftfile = ens_dir+'/clm_params_'+gst[1:]+'.nc'
            elif ('ppmv' in s and 'co2' in self.ensemble_parms):
                myoutput.write(" co2_ppmv = "+str(parm_values[pnum_co2])+'\n')
            elif ('fsoilordercon' in s):
                CNPfile_orig = ((s.split()[2]).strip("'"))
                if (CNPfile_orig[0:2] == './'):
                   CNPfile_orig  = orig_dir+'/'+CNPfile_orig[2:]
                CNPfile_new  = ens_dir+'/CNP_parameters_'+gst[1:]+'.nc'
                os.system('cp '+CNPfile_orig+' '+CNPfile_new)
                os.system('nccopy -3 '+CNPfile_new+' '+CNPfile_new+'_tmp')
                os.system('mv '+CNPfile_new+'_tmp '+CNPfile_new)
                myoutput.write(" fsoilordercon = '"+CNPfile_new+"'\n")
                CNPfile = ens_dir+'/CNP_parameters_'+gst[1:]+'.nc'
            elif ('fsurdat =' in s):
                surffile_orig = ((s.split()[2]).strip("'"))
                if (surffile_orig[0:2] == './'):
                  surffile_orig = orig_dir+'/'+surffile_orig[2:]
                surffile_new = ens_dir+'/surfdata_'+gst[1:]+'.nc'
                os.system('cp '+surffile_orig+' '+surffile_new)
                os.system('nccopy -3 '+surffile_new+' '+surffile_new+'_tmp')
                os.system('mv '+surffile_new+'_tmp '+surffile_new)
                myoutput.write(" fsurdat = '"+surffile_new+"'\n")
                surffile = ens_dir+'/surfdata_'+gst[1:]+'.nc'
            elif ('flanduse_timeseries =' in s):
                #Note - this is for ERW only
                landuse_orig = ((s.split()[2]).strip("'"))
                myoutput.write(" flanduse_timeseries = '"+landuse_orig.replace('ensemble_0','ensemble_'+str(ens_num-1))+"'\n")
            elif ('finidat = ' in s and self.has_finidat):
                finidat_file_path = os.path.abspath(self.runroot)+'/UQ/'+self.dependcase+'/g'+gst[1:]
                finidat_file_name = self.finidat.split('/')[-1]
                #finidat_file_orig = self.finidat
                finidat_file_new  = finidat_file_path+'/'+finidat_file_name 
                #if ('ad_spinup' in self.dependcase): 
                #        os.system('python adjust_restart.py --rundir '+finidat_file_path+' --casename '+ \
                #            self.dependcase)
                #os.system('cp '+finidat_file_orig+' '+finidat_file_new)
                myoutput.write(" finidat = '"+finidat_file_new+"'\n")
                #Make any requested restart modifications
                for key in self.case_options.keys():
                    if ('restart_' in key):
                        var   = key[8:]
                        value = self.case_options[key]
                        ncval = self.getncvar(finidat_file_new, var)
                        if ('*' in value):
                            value = value*ncval
                        if ('+' in value):
                            value = value+ncval
                        self.putncvar(finidat_file_new, var, value)
            elif ('logfile =' in s):
                #Get the current date and time
                now = datetime.datetime.now()
                #Format the date and time in %y%m%d-%H%M%S format
                date_string = now.strftime("%y%m%d-%H%M%S")
                myoutput.write(s.replace('`date +%y%m%d-%H%M%S`',date_string))
            else:
                myoutput.write(s.replace(orig_dir,ens_dir))
        myoutput.close()
        myinput.close()
        os.system(' mv '+ens_dir+'/'+f+'.tmp '+ens_dir+'/'+f)

  pnum = 0
  CNP_parms = ['ks_sorption', 'r_desorp', 'r_weather', 'r_adsorp', 'k_s1_biochem', 'smax', 'k_s3_biochem', \
             'r_occlude', 'k_s4_biochem', 'k_s2_biochem']

  fates_seed_zeroed=[False,False]
  pnum=0
  parm_values = self.samples[:,ens_num-1]
  parm_indices = self.ensemble_pfts
  for p in self.ensemble_parms:
    if ('INI' in p):
      if ('BGC' in self.casename):
         scalevars = ['soil3c_vr','soil3n_vr','soil3p_vr']
      else:
         scalevars = ['soil4c_vr','soil4n_vr','soil4p_vr']
      sumvars = ['totsomc','totsomp','totcolc','totcoln','totcolp']
      for v in scalevars:
         myvar = self.getncvar(finidat_file_new, v)
         myvar = parm_values[pnum] * myvar
         ierr = self.putncvar(finidat_file_new, v, myvar)
    elif (p == 'lai'):
      myfile = surffile
      param = self.getncvar(myfile, 'MONTHLY_LAI')
      param[:,:,:,:] = parm_values[pnum]
      ierr = self.putncvar(myfile, 'MONTHLY_LAI', param)
    elif ('app_rate' in p or 'grain_size' in p):
        #ERW parameters, these are handled by landuse file.
        myfile = 'null'
    elif (p != 'co2'):
      if (p in CNP_parms):
         myfile= CNPfile
      elif ('fates' in p):
         myfile = fates_paramfile
      else:
         myfile = pftfile
      param = self.getncvar(myfile,p)
      if (('fates_prt' in p and 'stoich' in p) or ('fates_turnover' in p and 'retrans' in p)):
        #this is a 2D parameter.
         param[parm_indices[pnum] % 12 , parm_indices[pnum] / 12] = parm_values[pnum]
         param[parm_indices[pnum] % 12 , parm_indices[pnum] / 12] = parm_values[pnum]
      elif ('fates_hydr_p50_node' in p or 'fates_hydr_avuln_node' in p or 'fates_hydr_kmax_node' in p or \
            'fates_hydr_pitlp_node' in p or 'fates_hydr_thetas_node' in p):
         param[parm_indices[pnum] / 12 , parm_indices[pnum] % 12] = parm_values[pnum]
         param[parm_indices[pnum] / 12 , parm_indices[pnum] % 12] = parm_values[pnum]
      elif ('fates_leaf_long' in p or 'fates_leaf_vcmax25top' in p):
         param[0,parm_indices[pnum]] = parm_values[pnum]
      elif (p == 'kmax' or p == 'psi50'):
          #2D parameter, set all segments to the same value
          param[:,parm_indices[pnum]] = parm_values[pnum]
      #elif (p == 'fates_seed_alloc'):
      #    if (not fates_seed_zeroed[0]):
      #       param[:]=0.
      #       fates_seed_zeroed[0]=True
      #    param[parm_indices[pnum]] = parm_values[pnum]
      #elif (p == 'fates_seed_alloc_mature'):
      #    if (not fates_seed_zeroed[1]):
      #       param[:]=0.
      #       fates_seed_zeroed[1]=True
      #    param[parm_indices[pnum]] = parm_values[pnum]             
      elif (p == 'dayl_scaling' or p == 'vcmaxse'):
        os.system('ncap2 -O -s "'+p+' = flnr" '+myfile+' '+myfile)
        print('Creting netcdf variable for '+p)
        param = self.getncvar(myfile,'flnr')
        param[:] = parm_values[pnum]
      elif (p == 'psi50'):
        param[:,parm_indices[pnum]] = parm_values[pnum]
      elif (parm_indices[pnum] > 0):
         param[parm_indices[pnum]] = parm_values[pnum]
      elif (parm_indices[pnum] == 0):
         try:
           param[:] = parm_values[pnum]
         except:
           param = parm_values[pnum]
      ierr = self.putncvar(myfile, p, param, addvar=True)
      #if ('fr_flig' in p):
      #   param=self.getncvar(myfile, 'fr_fcel')
      #   param[parm_indices[pnum]]=1.0-parm_values[pnum]-parm_values[pnum-1]
      #   ierr = self.putncvar(myfile, 'fr_fcel', param)
    pnum = pnum+1

  #ensure FATES seed allocation paramters sum to one
  #if (fates_seed_zeroed[0]):
  #  param = self.getncvar(myfile,'fates_seed_alloc')
  #  param2 = self.getncvar(myfile,'fates_seed_alloc_mature')
  #  for i in range(0,12):
  #    if (param[i] + param2[i] > 1.0):
  #      sumparam= param[i]+param2[i]
  #      param[i]  = param[i]/sumparam
  #      param2[i] = param2[i]/sumparam
  #  ierr = self.putncvar(myfile, 'fates_seed_alloc', param)      
  #  ierr = self.putncvar(myfile, 'fates_seed_alloc_mature', param2)


def plot_ensemble(self, myvar, percentiles=[1, 5, 25, 50, 75, 95, 99]):
    UQ_output = './UQ_output/' + self.casename + '/ensemble'
    os.makedirs(UQ_output, exist_ok=True)  # Ensures the directory exists
    """
    Plots percentiles (99th, 95th, 75th, 50th, 25th, 5th, and 1st) for ensemble data.
    
    Parameters:
        data (numpy.ndarray): 2D array of ensemble data (shape: [ensemble_size, num_time_steps]).
        x_axis (list or numpy.ndarray): x-axis values (e.g., time).
        output_file (str): Path to save the plot.
    """
    # Percentiles to calculate
    data=self.output[myvar].transpose()

    # Calculate percentiles along the ensemble axis
    percentile_values = np.percentile(data, percentiles, axis=0)

    # Define line styles for each percentile
    # (Use the same style for matching pairs: 1/99, 5/95, 25/75, and make 50 bold)
    line_styles = {
        1:  {'linestyle': '--', 'color': 'black',  'linewidth': 2},
        99: {'linestyle': '--', 'color': 'black',  'linewidth': 2},
        5:  {'linestyle': '-.', 'color': 'black', 'linewidth': 2},
        95: {'linestyle': '-.', 'color': 'black', 'linewidth': 2},
        25: {'linestyle': ':',  'color': 'black','linewidth': 2},
        75: {'linestyle': ':',  'color': 'black','linewidth': 2},
        50: {'linestyle': '-',  'color': 'black',   'linewidth': 3},  # Bold line
    }

    # Plot each percentile
    plt.figure(figsize=(10, 6))
    for i, p in enumerate(percentiles):
        style = line_styles[p]
        plt.plot(self.output['taxis'],
                 percentile_values[i, :],
                 linestyle=style['linestyle'],
                 color=style['color'],
                 linewidth=style['linewidth'],
                 label=f'{p}th Percentile')


    # Add labels and legend
    plt.xlabel("Time Step")
    plt.ylabel("Value")
    plt.title("Ensemble Percentiles")
    plt.legend()
    plt.grid(True)

    # Save the plot
    plt.tight_layout()
    plt.savefig(UQ_output+f'/{myvar}_percentiles.png', bbox_inches='tight')
    plt.close()

### END ###
