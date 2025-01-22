#!/usr/bin/env python
import sys,os, time
import numpy as np
import subprocess
import pickle
import model_ELM
from optparse import OptionParser

#Python code used to manage the ensemble simulations 
#  and perform post-processing of model output.

parser = OptionParser()


parser.add_option("--case", dest="case", default="", \
                  help="Case name")
(options, args) = parser.parse_args()

#Load case object
myfile=open('pklfiles/'+options.case+'.pkl','rb')
mycase=pickle.load(myfile)

#get the node file and parse
def get_nodelist():
  mynodes=[]
  nodelist=os.environ['SLURM_JOB_NODELIST'].split('xxx')
  print(nodelist)
  for n in nodelist:
    if ('[' in n):
        node_prefix=n.split('[')[0]
        nodelist2=n.split('[')[1].split(',')
        for n2 in nodelist2:
          if ('-' in n2):
            firstnode=n2.split('-')[0]
            lastnode=n2.split('-')[1].strip(']')
            for nn in range(int(firstnode),int(lastnode)+1):
              if ('baseline' in mycase.machine):
                nstr = str(nn)
              else:
                nstr = str(10000+nn)[1:]
              mynodes.append(node_prefix+nstr)
          else:
              if ('baseline' in mycase.machine):
                nstr=n2.strip(']')
              else:
                nstr=str(10000+int(n2.strip(']')))[1:]
              mynodes.append(node_prefix+nstr)
    else:
        mynodes.append(n)
  return mynodes

def get_node_submit(pactive,process_nodes,mynodes):
    node_submit=0
    for n in range(0,len(mynodes)):
         ctn=0    #Counter for active processes on each node
         for p in range(0,len(processes)):
                if pactive[p] == 1 and process_nodes[p] == n:
                    ctn=ctn+1
         if (ctn < mycase.npernode/mycase.np):
             #If this node is not full, submit
             node_submit=n
    return(node_submit)

def check_run_success(n):
    success=False
    jobst = str(100000+n)
    rundir = mycase.runroot+'/UQ/'+mycase.casename+'/g'+jobst[1:]
    yst = str(10000+mycase.startyear+mycase.run_n)[1:]
    if (os.path.isfile(rundir+'/'+mycase.casename+'.elm.r.'+yst+'-01-01-00000.nc')):
        success=True
    return success

def active_processes(processes,process_jobnum,process_hang):
    """Returns the number of processes that are still running."""
    pactive=[]
    n=0
    for process in processes:
        if process.poll() is None:  # None means the process is still running
            #Check if final restart file created
            pactive.append(1)
            if (check_run_success(process_jobnum[n])):
                process_hang[n] = process_hang[n]+1
            if (process_hang[n] > 30):
                process.kill()  # Force kill the process
        else:
            pactive.append(0)
            #Post-process ensemble member if it hasn't yet been done
            if (mycase.postprocessed[n] == 0):
                print(n, check_run_success(process_jobnum[n]))
                if (check_run_success(process_jobnum[n])):
                    ierr = postprocess_ensemble(process_jobnum[n])
                else:
                    print('Ensemble member '+str(process_jobnum[n])+ \
                            'Failed to complete')
                mycase.postprocessed[n] = 1
        n=n+1
    return pactive

def postprocess_ensemble(n):
  #Postprocess
  if (mycase.postproc_vars != []):
      for v in mycase.postproc_vars:
        hnum=1
        mypfts=[0]
        if ('_pft' in v):
            #PFT level outputs requested
            hnum=2
            mypfts=mycase.postproc_pfts
        for p in mypfts:
          if (mycase.postproc_freq == 'daily'):  #default
            mycase.postprocess(v, ens_num=n,startyear=mycase.postproc_startyear, \
                  endyear=mycase.postproc_endyear,index=p,hnum=hnum)
          elif (mycase.postproc_freq == 'monthly'):  #monthly
            mycase.postprocess(v, ens_num=n,startyear=mycase.postproc_startyear, \
                  endyear=mycase.postproc_endyear,index=p,hnum=hnum, dailytomonthly=True)
          elif (mycase.postproc_freq == 'annual'):  #annual
            mycase.postprocess(v, ens_num=n,startyear=mycase.postproc_startyear, \
                  endyear=mycase.postproc_endyear,index=p,hnum=hnum, annualmean=True)
  return 0

workdir = os.getcwd()

processes=[]
process_jobnum=[]
process_hang=[]    #Keep track of how long process has been hanging
mycase.postprocessed=np.zeros([mycase.nsamples],int)
n_job = 1
if (mycase.noslurm == False):
    process_nodes = []
    mynodes = get_nodelist()

#Run the simulations 
while (n_job <= mycase.nsamples):
  pactive = active_processes(processes,process_jobnum,process_hang)
  if (sum(pactive) < int(mycase.np_ensemble)):
    jobst = str(100000+n_job)
    rundir = mycase.runroot+'/UQ/'+mycase.casename+'/g'+jobst[1:]+'/'
    log_file_path = f"{rundir}e3sm_log.txt"
    #Copy relevant files
    mycase.ensemble_copy(n_job)
    with open(log_file_path, "w") as log_file:
       if (mycase.noslurm == False):
         node_submit=get_node_submit(pactive,process_nodes,mynodes)
         command = ['srun -n '+str(mycase.np)+' -c 1 -w '+mynodes[node_submit]+' '+mycase.exeroot+'/e3sm.exe']
         process_nodes.append(node_submit)
       else:
         command = [mycase.exeroot+'/e3sm.exe']
       process = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT, cwd=rundir, stdout=log_file)
       processes.append(process)
       process_jobnum.append(n_job)
       process_hang.append(0)
    n_job=n_job+1
  else:
    time.sleep(1)

while (sum(pactive) > 0):
    pactive = active_processes(processes,process_jobnum,process_hang)
    time.sleep(1)

mycase.create_pkl()

#Train surrogate models
mycase.train_surrogate(mycase.postproc_vars)

#run GSA
mycase.GSA(mycase.postproc_vars)

#Save postprocessed output
mycase.create_pkl()



