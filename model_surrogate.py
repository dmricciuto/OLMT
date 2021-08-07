import numpy as np
from sklearn.neural_network import MLPRegressor
import pickle
 
class MyModel(object):

    def __init__(self,case=''):

        UQdir = './UQ_output/'+case
        self.ptrain = np.loadtxt(UQdir+'/data/ptrain.dat')
        self.ytrain = np.loadtxt(UQdir+'/data/ytrain.dat')
        self.nparms = self.ptrain.shape[1]
        self.nobs   = self.ytrain.shape[1]
        self.ntrain=self.ptrain.shape[0]
        self.yrange = np.zeros([2,self.nobs],np.float)
        for i in range(0,self.nobs):
          self.yrange[0,i] = min(self.ytrain[:,i])
          self.yrange[1,i] = max(self.ytrain[:,i])

        self.pmin = np.zeros([self.nparms], np.float)
        self.pmax= np.zeros([self.nparms], np.float)
        for i in range(0,self.nparms):
          self.pmin[i] = min(self.ptrain[:,i])
          self.pmax[i] = max(self.ptrain[:,i])

        pnamefile = open(UQdir+'/data/pnames.txt','r')
        self.parm_names = []
        for s in pnamefile:
          self.parm_names.append(s[:-1])
        pnamefile.close()
        print(self.parm_names, self.nobs, self.nparms)
        self.pdef = np.zeros([self.nparms], np.float)
        for i in range(0,self.nparms):
          self.pdef[i] = (self.pmin[i]+self.pmax[i])/2

        self.obs = np.zeros([self.nobs],np.float)
        self.obs_err = np.zeros([self.nobs],np.float)
        obsfile = open(UQdir+'/data/obs.dat')
        i=0
        for s in obsfile:
          self.obs[i] = np.float(s.split()[0])
          self.obs_err[i] = np.float(s.split()[1])
          i=i+1
        obsfile.close()
        pkl_filename = UQdir+'/NN_surrogate/NNmodel.pkl'
        with open(pkl_filename, 'rb') as file:
          self.nnmodel = pickle.load(file)

    def run(self,parms):
        parms_nn = np.zeros([1,self.nparms],np.float)
        for p in range(0,self.nparms):
          parms_nn[0,p] = (parms[p]-self.pmin[p])/(self.pmax[p]-self.pmin[p])
        self.output = self.nnmodel.predict(parms_nn).flatten()
        for q in range(0,len(self.output)):
          self.output[q] = self.output[q]*(self.yrange[1,q]-self.yrange[0,q])+self.yrange[0,q]
