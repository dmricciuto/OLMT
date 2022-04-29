import numpy as np
from netCDF4 import Dataset
import os,sys
import gapfill
import write_elm_met

#------- user input -------------
site = 'MAR-NE'
start_year = 2016
end_year = 2016
time_offset = -5    #Standard time offset from UTC (e.g. EST is -5)
npd = 48            #number of time steps per day (48 = half hourly)
mylon = 270.0       #site longitude (0 to 360)
mylat = 45.0        #site latitude
measurement_height = 30    #tower height (m)
fname_template = 'SITE-EddyFluxTallTower-YYYY.csv'
calc_flds = True    #use T and RH to comput FLDS (use if data missing or sparse)
leapdays = True     #input data has leap days (to be removed for ELM)
outdir = './1x1pt_'+site+'/'     #Desired directory for ELM met inputs

metdata={}
#outvars   - met variables used as ELM inputs
#invars    - corresponding variables to be read from input file
#conv_add  - offset for converting units (e.g. C to K)
#conv_mult - multiplier for converting units (e.g. hPa to Pa, PAR to FSDS)
#valid_min - minimum acceptable value for this variable (set as NaN outside range)
#valid_max - maximum acceptable value for this variable (set as NaN outside range)

#Note - FLDS not included here (calculated)
outvars  = ['TBOT','RH','WIND','PSRF','FSDS',    'PRECTmms']
invars   = ['TA',  'RH','WS',  'PA', 'PPFD_OUT', 'H2O']   #matching header of input file
conv_add = [273.15,   0,     0,    0,         0,      0]
conv_mult= [     1,   1,     1, 1000,1./(0.48*4.6),   1]
valid_min= [180.00,   0,     0,  8e4,         0,      0]
valid_max= [350.00,100.,    80,1.5e5,      2500,      15]

#ELM Variable names and units
#TBOT:     Air temperature at measurement (tower) height (K)
#RH:       Relative humidity at measurment height (%)
#WIND:     Wind speeed at measurement height (m/s)
#PSRF:     air pressure at surface  (Pa)
#FSDS:     Incoming Shortwave radiation  (W/m2)
#FLDS:     Incoming Longwave radiation   (W/m2)
#PRECTmms: Precipitation       (kg/m2/s)


os.system('mkdir -p '+outdir)
for v in outvars:
  metdata[v] = []

#Load the data
for y in range(start_year,end_year+1):
  if (y % 4) == 0:
     isleapyear = True
  filename = fname_template.replace('SITE',site).replace('YYYY',str(y))
  lnum= 0
  myfile = open(filename,'r')
  for s in myfile:
    if (lnum == 0):
      header=s.split(',')
    else:   
      #skip leap days
      if (not leapdays or (not isleapyear or (isleapyear and (lnum-1)/npd != 59))):
       data=s.split(',')
       for v in range(0,len(invars)):
        for h in range(0,len(header)):
          if header[h] == invars[v]:
            try:
              val = float(data[h])*conv_mult[v]+conv_add[v]
              if (val >= valid_min[v] and val <= valid_max[v]):
                metdata[outvars[v]].append(val)
              else:
                metdata[outvars[v]].append(np.NaN)
            except:
              metdata[outvars[v]].append(np.NaN)
    lnum=lnum+1

#Fill missing values with diurnal mean
for key in metdata:
  print(key)
  gapfill.diurnal_mean(metdata[key],npd=npd)


out_fname = outdir+'/all_hourly.nc'
write_elm_met.bypass_format(out_fname, metdata, mylat, mylon, start_year, end_year, edge=0.1, \
                time_offset=time_offset, calc_qbot = False, calc_lw = calc_flds, zbot=measurement_height)

