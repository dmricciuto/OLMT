from netCDF4 import Dataset
import numpy as np
import os
#coefficients for calculating saturation vapor pressure
a = [6.107799961, 4.436518521e-01, 1.428945805e-02, 2.650648471e-04, \
         3.031240396e-06, 2.034080948e-08, 6.136820929e-11]
b = [6.109177956, 5.034698970e-01, 1.886013408e-02, 4.176223716e-04, \
         5.824720280e-06, 4.838803174e-08, 1.838826904e-10]


#Function for cacluating saturation specific humidity
def calc_q(e_in, pres):
    myq = 0.622 * e_in / (pres - 0.378*e_in)
    return myq

def esat(t):
    if (t[0] > 0):
        myesat = (a[0]+t*(a[1]+t*(a[2]+t*(a[3]+t*(a[4]+t*(a[5]+t*a[6]))))))
    else:
        myesat = (b[0]+t*(b[1]+t*(b[2]+t*(b[3]+t*(b[4]+t*(b[5]+t*b[6]))))))
    return myesat


def bypass_format(filename, met_data, lat, lon, startyear, endyear, edge=0.1, time_offset=0, calc_qbot = False, calc_lw = False, zbot=10):
  metvars = met_data.keys()

  units={}
  units['TBOT'] = 'K'
  units['TSOIL'] = 'K'
  units['RH'] = '%'
  units['WIND'] = 'm/s'
  units['FSDS'] = 'W/m2'
  units['PAR'] = 'umol/m2/s'
  units['FLDS'] = 'W/m2'
  units['PSRF'] = 'Pa'
  units['PRECTmms'] = 'kg/m2/s'
  units['QBOT'] = 'kg/kg'
  units['ZBOT'] = 'm'
  long_names = {}
  long_names['TBOT'] = 'temperature at the lowest atm level (TBOT)'
  long_names['RH'] = 'relative humidity at the lowest atm level (RH)'
  long_names['WIND'] = 'wind at the lowest atm level (WIND)'
  long_names['FSDS'] = 'incident solar (FSDS)'
  long_names['FLDS'] = 'incident longwave (FLDS)'
  long_names['PSRF'] = 'pressure at the lowest atm level (PSRF)'
  long_names['PRECTmms'] = 'precipitation (PRECTmms)'
  long_names['QBOT'] = 'specific humidity at the lowest atm level (QBOT)'
  long_names['ZBOT'] = 'observational height (ZBOT)'

  nt = len(met_data['TBOT'])
  npd = np.round(nt/(endyear-startyear+1))/365

  all_hourly = Dataset(filename,'w')
  all_hourly.createDimension('DTIME', nt)
  all_hourly.createDimension('gridcell',1)
  all_hourly.createDimension('scalar',1)
  for v in metvars:
    all_hourly.createVariable(v, 'f', ('gridcell','DTIME',))
    nshift = int(abs(time_offset*int(npd/24)))
    if (time_offset < 0):
      all_hourly[v][0,nshift:] = met_data[v][:-1*nshift]
      all_hourly[v][0,0:nshift] = met_data[v][0]
    elif (time_offset > 0):
      all_hourly[v][0,:-1*nshift] = met_data[v][nshift:]
      all_hourly[v][0,-1*nshift:] = met_data[v][nt-1]
    else:
      all_hourly[v][0,:] = met_data[v][:]
    all_hourly[v].units = units[v]
    all_hourly[v].long_name = long_names[v]
    all_hourly[v].mode = 'time-dependent'

  if (calc_qbot):
    all_hourly.createVariable('QBOT','f',('gridcell','DTIME',))
    all_hourly.createVariable('VPD','f',('gridcell','DTIME',))
    mye = esat(all_hourly['TBOT'][0,:]-273.15) * all_hourly['RH'][0,:]/100.
    all_hourly['VPD'][0,:] = esat(all_hourly['TBOT'][0,:]-273.15) * (1.0 - all_hourly['RH'][0,:]/100.)*100.
    all_hourly['VPD'].units = units['VPD']
    all_hourly['VPD'].long_name = long_names['VPD']
    all_hourly['VPD'].mode = 'time_dependent'

    all_hourly['QBOT'][0,:] = calc_q(mye, all_hourly['PSRF'][0,:]/100.)      
    all_hourly['QBOT'].units = units['QBOT']
    all_hourly['QBOT'].long_name = long_names['QBOT']
    all_hourly['QBOT'].mode = 'time_dependent'

  if (calc_lw):
    all_hourly.createVariable('FLDS','f',('gridcell','DTIME',))
    stebol = 5.67e-8
    mye = esat(all_hourly['TBOT'][0,:]-273.15) * all_hourly['RH'][0,:]/100.
    ea = 0.70 + 5.95e-5*mye*np.exp(1500.0/all_hourly['TBOT'][0,:])
    all_hourly['FLDS'][0,:] = ea * stebol * (all_hourly['TBOT'][0,:]) ** 4

  if (not 'ZBOT' in metvars):
    all_hourly.createVariable('ZBOT','f',('gridcell','DTIME',))
    all_hourly['ZBOT'][:,:] = zbot
    all_hourly['ZBOT'].units = units['ZBOT']
    all_hourly['ZBOT'].long_name = long_names['ZBOT']
    all_hourly['ZBOT'].mode = 'time_dependent'

  all_hourly.close()

  os.system('ncpdq '+filename+' '+filename+'_pk')
  os.system('mv    '+filename+'_pk '+filename)
  output_data = Dataset(filename,'a')
  output_data.createDimension('scalar', 1)
  output_data.createVariable('DTIME', 'f8', 'DTIME')
  output_data.variables['DTIME'].long_name='observation time'
  output_data.variables['DTIME'].units='days since '+str(startyear)+'-01-01 00:00:00'
  output_data.variables['DTIME'].calendar='noleap'
  n_years = endyear-startyear+1
  output_data.variables['DTIME'][:] = np.cumsum(np.ones([int(n_years*365*npd)], np.float)/npd)-0.5/npd
  output_data.createVariable('LONGXY', 'f8', 'gridcell')
  output_data.variables['LONGXY'].long_name = "longitude"
  output_data.variables['LONGXY'].units = 'degrees E'
  output_data.variables['LONGXY'][:] = lon 
  output_data.createVariable('LATIXY', 'f8', 'gridcell')
  output_data.variables['LATIXY'].long_name = "latitude"
  output_data.variables['LATIXY'].units = 'degrees N'
  output_data.variables['LATIXY'][:] = lat 
  output_data.createVariable('start_year', 'i4', 'scalar')
  output_data.variables['start_year'][:] = startyear
  output_data.createVariable('end_year', 'i4', 'scalar')
  output_data.variables['end_year'][:] = endyear
  output_data.close()


  #for y in range(startyear,endyear):
  #  for m in range(0,12):
  #    mst = str(101+m)[1:]
  #    monthly = Dataset('1x1pt_'+site+'/'+str(y)+'-'+mst+'.nc','w')

