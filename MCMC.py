import numpy as np
from scipy.stats import norm
import model_surrogate as models
import os, math, random
import matplotlib
matplotlib.use('Agg')
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--case", dest="casename", default="", \
                  help="Name of case")
parser.add_option("--nevals", dest="nevals", default="200000", \
                  help="Number of model evaluations")
parser.add_option("--burnsteps", dest="burnsteps", default="10", \
                  help="Number burn steps")
parser.add_option("--parm_list", dest="parm_list", default='parm_list', \
                  help = 'File containing list of parameters to vary')
(options, args) = parser.parse_args()

UQ_output = 'UQ_output/'+options.casename
os.system('mkdir -p '+UQ_output+'/MCMC_output')

def posterior(parms):
    #Calculate the posterior (prior and log likelihood)
    line = 0
    #Uniform priors
    prior = 1.0
    for j in range(0,model.nparms):
        if (parms[j] < model.pmin[j] or parms[j] > model.pmax[j]):
            prior = 0.0

    post = prior
    if (prior > 0.0):
        model.run(parms)
        myoutput = model.output.flatten()
        myobs    = model.obs.flatten()
        myerr    = model.obs_err.flatten()
        for v in range(0,len(myoutput)):
            if (abs(myobs[v]) < 1e5 and myerr[v] > 0):
                resid = (myoutput[v] - myobs[v])
                ri = (resid/myerr[v])**2
                li = -1.0 * np.log(2.0*np.pi)/2.0 - \
                     np.log(myerr[v]) - ri/2.0
                post = post + li
    else:
        post = -9999999
    return(post)

#-------------------------------- MCMC ------------------------------------------------------

def MCMC(parms, nevals, type='uniform', nburn=1000, burnsteps=10):
    #Metropolis-Hastings Markov Chain Monte Carlo with adaptive sampling
    post_best = -99999
    post_last = -99999
    accepted_step = 0
    accepted_tot  = 0
    nparms     = model.nparms
    #parms      = np.zeros(nparms)
    parm_step  = np.zeros(nparms)
    chain      = np.zeros((nparms+1,nevals))
    chain_prop = np.zeros((nparms,nevals))
    chain_burn = np.zeros((nparms,nevals))
    output     = np.zeros((model.nobs,nevals))
    mycov      = np.zeros((nparms,nparms))

    for p in range(0,nparms):
        #Starting step size = 1% of prior range
        #parm_step[p] = 2.4**2/nparms * (model.pmax[p]-model.pmin[p])
        parm_step[p] = 0.05 * (model.pmax[p]-model.pmin[p])
        #parms[p] = np.random.uniform(parms[p]-parm_step[p],parms[p]+parm_step[p],1)
        parms[p] = model.pdef[p]
        #parms_sens = np.copy(parms)
        #vary this parameter by one step
        #parms_sens[p] = parms_sens[p]+parm_step[p]
        #post_sens = posterior(parms_sens)
        #use 1D sensitivities to decrease the step sizes accordingly
        #print p, np.absolute(post_def - post_sens)
        #if (np.absolute(post_def - post_sens) > 1.0):
        #    parm_step[p] = parm_step[p]/(np.absolute(post_def - post_sens))
    for i in range(0,nparms):
        mycov[i,i] = parm_step[i]**2

    parm_last = parms
    scalefac = 1.0

    for i in range(0,nevals):

         #update proposal step size
        if (i > 0 and (i % nburn) == 0 and i < burnsteps*nburn):
            acc_ratio = float(accepted_step) / nburn
            mycov_step = np.cov(chain_prop[0:nparms,accepted_tot- \
                                              accepted_step:accepted_tot])
            mycov_chain = np.cov(chain_burn[0:nparms,int(accepted_tot/4):accepted_tot])
            thisscalefac = 1.0
            #Compute scaling factors for step sizes based on acceptance ratio
            if (acc_ratio <= 0.2):
                thisscalefac = max(acc_ratio/0.3, 0.15)
            elif (acc_ratio > 0.4):
                thisscalefac = min(acc_ratio/0.3, 2.5)
            scalefac = scalefac * thisscalefac
            #Calculate covariance matrix of recent samples
            for j in range(0,nparms):
                for k in range(0,nparms):
                    if (acc_ratio > 0.05):
                        mycov[j,k] = mycov_chain[j,k] * scalefac
                            #if (j == k):
                            #mycov[j,k] =
                                #scalefac* max(mycov_chain[j,j] / \
                                       #  mycov_step[j,j], 1) * mycov_step[j,j]
                    else:
                        #if (j == k):
                        mycov[j,k] = thisscalefac * mycov[j,k]
                    if (j == k):
                        print(j, scalefac,mycov[j,j]/(parm_step[j]**2))


            print('BURNSTEP', i/nburn, acc_ratio, thisscalefac, scalefac)
            mycov_step = np.cov(chain_prop[0:nparms,accepted_tot- \
                                                  accepted_step:accepted_tot])
            #print(np.corrcoef(chain[0:4,i-nburn:i]))
            accepted_step = 0
    
    
        if (i == burnsteps*nburn):
        #Parameter chain plots
            for p in range(0,nparms):
                fig = plt.figure()
                xchain = np.cumsum(np.ones(int(nburn*burnsteps)))
                plt.plot(xchain, chain[p,0:int(nburn*burnsteps)])
                plt.xlabel('Evaluations')
                plt.ylabel(model.parm_names[p])
                if not os.path.exists(UQ_output+'/MCMC_output/plots/chains'):
                    os.makedirs(UQ_output+'/MCMC_output/plots/chains')
                plt.savefig(UQ_output+'/MCMC_output/plots/chains/burnin_chain_'+model.parm_names[p]+'.pdf')
                plt.close(fig) 
    
        #get proposal step
        parms = np.random.multivariate_normal(parm_last, mycov)
   
        #------- run the model and calculate log likelihood -------------------
        post = posterior(parms)
        
        #determine whether proposal step is accepted
        if ( (post - post_last < np.log(random.uniform(0,1)))):
            #if not accepted, go back to previous step
            for j in range(0,nparms):
                parms[j] = parm_last[j]
        else:
            #proposal step is accepted
            post_last = post
            accepted_tot = accepted_tot+1
            accepted_step = accepted_step+1
            chain_prop[0:nparms,accepted_tot] = parms-parm_last
            chain_burn[0:nparms,accepted_tot] = parms
            parm_last = parms
            #keep track of best solution so far
            if (post > post_best):
                post_best = post
                parms_best = parms
                print(post_best)
                output_best = model.output

        #populate the chain matrix
        for j in range(0,nparms):
            chain[j][i] = parms[j]
        chain[nparms][i] = post_last
        for j in range(0,model.nobs):
            output[j,i] = model.output[j]

        if (i % 1000 == 0):
            print(' -- '+str(i)+' --\n')

    print("Computing statistics")
    chain_afterburn = chain[0:nparms,int(nburn*burnsteps):]
    chain_sorted = chain_afterburn
    output_sorted = output[0:model.nobs,int(nburn*burnsteps):]
    output_sorted.sort()

    np.savetxt(UQ_output+'/MCMC_output/MCMC_chain.txt', np.transpose(chain_afterburn))
    #Print out some statistics
    parm_data=open(options.parm_list,'r')
    parm_best=open(UQ_output+'/MCMC_output/parms_best.txt','w')
    p=0
    for s in parm_data:
      row = s.split()
      parm_best.write(row[0]+' '+row[1]+' '+str(parms_best[p])+'\n')
      p=p+1
    parm_data.close()
    parm_best.close()
    np.savetxt(UQ_output+'/MCMC_output/correlation_matrix.txt',np.corrcoef(chain_afterburn))

    #parameter correlation plots (threshold correlations)
    #corr_thresh = 0.8
    #for p1 in range(0,nparms-1):
    #  for p2 in range(p1+1,nparms):
    #    if (abs(parmcorr[p1,p2]) > corr_thresh):
    #      fig = plt.figure()
    #      plt.hexbin(chain_afterburn[p1,:],chain_afterburn[p2,:])
    #      cbar = plt.colorbar()
    #      cbar.set_label('bin count')
    #      plt.xlabel(model.parm_names[p1])
    #      plt.ylabel(model.parm_names[p2])
    #
    #      plt.suptitle('r = '+str(parmcorr[p1,p2]))
    #      if not os.path.exists(UQ_output+'/MCMC_output/plots/corr'):
    #           os.makedirs(UQ_output+'/MCMC_output/plots/corr')
    #      plt.savefig(UQ_output+'/MCMC_output/plots/corr/corr_'+model.parm_names[p1]+'_'+model.parm_names[p2]+'.pdf')
    #      plt.close(fig)
    #Parameter chain plots
    for p in range(0,nparms):
        fig = plt.figure()
        xchain = np.cumsum(np.ones(nevals-int(nburn*burnsteps)))
        plt.plot(xchain, chain_afterburn[p,:])
        plt.xlabel('Evaluations')
        plt.ylabel(model.parm_names[p])
        if not os.path.exists(UQ_output+'/MCMC_output/plots/chains'):
            os.makedirs(UQ_output+'/MCMC_output/plots/chains')
        plt.savefig(UQ_output+'/MCMC_output/plots/chains/chain_'+model.parm_names[p]+'.pdf')
        plt.close(fig)

    chain_sorted.sort()
    parm95=open(UQ_output+'/MCMC_output/parms_95pctconf.txt','w')
    for p in range(0,nparms):
        parm95.write(str(model.parm_names[p])+' '+ \
        str(chain_sorted[p,int(0.025*(nevals-nburn*burnsteps))])+' '+ \
        str(chain_sorted[p,int(0.975*(nevals-nburn*burnsteps))])+'\n')
    parm95.close()
    print("Ratio of accepted steps to total steps:")
    print(float(accepted_tot)/nevals)
    out95=open(UQ_output+'/MCMC_output/outputs_95pctconf.txt','w')
    for p in range(0,model.nobs):
        out95.write(str(output_sorted[p,int(0.025*(nevals-nburn*burnsteps))])+' '+ \
        str(output_sorted[p,int(0.975*(nevals-nburn*burnsteps))])+'\n')
    out95.close()
    #make parameter histogram plots
    for p in range(0,nparms):
        fig = plt.figure()
        n, bins, patches = plt.hist(chain_afterburn[p,:],25,normed=1)
        plt.xlabel(model.parm_names[p])
        plt.ylabel('Probability Density')
        if not os.path.exists(UQ_output+'/MCMC_output/plots/pdfs'):
            os.makedirs(UQ_output+'/MCMC_output/plots/pdfs')
        plt.savefig(UQ_output+'/MCMC_output/plots/pdfs/'+model.parm_names[p]+'.pdf')
        plt.close(fig)

    #make prediction plots
    fig = plt.figure()
    ax=fig.add_subplot(111)
    x = np.cumsum(np.ones([model.nobs],np.float))
    ax.errorbar(x,model.obs, yerr=model.obs_err, label='Observations')
    ax.plot(x,output_best,'r', label = 'Model best')
    ax.plot(x,output_sorted[:,int(0.025*(nevals-nburn*burnsteps))], \
                 'k--', label='Model 95% CI')
    ax.plot(x,output_sorted[:,int(0.975*(nevals-nburn*burnsteps))],'k--')
    #plt.xlabel(model.xlabel)
    #plt.ylabel(model.ylabel)
    box = ax.get_position()
    ax.set_position([box.x0,box.y0,box.width*0.8,box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1,0.5), fontsize='small')
    if not os.path.exists(UQ_output+'/MCMC_output/plots/predictions'):
        os.makedirs(UQ_output+'/MCMC_output/plots/predictions')
    plt.savefig(UQ_output+'/MCMC_output/plots/predictions/Predictions.pdf')
    plt.close(fig)
    return parms_best


#Create the model object
model = models.MyModel(case=options.casename)
#run MCMC
parms = MCMC(model.pdef, int(options.nevals), burnsteps=int(options.burnsteps), \
                          nburn=int(options.nevals)/(2*int(options.burnsteps)))

plt.show()

