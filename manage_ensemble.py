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
parser.add_option("--constraints", dest="constraints", default="", \
                  help="Directory containing model constraints")
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
parser.add_option("--site", dest="site", default='parm_list', \
                  help = 'Site name')
parser.add_option('--run_uq', dest="run_uq", default=True, action="store_true", \
                  help = 'Run sensitivity analysis using UQTk')

(options, args) = parser.parse_args()

options.n = int(options.n)

options.do_QPSO = False
if (options.constraints != ''):
  options.do_QPSO = True
  if (options.n == 0):
    print('QPSO population not set.  Setting to 32')
    options.mc_ensemble = 32

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
      if (options.mc_ensemble > 0):
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
             myfactor, myoffset, mypft, thisjob, runroot, case, pnames, ppfts, data, parms):
    rundir = options.runroot+'/UQ/'+case+'/g'+str(100000+thisjob)[1:]+'/'
    index=0
    ierr = 0
    thiscol = 0
    print(thisjob)
    for v in myvars:
        ndays_total = 0
        output = []
        n_years = myyear_end[index]-myyear_start[index]+1
        npy=1
        for y in range(myyear_start[index],myyear_end[index]+1):
            if (mypft[index] <= 0):
              fname = rundir+case+'.'+options.model_name+'.h0.'+str(10000+y)[1:]+'-01-01-00000.nc'
              myindex = 0
              hol_add = 1
            else:
              fname = rundir+case+'.'+options.model_name+'.h1.'+str(10000+y)[1:]+'-01-01-00000.nc'
              myindex = mypft[index]
              hol_add = 17
            if (os.path.exists(fname)):
              mydata = nffun.getvar(fname,v) 
              if (len(mydata) < 10):
                npy = 1 
              elif (len(mydata) >= 365):    #does not currently allow hourly
                npy = 365
            else:
              print(fname)
              mydata = np.zeros([npy,34], np.float)+np.NaN
            #get output and average over days/years
            n_days = myday_end[index]-myday_start[index]+1
            ndays_total = ndays_total + n_days
            #get number of timesteps per output file
            
            if (npy == 365):
                for d in range(myday_start[index]-1,myday_end[index]):
                    if ('US-SPR' in case):
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
                 else:
                   try:
                     output.append(mydata[0,myindex]*myfactor[index]+myoffset[index])
                   except:
                     output.append(np.NaN)
        for i in range(0,ndays_total/myavg[index]):
            data[thiscol] = sum(output[(i*myavg[index]):((i+1)*myavg[index])])/myavg[index]
            thiscol=thiscol+1
        index=index+1

    #get the parameters
    if (options.microbe):
      pfname = rundir+'microbepar_in'
      pnum=0
      for p in pnames:
        myinput = open(pfname, 'r')
        for s in myinput:
          if (p == s.split()[0]):
            parms[pnum] = s.split()[1]
        myinput.close()
        pnum=pnum+1
    else:
      pfname = rundir+'clm_params_'+str(100000+thisjob)[1:]+'.nc'
      fpfname = rundir+'fates_params_'+str(100000+thisjob)[1:]+'.nc'
      sfname = rundir+'surfdata_'+str(100000+thisjob)[1:]+'.nc'
      pnum=0
      for p in pnames:
         if (p == 'lai'):     #Surface data file
           mydata = nffun.getvar(sfname,'MONTHLY_LAI')
           parms[pnum] = mydata[0,0,0,0]
         elif (p == 'co2'):   #CO2 value from namelist
           lnd_infile = open(rundir+'lnd_in','r')
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
             parms[pnum] = mydata[int(ppfts[pnum])]
           elif(int(ppfts[pnum]) <= 0):
             try:
               parms[pnum] = mydata[0]
             except:
               parms[pnum] = mydata
         pnum=pnum+1

    return ierr
            

def calc_costfucntion(constraints, thisjob, runroot, case):
  #Calculate cost function value (SSE) given the data constraints in the provided directory
  rundir = runroot+'/UQ/'+case+'/g'+str(100000+thisjob)[1:]+'/'
  sse = 0
  os.system('rm '+rundir+case+'.'+options.model_name+'*_constraint.nc')
  myoutput = open(rundir+'myoutput_sse.txt','w')
  for filename in os.listdir(constraints):

   if (not os.path.isdir(filename)):
    myinput = open(constraints+'/'+filename,'r')
    myvarname = filename.split('.')[0]  #model variable is filename
    #code to deal with special variables and/or aggregation
    #-------------
    lnum = 0   #line number
    year = 0
    for s in myinput:
        if (lnum == 0):
            header = s.split()
        elif (len(header) == len(s.split())):
            hnum = 0
            PFT=-1      #default:  don't use PFT-specific info 
                        #  if specified, use h1 file (PFT-specific)
            doy=-1      #default:  annual average
            month=-1    #default:  don't use monthly data
            depth=-1
            unc = -999
            for h in header:
                if (h.lower() == 'year'):
                    year_last = year
                    year = int(s.split()[hnum])
                if (h.lower() == 'doy'):
                    doy = int(s.split()[hnum])
                if (h.lower() == 'month'):
                    month = int(s.split()[hnum])
                if (h.lower() == 'pft'):
                    PFT = int(s.split()[hnum])
                if (h.lower() == 'value'):
                    value = float(s.split()[hnum])
                if (h.lower() == 'depth'):
                    depth = float(s.split()[hnum])
                if ('unc' in h.lower()):
                    unc   = float(s.split()[hnum])
                hnum = hnum+1
            #get the relevant variable/dataset
            #Assumes annual file with daily output
            if (PFT == -1):
                myfile  = rundir+case+'.'+options.model_name+'.h0.'+str(year)+'-01-01-00000_constraint.nc'
                myfileo = rundir+case+'.'+options.model_name+'.h0.'+str(year)+'-01-01-00000.nc'
            else:
                myfile  = rundir+case+'.'+options.model_name+'.h1.'+str(year)+'-01-01-00000_constraint.nc'
                myfileo = rundir+case+'.'+options.model_name+'.h1.'+str(year)+'-01-01-00000.nc'
            #post processing of model output with nco to match constraining variables
            if (not os.path.isfile(myfile)):
                os.system('cp '+myfileo+' '+myfile)
                if ('h1' in myfile and ('STEMC' in myvarname or 'AGBIOMASS' in myvarname)):
                    os.system('ncap2 -3 -s "STEMC=DEADSTEMC+LIVESTEMC" '+myfile+' '+myfile+'.tmp')
                    os.system('mv '+myfile+'.tmp '+myfile)
                    os.system('ncap2 -3 -s "AGBIOMASS=DEADSTEMC+LIVESTEMC+LEAFC" '+myfile+' '+myfile+'.tmp')
                    os.system('mv '+myfile+'.tmp '+myfile)
                if ('h0' in myfile and 'WTHT' in myvarname):
                    #Water table height relative to hollow bottoms (7.5cm below hollow gridcell mean)
                    os.system('ncap2 -3 -s "WTHT=(ZWT*-1+0.225)*1000 " '+myfile+' '+myfile+'.tmp')
                    os.system('mv '+myfile+'.tmp '+myfile)
            myvals = nffun.getvar(myfile, myvarname)
            if (doy > 0 and value > -900):
                #Daily constraint
                if (myvarname == 'WTHT'):
                    unc = 50.0   #no uncertainty given for water table height.
                if (PFT > 0):
                    #PFT-specific constraints (daily)
                    if (myvarname == 'AGBIOMASS' and PFT == 3):
                        #Both tree types - Larch and spruce, hummock+hollow
                        model_val = (myvals[doy,PFT-1]*0.25+myvals[doy,PFT]*0.25)*0.75 \
                                   +(myvals[doy,PFT+16]*0.25+myvals[doy,PFT+17]*0.25)*0.25
                    else:
                        #use hummock+hollow
                        model_val = myvals[doy,PFT-1]*0.25*0.75 + myvals[doy,PFT+16]*0.25*0.25
                    if (unc < 0):
                        unc = value*0.25 #default uncertainty set to 25%
                    sse = sse + ((model_val-value) /unc)**2
                elif (depth > 0):
                    #depth-specific constraint in cm (relative to hollow)
                    layers = [0,1.8,4.5,9.1,16.6,28.9,49.3,82.9,138.3,229.6,343.3]
                    for l in range(0,10):
                        if (depth >= layers[l] and depth < layers[l+1]):
                            thislayer = l
                            model_val = myvals[doy,thislayer,1]   #Hollow 
                            sse = sse + ((model_val-value) / unc )**2
                else:
                    #Column-level constraint (daily)
                    #Water table, column-level (no PFT info), use hummock only
                    model_val = myvals[doy,0]
                    sse = sse + ((model_val-value) / unc )**2
            elif (value > -900):
                #Monthly or annual constraint
                daysm=[0,31,59,90,120,151,181,212,243,273,304,334,365]
                if (month > 0):
                  lbound = daysm[month-1]
                  ubound = daysm[month]
                else: 
                  lbound = 0
                  ubound = 365
                #model_val = sum(myvals[0:365,PFT-1]*0.25*0.75)*24*3600 + \
                #            sum(myvals[0:365,PFT+16]*0.25*0.25)*24*3600
                if (PFT <= 0):
                  model_val = sum(myvals[lbound:ubound,0]) / (ubound - lbound)
                else:
                  model_val = sum(myvals[lbound:ubound,PFT-1]) / (ubound - lbound)
                sse = sse + ((model_val-value) / unc )**2
                myoutput.write(str(myvarname)+' '+str(year)+' '+str(month)+' '+str(PFT)+' '+ \
                  str(model_val)+' '+str(value)+' '+str(unc)+' '+str(sse)+'\n')
        lnum = lnum+1
  myoutput.close()
  return sse

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
    time.sleep(rank)
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
            if (len(s.split()) == 11):
              myobs.append(float(s.split()[9]))
              myobs_err.append(float(s.split()[10]))
            else: 
              myobs.append(-9999)
              myobs_err.append(-9999)                
            days_total = (int(s.split()[2]) - int(s.split()[1])+1)*(int(s.split()[4]) - int(s.split()[3])+1)        
            data_cols = data_cols + days_total / int(s.split()[5])
    if (rank == 0):
        data = np.zeros([data_cols,options.n], np.float)-999
    data_row = np.zeros([data_cols], np.float)-999
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
parm_row = np.zeros([nparms], np.float)-999
if (rank == 0):
  parms = np.zeros([nparms, options.n], np.float)-999
  sse_ensemble = np.zeros([options.n], np.float)-999      

niter = 1
if (options.do_QPSO):
  niter = 100

if (rank == 0):
    if (options.do_QPSO):
      beta_l = 0.4
      beta_u = 0.7
      nevals = 0
      x = np.zeros([options.n,nparms],np.float)    #parameters for each pop
      fx = np.zeros(options.n,np.float)                #costfunc for each pop
      mbest = np.zeros(nparms)

    #-------- Create ensemble file if one wasn't provided ------------------------
    if (options.mc_ensemble > 0 or options.do_QPSO):
      #Create a parameter samples file
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
        pmin.append(float(s.split()[2]))
        pmax.append(float(s.split()[3]))
        nparms = nparms+1
      pfile.close()
      samples=np.zeros((nparms,options.n), dtype=np.float)
      for i in range(0,options.n):
          for j in range(0,nparms):
              samples[j,i] = pmin[j]+(pmax[j]-pmin[j])*np.random.rand(1)
              if (options.do_QPSO):
                x[i,j]=samples[j,i]
      np.savetxt(options.ens_file, np.transpose(samples))

    #--------------------------Perform the model simulations---------------------
    for thisiter in range(0,niter):
      n_done = 0
      #generate samples for QPSO
      if (thisiter > 0): 
        beta = beta_u - (beta_u-beta_l)*i*1.0/niter
        xlast = np.copy(x)
        for p in range(0, nparms):
            mbest[p] = np.sum(xbest[:,p])/options.n
        for n in range(0,options.n):
            isvalid = False
            while (not isvalid):
                u = np.random.uniform(0,1,1)
                v = np.random.uniform(0,1,1)
                w = np.random.uniform(0,1,1)
                pupdate = u * xbest[n,:] + (1.0-u)*xbestall[:]
                betapro = beta * np.absolute(mbest[:] - xlast[n,:])
                x[n,:] = pupdate + (-1.0 ** np.ceil(0.5+v))*betapro*(-np.log(w))
                isvalid = True
                for p in range(0,nparms):
                    if (x[n,p] < pmin[p] or x[n,p] > pmax[p]):
                        isvalid=False
        np.savetxt(options.ens_file, x)

  
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
          if (options.constraints != ''):
            sse_ensemble[thisjob-1] = comm.recv(source=process, tag=7)
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
          if (options.constraints != ''):
            sse_ensemble[thisjob-1] = comm.recv(source=process, tag=7)
          if (do_postproc):
              data_row = comm.recv(source=process, tag=5)
              data[:,thisjob-1] = data_row
              parm_row = comm.recv(source=process, tag=6)
              parms[:,thisjob-1] = parm_row
          n_done = n_done+1
          comm.send(-1, dest=process, tag=1)
          comm.send(-1, dest=process, tag=2)

      if (options.do_QPSO):
        fx = sse_ensemble
        if (thisiter == 0):
          xbest = np.copy(x)            #Best parms for each pop so far
          fxbest = np.copy(fx)          #Best costfunc for each pop so far
          xbestall  = (np.copy(x[0,:])).squeeze()    #Overall best parms so far
          fxbestall = np.copy(fx[0])    #OVerall best costfunc so far

        for n in range(0,options.n):
          if (fx[n] < fxbest[n]):
            xbest[n,:] = np.copy(x[n,:])
            fxbest[n] = np.copy(fx[n])
          if (fxbest[n] < fxbestall):
            #get overall best parameters and function values
            xbestall[:] = np.copy(x[n,:])
            fxbestall = np.copy(fx[n]) 
        print('ITER', thisiter, fxbest, fxbestall)

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
        for p in pnames:
          myoutput.write(p+'\n')
          eden_header=eden_header+p+','
        myoutput.close()
        myoutput = open(UQ_output+'/data/outnames.txt', 'w')
        for v in myvars:
          myoutput.write(v+'\n')
          eden_header=eden_header+v+','
        myoutput.close()
        myoutput = open(UQ_output+'/data/param_range.txt', 'w')
        for p in range(0,len(pmin)):
          myoutput.write(pmin[p]+' '+pmax[p]+'\n')
        myoutput.close()
        print(np.hstack((parm_out,data_out)))
        np.savetxt(UQ_output+'/data/foreden.csv', np.hstack((parm_out,data_out)), delimiter=',', header=eden_header[:-1])
        if (options.run_uq):
          #Run the sensitivity analysis using UQTk
          os.system('cp UQTk_scripts/*.x '+UQ_output+'/')
          os.chdir(UQ_output)
          os.system('./run_sensitivity.x')
          os.system('mkdir -p UQTk_output')
          os.system('mkdir -p UQTk_plots')
          os.system('mkdir -p UQTk_scripts')
          os.system('mv *.eps UQTk_plots')
          os.system('mv *.x UQTk_scripts')
          os.system('mv *.tar *.pk UQTk_output')
          os.chdir('../..')
          #Create the surrogate model
          os.system('python surrogate_NN.py --case '+options.casename)
          if (max(myobs_err) > 0):
            #Run the MCMC calibration on surrogate model if data provided
            os.system('python MCMC.py --case '+options.casename)
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
                if (options.constraints != '' and '20TR' in options.casename):
                  mycases.append(options.casename.replace('20TRCNPRDCTCBC','1850CNRDCTCBC_ad_spinup'))
                  mycases.append(options.casename.replace('20TRCNPRDCTCBC','1850CNPRDCTCBC'))
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
            if (do_postproc):
                ierr = postproc(myvars, myyear_start, myyear_end, myday_start, \
                         myday_end, myavg_pd, myfactor, myoffset, mypft, myjob, \
                         options.runroot, options.casename, pnames, ppfts, data_row, parm_row)
                comm.send(rank, dest=0, tag=3)
                comm.send(myjob, dest=0, tag=4)
                comm.send(data_row, dest=0, tag=5)
                comm.send(parm_row, dest=0, tag=6)
            else:
                comm.send(rank,  dest=0, tag=3)
                comm.send(myjob, dest=0, tag=4)
                if (options.constraints != ''):
                  sse = calc_costfucntion(options.constraints, myjob, options.runroot, options.casename)
                  comm.send(sse, dest=0, tag=7)
  MPI.Finalize()
