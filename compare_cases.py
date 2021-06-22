import numpy as np
from netCDF4 import Dataset
from optparse import OptionParser
import glob

parser = OptionParser()
parser.add_option("--runroot", dest="runroot", default='', \
                  help = 'Base CESM directory (default = ..)')
parser.add_option("--cases", dest="mycase", default='', \
                  help = "name of case id prefixs to plot (comma delmited)")
parser.add_option("--h0vars", dest="h0vars", default='', \
                  help = "List of variables to compare in h0 files (default = all)")
(options,args) = parser.parse_args()

#Simple funcion to compare all numerical values in two netcdf values and identify diffs
def comparencfiles(f1,f2,vars_compare=[]):
  excluded_vars = ['date_written','time_written','pftname','soilordername', \
         'qflx_snofrz_lyr','irrig_rate','TWS_MONTH_BEGIN','ENDWB_COL','vcmaxcintsun', \
         'vcmaxcintsha','fates_ddbhdt','mlaidiff','btran2','locfnh','locfnhr', \
         'fates_pftname','fates_prt_organ_name']
  data1 = Dataset(f1,'r')
  hasdiff=False
  data2 = Dataset(f2,'r')
  for key in data1.variables:
    if (not key in excluded_vars):
      if (vars_compare == [] or key in vars_compare):
        if (not key in data2.variables):
         print('    Error: '+key+' not in '+f2)
         hasdiff=True
        else:
          try:
            if (not np.ma.allequal(data1[key][:].squeeze(),data2[key][:].squeeze())):
              print('    Differences in '+key+': ')
              print('      Case 1 Mean: '+str(np.ma.mean(data1[key][:].squeeze())))
              print('      Case 2 Mean: '+str(np.ma.mean(data2[key][:].squeeze())))
              hasdiff=True
          except:
            print('      Can not compare '+key)
  return hasdiff

if (options.h0vars != ''):
  h0vars = options.h0vars.split(',')
else:
  h0vars=[]

cases = options.mycase.split(',')
runroots = options.runroot.split(',')

#Input file types to compare
ftypes=['paramfile','fates_paramfile','fsoilordercon','fsurdat','fatmlndfrc','finidat']
run_files={}
for f in ftypes:
  run_files[f]=[]

cnum=0
h0list={}
for c in cases:
  if len(runroots) > 1:
    rundir = runroots[cnum]+'/'+c+'/run'
  else:
    rundir = runroots[0]+'/'+c+'/run'
  h0list[c]=glob.glob(rundir+'/*clm2.h0.*.nc')
  h0list[c].sort()
  lnd_in = open(rundir+'/lnd_in','r')
  for s in lnd_in:
    for f in ftypes:
      if (' '+f+' =' in s):
        run_files[f].append(s.split('=')[1].strip(" '\n"))
  lnd_in.close()
  cnum=cnum+1

#compare the input files:
for f in ftypes:
  if (len(run_files[f]) > 0):
    print('TEST for '+f)
    for c in range(1,len(cases)):
      if (len(run_files[f]) < c+1):
            print('  FAIL: '+f+' does not exist for '+cases[c])
      elif (run_files[f][0] != '' and run_files[f][c] != ''):
        hasdiff = comparencfiles(run_files[f][0],run_files[f][c])
        if (hasdiff):
            print('  FAIL: '+run_files[f][0]+' and \n'+'        '+run_files[f][c]+' differ.')
        else:
            print('  PASS: '+run_files[f][0]+' and \n'+'        '+run_files[f][c]+' are equal.')
      elif (run_files[f][0] == '' and run_files[f][c] == ''):
          print('  PASS: No files of this type specified')
      else:
          print('  FAIL: File specified for one case and not the other')
          print('    '+cases[0]+': '+run_files[f][0])
          print('    '+cases[c]+': '+run_files[f][c])


#Compare the h0 output files
print('TEST for h0 model output')
for c in range(1,len(cases)):
  print('Case 1: '+cases[0])
  print('Case 2: '+cases[c])
  if (len(h0list[cases[0]]) != len(h0list[cases[c]])):
    print('  FAIL: Number of h0 files differ between cases')
  else:
    ngood=0
    for h in range(0, len(h0list[cases[0]])):
      hasdiff = comparencfiles(h0list[cases[0]][h],h0list[cases[c]][h],vars_compare=h0vars)
      if (hasdiff):
        print('  FAIL: '+h0list[cases[0]][h]+' and \n'+'        '+h0list[cases[c]][h]+' differ.')
        print('  Exiting test')
        break
      else:
        ngood=ngood+1
    if (not hasdiff):
      print('  PASS: All '+str(ngood)+' h0 files are equal.')
