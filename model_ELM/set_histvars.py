#!/usr/bin/env python
import re, os, sys, csv, time, math
import numpy

def set_histvars(self,spinup=-1,hist_mfilt=-9999,hist_nhtfrq=-9999):
   if (spinup>0):
      var_list_spinup = ['PPOOL', 'EFLX_LH_TOT', 'RETRANSN', 'PCO2', 'PBOT', 'NDEP_TO_SMINN', 'OCDEP', \
                    'BCDEP', 'COL_FIRE_CLOSS', 'HDM', 'LNFM', 'NEE', 'GPP', 'FPSN', 'AR', 'HR', \
                    'MR', 'GR', 'ER', 'NPP', 'TLAI', 'SOIL3C', 'TOTSOMC', 'TOTSOMC_1m', 'LEAFC', \
                    'DEADSTEMC', 'DEADCROOTC', 'FROOTC', 'LIVESTEMC', 'LIVECROOTC', 'TOTVEGC', 'N_ALLOMETRY','P_ALLOMETRY',\
                    'TOTCOLC', 'TOTLITC', 'BTRAN', 'SCALARAVG_vr', 'CWDC', 'QVEGE', 'QVEGT', 'QSOIL', 'QDRAI', \
                    'QRUNOFF', 'FPI', 'FPI_vr', 'FPG', 'FPI_P','FPI_P_vr', 'FPG_P', 'CPOOL','NPOOL', 'PPOOL', 'SMINN', 'HR_vr', \
                    'LITFALL', 'XR', 'PFT_FIRE_CLOSS']
      if ('ICBELMBC' in self.compset):
        var_list_spinup = ['FPSN','TLAI','QVEGT','QVEGE','QSOIL','EFLX_LH_TOT','FSH','RH2M','TSA','FSDS','FLDS','PBOT', \
                         'WIND','BTRAN','DAYL','T10','QBOT']


     #if (self.C14):
      #    var_list_spinup.append('C14_TOTSOMC')
      #    var_list_spinup.append('C14_TOTSOMC_1m')
      #    var_list_spinup.append('C14_TOTVEGC')
      if (not 'ECA' in self.compset and not 'ELMBC' in self.compset):
        var_list_spinup.extend(['SOIL4C'])
      vst = ''
      for v in var_list_spinup:
        vst=vst+"'"+v+"',"
      if (not 'ELMBC' in self.compset):
        if ('FATES' in self.compset):
          #All variables, annual output for FATES
          self.customize_namelist(variable='hist_mfilt',value='1')
          self.customize_namelist(variable='hist_nhtfrq',value='-8760')
        else:
          self.customize_namelist(variable='hist_empty_htapes',value='.true.')
          self.customize_namelist(variable='hist_fincl1',value=vst[:-1])
          self.customize_namelist(variable='hist_fincl2',value=vst[:-1])
          self.customize_namelist(variable='hist_dov2xy',value='.true.,.false.')
          self.customize_namelist(variable='hist_mfilt',value='1,1')
          self.customize_namelist(variable='hist_nhtfrq',value=str(self.nyears_spinup*-8760)+','+str(self.nyears_spinup*-8760))
      else:
        if (not self.postproc_vars):
          self.customize_namelist(variable='hist_mfilt',value='365')
          self.customize_namelist(variable='hist_nhtfrq',value='-24')
        else:
          vst_pp=''
          vst_pp_pft=''
          for v in self.postproc_vars:
              if ('_pft' in v):
                  #PFT specific outputs (put in h2 file)
                  vst_pp_pft=vst_pp_pft+"'"+v.split('_pft')[0]+"',"
              else:
                  vst_pp=vst_pp+"'"+v+"',"
          #Write daily for requested postprocessed variables
          if (vst_pp_pft != ''):
              self.customize_namelist(variable='hist_mfilt',value='1,365,365')
              self.customize_namelist(variable='hist_nhtfrq',value='-8760,-24,-24')
              self.customize_namelist(variable='hist_dov2xy',value='.true.,.true.,.false.')
              self.customize_namelist(variable='hist_fincl3',value=vst_pp_pft[:-1])
          else:
              self.customize_namelist(variable='hist_mfilt',value='1,365')
              self.customize_namelist(variable='hist_nhtfrq',value='-8760,-24')
          self.customize_namelist(variable='hist_fincl2',value=vst_pp[:-1])
   else:
      #Transient simulation
      if (self.postproc_vars == []):
        #Default to daily output for all variables if not postproc vars
        #if ('US-SPR' in self.site):
        #    #For default SPRUCE run, set history variables
        #else:
        self.customize_namelist(variable='hist_mfilt',value='365')
        self.customize_namelist(variable='hist_nhtfrq',value='-24')
      else:
        #Write annual for all vars, requested postproc vars daily
        vst_pp=''
        vst_pp_pft=''
        for v in self.postproc_vars:
            if ('_pft' in v):
                #PFT specific outputs (put in h2 file)
                vst_pp_pft=vst_pp_pft+"'"+v.split('_pft')[0]+"',"
            else:
                vst_pp=vst_pp+"'"+v+"',"
        if (vst_pp_pft != ''):
            self.customize_namelist(variable='hist_mfilt',value='1,365,365')
            self.customize_namelist(variable='hist_nhtfrq',value='-8760,-24,-24')
            self.customize_namelist(variable='hist_dov2xy',value='.true.,.true.,.false.')
            self.customize_namelist(variable='hist_fincl3',value=vst_pp_pft[:-1])
        else:
            self.customize_namelist(variable='hist_mfilt',value='1,365')
            self.customize_namelist(variable='hist_nhtfrq',value='-8760,-24')
        self.customize_namelist(variable='hist_fincl2',value=vst_pp[:-1])
