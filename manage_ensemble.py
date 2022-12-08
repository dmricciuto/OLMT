#!/usr/bin/env python
import sys,os, time
import numpy as np
import netcdf4_functions as nffun
import subprocess
from mpi4py import MPI
from optparse import OptionParser

#MPI python code used to manage the ensemble simulations 
#  and perform post-processing of model output.
#  DMRicciuto 7/14/2016

parser = OptionParser()

parser.add_option("--runroot", dest="runroot", default="../../run", \
                  help="Directory where the run would be created")
parser.add_option("--exeroot", dest="exeroot", default="../../run", \
                  help="Directory where the executable would be created")
parser.add_option("--n_ensemble", dest="n", default=0, \
                  help="Number of ensemble members")
parser.add_option("--case", dest="casename", default="", \
                  help="Name of case")
parser.add_option("--ens_file", dest="ens_file", default="", \
                  help="Name of samples file")
parser.add_option("--mc_ensemble", dest="mc_ensemble", default=0, \
                  help = 'Create monte carlo ensemble')
parser.add_option("--microbe", dest="microbe", default = False, action="store_true", \
                  help = 'CNP mode - initialize P pools')
parser.add_option('--model_name', dest='model_name', default="clm2", \
                    help='Model name used in restart file (clm2 or elm)')
parser.add_option("--postproc_file", dest="postproc_file", default="", \
                  help="Location of post_processing info")
parser.add_option("--postproc_only", dest="postproc_only", default=False, \
                  action="store_true", help='Only do post-processing')
parser.add_option("--parm_list", dest="parm_list", default='parm_list', \
                  help = 'File containing list of parameters to vary')
parser.add_option("--cnp", dest="cnp", default = False, action="store_true", \
                  help = 'CNP mode - initialize P pools')
parser.add_option("--site", dest="site", default='', \
                  help = 'Site name')
parser.add_option("--spruce_treatments", dest="spruce_treatments", default=False, \
                  action='store_true', help = 'Run 11 SPRUCE treatment simulations')
parser.add_option('--run_uq', dest="run_uq", default=True, action="store_true", \
                  help = 'Run sensitivity analysis using UQTk')

(options, args) = parser.parse_args()

options.n = int(options.n)

#Get number of samples from ensemble file
if (os.path.isfile(options.ens_file)):
    if (options.n == 0):
        #get # of lines
        myinput=open(options.ens_file)
        for s in myinput:
            options.n = options.n+1
        myinput.close()
else:
    if (not options.postproc_only):
      if (int(options.mc_ensemble) > 0):
        options.n = int(options.mc_ensemble)
        caseid = options.casename.split('_')[0]
        if (options.ens_file == ''):
          options.ens_file = 'mcsamples_'+caseid+'_'+str(options.n)+'.txt'
        print('Creating Monte Carlo ensemble with '+str(options.n)+' members')
      else:
        print('ensemble file does not exist.  Exiting')
        sys.exit()
    else:
      print('Ensemble file not provided')
      print('Getting parameter information from output files')

#Define function to perform ensemble member post-processing
def postproc(myvars, myyear_start, myyear_end, myday_start, myday_end, myavg, \
             myfactor, myoffset, mypft, mytreatment, thisjob, runroot, case, pnames, ppfts, data, parms):
    baserundir = options.runroot+'/UQ/'+case+'/g'+str(100000+thisjob)[1:]+'/'
    index=0
    ierr = 0
    thiscol = 0
    print(thisjob)
    for v in myvars:
        rundir=baserundir
        if (mytreatment[index] != 'NA'):
          rundir = rundir+mytreatment[index]+'/'
        ndays_total = 0
        output = []
        n_years = myyear_end[index]-myyear_start[index]+1
        npy=1
        for y in range(myyear_start[index],myyear_end[index]+1):
            if (mypft[index] <= 0 or 'PFT' in v):
              fname = rundir+case+'.'+options.model_name+'.h0.'+str(10000+y)[1:]+'-01-01-00000.nc'
              myindex = max(0,mypft[index])
              hol_add = 1
            else:
              fname = rundir+case+'.'+options.model_name+'.h1.'+str(10000+y)[1:]+'-01-01-00000.nc'
              myindex = mypft[index]
              hol_add = 17
            if (os.path.exists(fname)):
              mydata = nffun.getvar(fname,v) 
              if ('ZWT' in v):
                mydata2 = nffun.getvar(fname,'H2OSFC')
              if (len(mydata) < 10):
                npy = 1 
              elif (len(mydata) >= 365):    #does not currently allow hourly
                npy = 365
            else:
              #print(fname)
              mydata = np.zeros([npy,34], float)+np.NaN
            #get output and average over days/years
            n_days = myday_end[index]-myday_start[index]+1
            ndays_total = ndays_total + n_days
            #get number of timesteps per output file
            #print(v, n_days, ndays_total)
        
            if (npy == 365):
                for d in range(myday_start[index]-1,myday_end[index]):
                    if ('US-SPR' in case and 'ZWT' in v):
                      #Use hollows for water table height
                      output.append(mydata[d][myindex+hol_add]*myfactor[index] \
                             +myoffset[index]+mydata2[d][myindex+hol_add]/1000.)
                    elif ('US-SPR' in case):
                      output.append(0.25*(mydata[d][myindex+hol_add]*myfactor[index] \
                             +myoffset[index]) + 0.75*(mydata[d][myindex]*myfactor[index] \
                             +myoffset[index]))
                    else:
                      output.append(mydata[d][myindex]*myfactor[index] \
                             +myoffset[index])
            elif (npy == 1):                    #Assume annual output (ignore days)
               for d in range(myday_start[index]-1,myday_end[index]):    #28-38 was myindex
                 if ('SCPF' in v):
                   output.append(sum(mydata[0,28:38])/10.0*myfactor[index]+myoffset[index])
                 elif ('NPLANT_SCLS' in v):
                   output.append(sum(mydata[0,1:])*myfactor[index]+myoffset[index])
                 elif ('SCLS' in v):
                    output.append(sum(mydata[0,:])*myfactor[index]+myoffset[index])
                 else:
                   try:
                     output.append(mydata[0,myindex]*myfactor[index]+myoffset[index])
                   except:
                     output.append(np.NaN)
        for i in range(0,int(ndays_total/myavg[index])):
            data[thiscol] = sum(output[(i*myavg[index]):((i+1)*myavg[index])])/myavg[index]
            thiscol=thiscol+1
        index=index+1

    #get the parameters
    if (options.microbe):
      pfname =baserundir+'microbepar_in'
      pnum=0
      for p in pnames:
        myinput = open(pfname, 'r')
        for s in myinput:
          if (p == s.split()[0]):
            parms[pnum] = s.split()[1]
        myinput.close()
        pnum=pnum+1
    else:
      pfname = baserundir+'clm_params_'+str(100000+thisjob)[1:]+'.nc'
      #pfname_def = baserundir+'clm_params.nc'
      fpfname = baserundir+'fates_params_'+str(100000+thisjob)[1:]+'.nc'
      sfname = baserundir+'surfdata_'+str(100000+thisjob)[1:]+'.nc'
      pnum=0
      for p in pnames:
         if (p == 'lai'):     #Surface data file
           mydata = nffun.getvar(sfname,'MONTHLY_LAI')
           parms[pnum] = mydata[0,0,0,0]
         elif (p == 'co2'):   #CO2 value from namelist
           lnd_infile = open(baserundir+'lnd_in','r')
           for s in lnd_infile:
             if ('co2_ppm' in s):
               ppmv = float(s.split()[2])
           parms[pnum] = ppmv
           lnd_infile.close()
         elif ('fates' in p):   #fates parameter file
           mydata = nffun.getvar(fpfname,p) 
           if (int(ppfts[pnum]) >= 0):
             if ('fates_prt_nitr_stoich_p1' in p):
               #this is a 2D parameter.
               parms[pnum] = mydata[int(ppfts[pnum])/ 12 , int(ppfts[pnum]) % 12] 
             elif ('fates_hydr_p50_node' in p or 'fates_hydr_avuln_node' in p or \
                   'fates_hydr_kmax_node' in p or 'fates_hydr_pitlp_node' in p or \
                   'fates_hydr_thetas_node' in p):
               parms[pnum] = mydata[int(ppfts[pnum]) / 12 , int(ppfts[pnum]) % 12]
             elif ('fates_leaf_long' in p or 'fates_leaf_vcmax25top' in p):
               parms[pnum] = mydata[0,int(ppfts[pnum])] 
             elif (p == 'fates_seed_alloc'):
             #  if (not fates_seed_zeroed[0]):
             #    param[:]=0.
             #    fates_seed_zeroed[0]=True
               parms[pnum] = mydata[int(ppfts[pnum])] 
             elif (p == 'fates_seed_alloc_mature'):
             #  if (not fates_seed_zeroed[1]):
             #    param[:]=0.
             #    fates_seed_zeroed[1]=True
               parms[pnum] = mydata[int(ppfts[pnum])] 
             elif (int(ppfts[pnum]) > 0):
               parms[pnum] = mydata[int(ppfts[pnum])]
             elif (int(ppfts[pnum]) == 0):
               try:
                 parms[pnum] = mydata[int(ppfts[pnum])] 
               except:
                 parms[pnum] = mydata
           else:
             try:
               parms[pnum] = mydata[0]
             except:
               parms[pnum] = mydata
         else:                #Regular parameter file
           mydata = nffun.getvar(pfname,p) 
           if (int(ppfts[pnum]) > 0):
             if (p == 'psi50'):
               parms[pnum] = mydata[0,int(ppfts[pnum])]
             else:
               parms[pnum] = mydata[int(ppfts[pnum])]
           elif(int(ppfts[pnum]) <= 0):
             try:
               parms[pnum] = mydata[0]
             except:
               parms[pnum] = mydata
         pnum=pnum+1

    return ierr
            

comm=MPI.COMM_WORLD
rank=comm.Get_rank()
size=comm.Get_size()

workdir = os.getcwd()

#get postproc info
do_postproc=False
if (os.path.isfile(options.postproc_file)):
    do_postproc=True
    myvars=[]
    myyear_start=[]
    myyear_end=[]
    myday_start=[]
    myday_end=[]
    myavg_pd=[]
    myfactor=[]
    myoffset=[]
    mypft=[]
    myobs=[]
    myobs_err=[]
    mytreatment=[]
    time.sleep(rank*0.2)
    postproc_input = open(options.postproc_file,'r')
    data_cols = 0
    for s in postproc_input:
        if (s[0:1] != '#'):
            myvars.append(s.split()[0])
            myyear_start.append(int(s.split()[1]))
            myyear_end.append(int(s.split()[2]))
            myday_start.append(int(s.split()[3]))
            myday_end.append(int(s.split()[4]))
            myavg_pd.append(int(s.split()[5]))
            myfactor.append(float(s.split()[6]))
            myoffset.append(float(s.split()[7]))
            if (len(s.split()) >= 9):
              mypft.append(int(s.split()[8]))
            else:
              mypft.append(-1)
            if (len(s.split()) >= 11):
              myobs.append(float(s.split()[9]))
              myobs_err.append(float(s.split()[10]))
            else: 
              myobs.append(-9999)
              myobs_err.append(-9999)
            if (len(s.split()) == 12):        
              mytreatment.append(s.split()[11])     
            else:
              mytreatment.append('NA')
            days_total = (int(s.split()[2]) - int(s.split()[1])+1)*(int(s.split()[4]) - int(s.split()[3])+1)        
            data_cols = int(round(data_cols + days_total / int(s.split()[5])))
            print('DATA_COLS',data_cols)
    print(mytreatment)
    if (rank == 0):
        data = np.zeros([data_cols,options.n], float)-999
    data_row = np.zeros([data_cols], float)-999
    postproc_input.close()

#get the parameter names
pnames=[]
ppfts=[]
pmin=[]
pmax=[]
pfile = open(options.parm_list,'r')
nparms = 0
for s in pfile:
  pnames.append(s.split()[0])
  ppfts.append(s.split()[1])
  pmin.append(s.split()[2])
  pmax.append(s.split()[3])
  nparms = nparms+1
pfile.close()
parm_row = np.zeros([nparms], float)-999
if (rank == 0):
  parms = np.zeros([nparms, options.n],float)-999
  sse_ensemble = np.zeros([options.n], float)-999      

niter = 1

if (rank == 0):

    #--------------------------Perform the model simulations---------------------
    for thisiter in range(0,niter):
      n_done = 0
  
      #send first np-1 jobs where np is number of processes
      for n_job in range(1,size):
          comm.send(n_job, dest=n_job, tag=1)
          comm.send(0,     dest=n_job, tag=2)
          if (options.postproc_only == False):
              time.sleep(0.2)
      #Assign rest of jobs on demand
      for n_job in range(size,options.n+1):
          process = comm.recv(source=MPI.ANY_SOURCE, tag=3)
          thisjob = comm.recv(source=process, tag=4)
          if (do_postproc):
              data_row = comm.recv(source=process, tag=5)
              data[:,thisjob-1] = data_row
              parm_row = comm.recv(source=process, tag=6)
              parms[:,thisjob-1] = parm_row
          n_done = n_done+1
          comm.send(n_job, dest=process, tag=1)
          comm.send(0,     dest=process, tag=2)
      #receive remaining messages and finalize
      while (n_done < options.n):
          process = comm.recv(source=MPI.ANY_SOURCE, tag=3)
          thisjob = comm.recv(source=process, tag=4)
          if (do_postproc):
              data_row = comm.recv(source=process, tag=5)
              data[:,thisjob-1] = data_row
              parm_row = comm.recv(source=process, tag=6)
              parms[:,thisjob-1] = parm_row
          n_done = n_done+1
          comm.send(-1, dest=process, tag=1)
          comm.send(-1, dest=process, tag=2)


    #---------------------------Output post-processing---------------------------
    if (do_postproc):
        data_out = data.transpose()
        parm_out = parms.transpose()
        good=[]
        for i in range(0,options.n):
          #only save valid runs (no NaNs)
          if not np.isnan(sum(data_out[i,:])):
            good.append(i)
        data_out = data_out[good,:]
        parm_out = parm_out[good,:]
        np.savetxt(options.casename+'_postprocessed.txt', data_out)
        #UQ-ready outputs (80% of data for traning, 20% for validation)
        UQ_output = 'UQ_output/'+options.casename
        os.system('mkdir -p '+UQ_output+'/data')
        np.savetxt(UQ_output+'/data/ytrain.dat', data_out[0:int(len(good)*0.8),:])
        np.savetxt(UQ_output+'/data/yval.dat',   data_out[int(len(good)*0.8):,:])
        np.savetxt(UQ_output+'/data/ptrain.dat', parm_out[0:int(len(good)*0.8),:])
        np.savetxt(UQ_output+'/data/pval.dat', parm_out[int(len(good)*0.8):,:])
        if (len(myobs) > 0):
          obs_out=open(UQ_output+'/data/obs.dat','w')
          for i in range(0,len(myobs)): 
            obs_out.write(str(myobs[i])+' '+str(myobs_err[i])+'\n')
          obs_out.close()       
        myoutput = open(UQ_output+'/data/pnames.txt', 'w')
        eden_header=''
        pnum=0      
        for p in pnames:
          if ((pnum == 0 and pnames[pnum+1] == p) or p == pnames[pnum-1]):
            myoutput.write(p+'_'+str(mypft[pnum])+'\n')
          else:
            myoutput.write(p+'\n')
          pnum=pnum+1
          eden_header=eden_header+p+','
        myoutput.close()
        myoutput = open(UQ_output+'/data/outnames.txt', 'w')
        vlast=''
        for v in myvars:
          #if v != vlast:
          #  vcount=0
          #  vlast=v
          #if (myvars.count(v) > 1):
          #  myoutput.write(v+'_'+str(vcount)+'\n')
          #  vcount=vcount+1
          #else:
          myoutput.write(v+'\n')
          eden_header=eden_header+v+','
        myoutput.close()

        os.system('mkdir -p '+UQ_output+'/GSA')
        myoutput = open(UQ_output+'/data/param_range.txt', 'w')
        myoutput2 = open(UQ_output+'/GSA/param_range.txt', 'w')
        for p in range(0,len(pmin)):
          myoutput.write(pmin[p]+' '+pmax[p]+'\n')
          myoutput2.write(pnames[p]+' '+pmin[p]+' '+pmax[p]+'\n')
        myoutput.close()
        myoutput2.close()
        print(np.hstack((parm_out,data_out)))
        np.savetxt(UQ_output+'/data/foreden.csv', np.hstack((parm_out,data_out)), delimiter=',', header=eden_header[:-1])
        if (options.run_uq):
          #Run the sensitivity analysis using UQTk
          #os.system('cp UQTk_scripts/*.x '+UQ_output+'/')
          #os.chdir(UQ_output)
          #os.system('./run_sensitivity.x')
          #os.system('mkdir -p UQTk_output')
          #os.system('mkdir -p UQTk_plots')
          #os.system('mkdir -p UQTk_scripts')
          #os.system('mv *.eps UQTk_plots')
          #os.system('mv *.x UQTk_scripts')
          #os.system('mv *.tar *.pk UQTk_output')
          #os.chdir('../..')
          #Create the surrogate model
          os.system('python surrogate_NN.py --case '+options.casename)
          #Run the senstivity analysis using SALib
          os.system('python run_GSA.py --case '+options.casename)
          if (max(myobs_err) > 0):
            #Run the MCMC calibration on surrogate model if data provided
            os.system('python MCMC.py --case '+options.casename+' --parm_list '+options.parm_list)
    MPI.Finalize()

#--------------------- Slave process (individual ensemble members) --------------
else:
  for thisiter in range(0,niter):
    status=0
    while status == 0:
        myjob = comm.recv(source=0, tag=1)
        status = comm.recv(source=0, tag=2) 

        if (status == 0):
            if (options.postproc_only == False):
                cnp = 'False'
                if (options.cnp):
                    cnp='True'
                mycases=[]
                mycases.append(options.casename)
                for c in mycases:
                  os.chdir(workdir)
                  #Python script to set up the ensemble run directory and manipulate parameters
                  os.system('python ensemble_copy.py --case '+c+' --runroot '+ \
                        options.runroot +' --ens_num '+str(myjob)+' --ens_file '+options.ens_file+ \
                        ' --parm_list '+options.parm_list+' --cnp '+cnp+' --site '+options.site+' --model_name '+ \
                        options.model_name)
                  jobst = str(100000+int(myjob))
                  rundir = options.runroot+'/UQ/'+c+'/g'+jobst[1:]+'/'
                  os.chdir(rundir)
                  #Run the executable
                  exedir = options.exeroot
                  if os.path.isfile(exedir+'/acme.exe'):
                     os.system(exedir+'/acme.exe > acme_log.txt')
                  elif os.path.isfile(exedir+'/e3sm.exe'):
                     os.system(exedir+'/e3sm.exe > e3sm_log.txt')
                  elif os.path.isfile(exedir+'/cesm.exe'):
                     os.system(exedir+'/cesm.exe > cesm_log.txt')
                  if (options.spruce_treatments):
                    #Transient/SP case should be set up produce 2015 restart file
                    #Then we will loop over 11 cases and put results into subdirectories.
                    treatments=['TAMB','T0.00','T2.25','T4.50','T6.75','T9.00', \
                                'T0.00CO2','T2.25CO2','T4.50CO2','T6.75CO2','T9.00CO2']
                    plots=[7,6,20,13,8,17,19,11,4,16,10]
                    os.system('cp lnd_in lnd_in_orig')
                    os.system('cp drv_in drv_in_orig')
                    for t in range(0,len(treatments)):
                      lnd_in_old=open('lnd_in_orig','r')
                      lnd_in_new=open('lnd_in','w')
                      pst = str(100+plots[t])[1:]
                      for s in lnd_in_old:
                        if ('finidat =' in s):
                          lnd_in_new.write(" finidat = './"+c+"."+options.model_name+".r.2015-01-01-00000.nc'\n")
                        elif ('metdata_bypass' in s):
                          lnd_in_new.write(s[:-2]+'/plot'+pst+"'\n")
                          if ('CO2' in treatments[t]):
                            lnd_in_new.write(' add_co2 = 500\n')
                            lnd_in_new.write(" startdate_add_co2 = '20160315'\n") 
                        elif ('landuse_timeseries' in s):
                          lnd_in_new.write(s.replace('plot07','plot'+pst))
                        else:
                          lnd_in_new.write(s)
                      lnd_in_old.close()
                      lnd_in_new.close()
                      drv_in_old=open(rundir+'/drv_in_orig','r')
                      drv_in_new=open(rundir+'/drv_in','w')
                      for s in drv_in_old:
                        if ('stop_n' in s):
                          drv_in_new.write(' stop_n = 7\n')
                        elif ('restart_n' in s):
                          drv_in_new.write(' restart_n = 7\n')
                        elif ('start_ymd' in s):
                          drv_in_new.write(' start_ymd = 20150101\n')
                        else:
                          drv_in_new.write(s)
                      drv_in_new.close()
                      drv_in_old.close()
                      os.system('mkdir '+rundir+'/'+treatments[t])
                      os.system(exedir+'/e3sm.exe > e3sm_log_'+treatments[t]+'.txt')
                      os.system('cp *.'+options.model_name+'.h?.20[1-2]*.nc '+treatments[t])
            if (do_postproc):
                ierr = postproc(myvars, myyear_start, myyear_end, myday_start, \
                         myday_end, myavg_pd, myfactor, myoffset, mypft, mytreatment, myjob, \
                         options.runroot, options.casename, pnames, ppfts, data_row, parm_row)
                comm.send(rank, dest=0, tag=3)
                comm.send(myjob, dest=0, tag=4)
                comm.send(data_row, dest=0, tag=5)
                comm.send(parm_row, dest=0, tag=6)
            else:
                comm.send(rank,  dest=0, tag=3)
                comm.send(myjob, dest=0, tag=4)
  MPI.Finalize()
