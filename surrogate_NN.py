from netCDF4 import Dataset
from sklearn.neural_network import MLPRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, math, sys
import numpy as np
#from mpi4py import MPI
import pickle
from optparse import OptionParser


parser = OptionParser()
parser.add_option("--case", dest="casename", default="", \
                  help="Name of case")
(options, args) = parser.parse_args()

UQ_output = 'UQ_output/'+options.casename
datapath = UQ_output+'/data/'
os.system('mkdir -p '+UQ_output+'/NN_surrogate')

#comm=MPI.COMM_WORLD
#rank=comm.Get_rank()
#size=comm.Get_size()

ptrain = np.loadtxt(datapath+'/ptrain.dat')
ytrain = np.loadtxt(datapath+'/ytrain.dat')
pval   = np.loadtxt(datapath+'/pval.dat')
yval   = np.loadtxt(datapath+'/yval.dat')

nparms = ptrain.shape[1]
ntrain = ptrain.shape[0]
nval   = pval.shape[0]
nqoi   = ytrain.shape[1]

ptrain_norm = ptrain.copy()
pval_norm   = pval.copy()

for i in range(0,nparms):
  ptrain_norm[:,i] = (ptrain[:,i] - min(ptrain[:,i]))/(max(ptrain[:,i])-min(ptrain[:,i]))
  pval_norm[:,i]   = (pval[:,i]  -  min(ptrain[:,i]))/(max(ptrain[:,i])-min(ptrain[:,i]))
  for j in range(0,nval):
    pval_norm[j,i] = max(pval_norm[j,i], 0.0)
    pval_norm[j,i] = min(pval_norm[j,i], 1.0)


rmse_best = 9999
corr_best = 0
for n in range(0,100):
  nmin = 10*np.sqrt(n+1) #max(10, ntrain/20)
  nmax = 20*np.sqrt(n+1) #min(ntrain/4, 100)
  nl = int(np.random.uniform(nmin,nmax))
  nl2 = int(np.random.uniform(nmin,nmax))*2
  do3 = 0 #np.random.uniform(0,1)
  nl3 = int(np.random.uniform(nmin,nmax))
  if (do3 > 0.5):
    clf = MLPRegressor(solver='adam', early_stopping=True, tol=1e-7, hidden_layer_sizes=(nl,nl2,nl3,), max_iter=200, validation_fraction=0.2)
  else: 
    clf = MLPRegressor(solver='adam', early_stopping=True, tol=1e-7, hidden_layer_sizes=(nl,nl2,), max_iter=200, validation_fraction=0.2)
  clf.fit(ptrain_norm, ytrain) 

  ypredict_train = clf.predict(ptrain_norm)
  ypredict_val   = clf.predict(pval_norm)

  corr_train=[]
  rmse_train = []
  corr_val=[]
  rmse_val=[]
  for qoi in range(0,nqoi):
    corr_train.append((np.corrcoef(ytrain.astype(float)[:,qoi], ypredict_train.astype(float)[:,qoi])[0,1])**2)
    rmse_train.append((sum((ypredict_train[:,qoi]-ytrain[:,qoi])**2)/ntrain)**0.5)
    corr_val.append((np.corrcoef(yval.astype(float)[:,qoi], ypredict_val.astype(float)[:,qoi])[0,1])**2)
    rmse_val.append((sum((ypredict_val[:,qoi]-yval[:,qoi])**2)/nval)**0.5)

  if (sum(corr_val) > corr_best):
    myfile = open(UQ_output+'/NN_surrogate/fitstats.txt','w')
    myfile.write('Number of parameters:         '+str(nparms)+'\n')
    myfile.write('Number of outputs:            '+str(nqoi)+'\n')
    myfile.write('Number of training samples:   '+str(ntrain)+'\n')
    myfile.write('Number of validation samples: '+str(nval)+'\n\n')
    myfile.write('Best neural network:\n')
    myfile.write('Size of NN layer 1: '+str(nl)+'\n')
    myfile.write('Size of NN layer 2: '+str(nl2)+'\n')
    if (do3 == 1):
      myfile.write('Size of NN layer 3: '+str(nl3)+'\n')
    for q in range(0,nqoi):
      myfile.write('QOI validation '+str(q)+' (R2,rmse): '+str(corr_val[q])+'  '+str(rmse_val[q]**2)+'\n')
    corr_best = sum(corr_val)
    pkl_filename = UQ_output+'/NN_surrogate/NNmodel.pkl'
    ypredict_val_best = ypredict_val
    with open(pkl_filename,'wb') as file:
      pickle.dump(clf, file)
    for q in range(0,nqoi):
      plt.clf()
      plt.scatter(yval[:,q], ypredict_val_best[:,q])
      plt.savefig(UQ_output+'/NN_surrogate/nnfit_qoi'+str(q)+'.pdf')
      myfile.close()
  if (min(corr_val) > 0.925):
    print('All QOIs have R2 > 0.925')
    break
