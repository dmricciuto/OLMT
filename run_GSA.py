import os, math, sys
import numpy as np
from optparse import OptionParser
import model_surrogate as models
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

parser = OptionParser()
parser.add_option("--case", dest="casename", default="", \
                  help="Name of case")
(options, args) = parser.parse_args()

GSAdir = './UQ_output/'+options.casename+'/GSA'
os.system('mkdir -p '+GSAdir+'/analyses')

os.system('python -m SALib.sample.saltelli -n 8192 -p '+GSAdir+'/param_range.txt -o '+ \
                  GSAdir+'/Saltelli_samples.txt')
#Create the model object
model = models.MyModel(case=options.casename)

#Get the parameter samples for GSA
samples=np.loadtxt(GSAdir+'/Saltelli_samples.txt')

#Run the NN surrogate model
model.run(samples)

np.savetxt(GSAdir+'/outputs.txt',model.output)

#Run GSA for each QOI
sens_main = np.zeros([model.nparms,model.nobs])
sens_main_unc = np.zeros([model.nparms,model.nobs])
sens_tot = np.zeros([model.nparms,model.nobs])
sens_tot_unc = np.zeros([model.nparms,model.nobs])

for n in range(0,model.nobs):
  print(n)
  os.system('python -m SALib.analyze.sobol --parallel -p '+GSAdir+'/param_range.txt -Y '+GSAdir+ \
            '/outputs.txt -c '+str(n)+' > '+GSAdir+'/analyses/analysis_ob'+str(n)+'.txt')
  myfile = open(GSAdir+'/analyses/analysis_ob'+str(n)+'.txt','r')
  lnum=0
  for s in myfile:
    print(s)
    if (lnum > 0 and lnum <= model.nparms):
      sens_tot[lnum-1,n] = float(s.split()[1])
      sens_tot_unc[lnum-1,n] = float(s.split()[2])
    elif (lnum > model.nparms+1 and lnum <= model.nparms*2+1):
      sens_main[lnum-2-model.nparms,n] = float(s.split()[1])
      sens_main_unc[lnum-2-model.nparms,n] = float(s.split()[2])    
    lnum=lnum+1
  myfile.close()

#Plot main sensitivity indices
fig,ax = plt.subplots()
x_pos = np.cumsum(np.ones(model.nobs))
x_labels=model.obs_name.copy()
for i in range(1,len(x_labels)):
    if (model.obs_name[i] == model.obs_name[i-1]):
        x_labels[i]=' '
ax.bar(x_pos, sens_main[0,:], align='center', alpha=0.5)
ax.set_xticks(x_pos)
ax.set_xticklabels(x_labels, rotation=45)
bottom=sens_main[0,:]
for p in range(1,model.nparms):
    ax.bar(x_pos, sens_main[p,:], bottom=bottom)
    bottom=bottom+sens_main[p,:]
plt.legend(model.parm_names)
plt.savefig(GSAdir+'/sens_main.pdf')

#Total sensitivity indices
fig,ax = plt.subplots()
ax.bar(x_pos, sens_tot[0,:], align='center', alpha=0.5)
ax.set_xticklabels(x_labels, rotation=45)
bottom=sens_tot[0,:]
for p in range(1,model.nparms):
    ax.bar(x_pos, sens_tot[p,:], bottom=bottom)
    bottom=bottom+sens_tot[p,:]
plt.legend(model.parm_names)
plt.savefig(GSAdir+'/sens_tot.pdf')

