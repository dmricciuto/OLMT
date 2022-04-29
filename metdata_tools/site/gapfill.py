import numpy as np


def diurnal_mean(var, window=10, npd=24):

  diurnal_mean = np.zeros([365,npd], np.float)
  for d in range(0,365):
    for h in range(0,npd):
      diurnal_mean[d,h] = np.nanmean(var[max(d-window,0)*npd+h:min(d+window,364)*npd+h:npd])
  
  for i in range(0,len(var)):
    if (np.isnan(var[i])):
      d = int((i % 365*npd) / npd)
      h = int(i % npd)
      var[i] = diurnal_mean[d,h]


