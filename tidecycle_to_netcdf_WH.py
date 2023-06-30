from numpy import pi,arange,sin,cos,zeros
from matplotlib import pyplot

# Two coefficient sum
def tide(t,diel_amp=250.0,neapspring_amp=1.0/0.91518,baseline=800.0,diel_period=3.3333e4,neapspring_period=1e8,diel_phase=513.4328,neapspring_phase=0.0):
    return diel_amp * sin(2.0*pi*(1/diel_period*t + diel_phase)) + neapspring_amp*sin(2.0*pi*(1/neapspring_period*t + neapspring_phase)) + baseline

# N coefficent sum following NOAA system (https://tidesandcurrents.noaa.gov/about_harmonic_constituents.html)
# Station data needs to be converted (e.g. https://tidesandcurrents.noaa.gov/harcon.html?id=8441241&unit=0)
# amp: feet to mm
# speed: degrees/hour to radians/second
# phase: degrees to radians
def tide2(t,amp,phase,speed,datum=0.0):
    n_constituents=len(amp)
    out=zeros(len(t))
    for n in range(n_constituents):
        out=out+amp[n]*cos(speed[n]/3600*pi/180*t - phase[n]*pi/180)

    return out+datum

# Plot one month of tidal cycle for different parameters
t=arange(0,3600*24*90,3600) 
f,axs=pyplot.subplots(2,num='Tidal cycles',clear=True)
axs[0].plot(t/(3600*24),tide(t))
axs[0].set(title="Tidal cycle: Teri's parameters",xlabel='Time (days)',ylabel='Tide height (mm)')

import pandas
# tide_coeffs=pandas.read_excel('tides_8419870_PlumIsland.xlsx',skiprows=1,index_col='Constituent #')
tide_coeffs=pandas.read_csv('/home/whf/E3SM/OLMT_coastal_v2/harmonic_tides_8575512.csv')
tide_coeffs_top2=tide_coeffs.sort_values('Amplitude',ascending=False).iloc[:2]
tide_coeffs_top8=tide_coeffs.sort_values('Amplitude',ascending=False).iloc[:8]
# Plot using NOAA tidal coefficients
# Using mean tide level from https://tidesandcurrents.noaa.gov/datums.html?id=8419870 as datum (converted to mm)
axs[1].plot(t/(3600*24),tide2(t,amp=tide_coeffs['Amplitude'].values,phase=tide_coeffs['Phase'].values,speed=tide_coeffs['Speed'].values,datum=4.38*304.8e-3),label='37 constituents')
axs[1].plot(t/(3600*24),tide2(t,amp=tide_coeffs_top8['Amplitude'].values,phase=tide_coeffs_top8['Phase'].values,speed=tide_coeffs_top8['Speed'].values,datum=4.38*304.8e-3),label='Top 8')
axs[1].plot(t/(3600*24),tide2(t,amp=tide_coeffs_top2['Amplitude'].values,phase=tide_coeffs_top2['Phase'].values,speed=tide_coeffs_top2['Speed'].values,datum=4.38*304.8e-3),label='Top 2')

axs[1].set(title="Tidal cycle: NOAA full calculation",xlabel='Time (days)',ylabel='Tide height (mm)')
axs[1].legend()

# Write out a 100 year file for ELM
import xarray
#time=xarray.Variable(dims='time',data=arange(876000),attrs={'units':'hours'})
#tide_height=xarray.Variable(dims=('time','gridcell'),data=tide2(arange(876000,dtype=float)*3600,amp=tide_coeffs['Amplitude'].values,phase=tide_coeffs['Phase'].values,speed=tide_coeffs['Speed'].values,datum=4.38*304.8e-3)[:,None],attrs={'units':'m'})
#tide_salinity=xarray.Variable(dims=('time','gridcell'),data=zeros(876000,dtype=float)[:,None]+20.0,attrs={'units':'ppt'})
#d=xarray.Dataset(data_vars={'tide_height':tide_height,'tide_salinity':tide_salinity},coords={'time':time,'gridcell':[0]})

#d.to_netcdf('./tides_100yr.nc')

# Write a one year file with PIE salinity data
#sal_data = pandas.read_csv('/home/whf/E3SM/OLMT_coastal_v2/Annapolis_schism_salinity20172018plus2_MSL_WT6_1.csv')
#sal_data = pandas.read_csv('/home/whf/E3SM/OLMT_coastal_v2/Annapolis_schism_salinity20172018_CB3_3W_MSL.csv')
#sal_data = pandas.read_csv('/home/whf/E3SM/inputs/Annapolis_schismPlus2_Peter_salinity_WT6_1_39yrs_NAVD.csv')
#sal_data = pandas.read_csv('/home/whf/E3SM/inputs/Annapolis_monthlySalinity_39yrs_NAVD.csv')
#sal_data = pandas.read_csv('/home/whf/E3SM/inputs/Annapolis_elev_0salinity_39yrs_NAVD.csv')
sal_data = pandas.read_csv('/home/whf/E3SM/inputs/LakeErie_Gageheight_0salt.csv')
sal_data['Tide_salinity']=sal_data['Tide_salinity'].fillna(25)
salinity=sal_data['Tide_salinity'].to_numpy()
time=sal_data['time_e'].to_numpy()
print(len(time))
#sal_data = pandas.read_csv('/home/whf/E3SM/inputs/Annapolis_elev_0salinity_35yrs_MSL.csv')
tide_elev=sal_data['Tide_height'].to_numpy()
#below two lines are using elev from different csv file
#elev_data= pandas.read_csv('/home/whf/E3SM/OLMT_coastal_v2/Annapolis_sal_elev_detrend_datenum_MSL.csv')
#tide_elev=elev_data['Tide_height'].to_numpy()
#wl_data=pandas.read_csv('~/PHM/plm.csv')
#wl=wl_data['wl18'].to_numpy()
#t_data = pandas.read_csv('~/PHM/soilt18.csv')
#t_data['soilt']=t_data['soilt'].fillna(274)
#soilt=t_data['soilt'].to_numpy()
time=xarray.Variable(dims='time',data=time[:],attrs={'units':'days'})
#tide_height=xarray.Variable(dims=('time','gridcell'),data=tide2(arange(8760,dtype=float)*3600,amp=tide_coeffs['Amplitude'].values,phase=tide_coeffs['Phase'].values,speed=tide_coeffs['Speed'].values,datum=4.38*304.8e-3)[:,None],attrs={'units':'m'})
#tide_height=xarray.Variable(dims=('time','gridcell'),data=tide2(arange(8760,dtype=float)*3600,amp=tide_coeffs['Amplitude'].values,phase=tide_coeffs['Phase'].values,speed=tide_coeffs['Speed'].values,datum=0.0)[:,None],attrs={'units':'m'})
tide_salinity=xarray.Variable(dims=('time','gridcell'),data=salinity[:,None],attrs={'units':'ppt'})
tide_height=xarray.Variable(dims=('time','gridcell'),data=tide_elev[0:len(time),None],attrs={'units':'m'})
#tide_temp=xarray.Variable(dims=('time','gridcell'),data=soilt[:,None],attrs={'units':'K'})

d=xarray.Dataset(data_vars={'tide_height':tide_height,'tide_salinity':tide_salinity},coords={'time':time,'gridcell':[0]})

#d.to_netcdf('./Annapolis_WT6_1_schism_salinity20172018plus2_35yrs_MSL_tides.nc')
d.to_netcdf('/home/whf/E3SM/inputs/LakeErie_Gageheight_0salt.nc')
