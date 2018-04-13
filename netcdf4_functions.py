#Python utilities for reading and writing variables to a netcdf file
#  using Scientific Python OR scipy, whichever available

def getvar(fname, varname):
    from netCDF4 import Dataset
    nffile = Dataset(fname,"r")
    varvals = nffile.variables[varname][:]
    nffile.close()
    return varvals

def putvar(fname, varname, varvals):
    from netCDF4 import Dataset
    import numpy as np
    nffile = Dataset(fname,"a")
    nffile.variables[varname][...] = varvals
    nffile.close()
    ierr = 0
    return ierr
