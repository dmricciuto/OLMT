import os, math, sys
import numpy as np
from optparse import OptionParser
import model_surrogate as models
import matplotlib
import matplotlib.pyplot as plt
from SALib.sample import saltelli
from SALib.analyze import sobol
import matplotlib.patches as mpatches
matplotlib.use('Agg')


def GSA(self, myvars, n_saltelli=8192):
    #Get parameter bounds
    pbounds = np.zeros([self.nparms_ensemble,2],float)
    for p in range(0,self.nparms_ensemble):
        print(p, self.nparms_ensemble, self.ensemble_pmin[p])
        pbounds[p,0]=self.ensemble_pmin[p]
        pbounds[p,1]=self.ensemble_pmax[p]

    problem = {
            'num_vars': self.nparms_ensemble,
            'names': self.ensemble_parms,
            'bounds': pbounds
            }
    psamples = saltelli.sample(problem, n_saltelli)

    surrogate_output = self.run_surrogate(psamples, myvars)
    self.sens_main={}
    self.sens_tot={}

    for v in myvars:
      nvar = surrogate_output[v].shape[1]
      self.sens_main[v] = np.zeros([self.nparms_ensemble,nvar],float)
      self.sens_tot[v]  = np.zeros([self.nparms_ensemble,nvar],float)
      for i in range(0,nvar):
        Si = sobol.analyze(problem, surrogate_output[v][:,i])
        self.sens_main[v][:,i]=Si['S1']
        self.sens_tot[v][:,i]=Si['ST']

    
def plot_GSA(self, myvars):
    UQ_output = './UQ_output/' + self.casename + '/GSA'
    os.makedirs(UQ_output, exist_ok=True)  # Ensures the directory exists
    
    for v in myvars:
        if v != 'taxis':
            # Create the figure and axis
            fig, ax = plt.subplots(figsize=(10, 6))  # Larger figure for better visualization
            
            nvar = self.sens_main[v].shape[1]
            x_pos = np.arange(nvar)
            
            # Define distinct colors and patterns
            colors = plt.cm.tab20.colors  # Use a colormap for distinct colors
            hatches = ['/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*']  # Patterns
            
            # Plot the stacked bars
            bottom = np.zeros(nvar)
            patches = []  # Store legend handles
            
            for p in range(self.nparms_ensemble):
                color = colors[p % len(colors)]
                hatch = hatches[p % len(hatches)]
                bar = ax.bar(
                    x_pos, 
                    self.sens_main[v][p, :], 
                    bottom=bottom, 
                    color=color, 
                    hatch=hatch, 
                    edgecolor='black'
                )
                bottom += self.sens_main[v][p, :]
                
                # Create a legend entry
                patches.append(mpatches.Patch(facecolor=color, hatch=hatch, edgecolor='black', label=self.ensemble_parms[p]))
            
            # Adjust the axis and labels
            ax.set_xticks(x_pos)
            ax.set_xticklabels([f'Var {i+1}' for i in range(nvar)], rotation=45)
            ax.set_ylabel('Sensitivity Index')
            ax.set_title(f'Main Sensitivity Indices for {v}')
            
            # Place legend outside the plot
            ax.legend(
                handles=patches, 
                loc='upper left', 
                bbox_to_anchor=(1, 1), 
                title='Parameters'
            )
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(UQ_output + f'/sens_main_{v}.png', bbox_inches='tight')
            plt.close(fig)  # Close the figure to free memory

            #Plot total sensitivity
            fig, ax = plt.subplots(figsize=(10, 6))  # Larger figure for better visualization
            # Plot the stacked bars
            bottom = np.zeros(nvar)
            patches = []  # Store legend handles

            for p in range(self.nparms_ensemble):
                color = colors[p % len(colors)]
                hatch = hatches[p % len(hatches)]
                bar = ax.bar(
                    x_pos,
                    self.sens_tot[v][p, :],
                    bottom=bottom,
                    color=color,
                    hatch=hatch,
                    edgecolor='black'
                )
                bottom += self.sens_tot[v][p, :]

                # Create a legend entry
                patches.append(mpatches.Patch(facecolor=color, hatch=hatch, edgecolor='black', label=self.ensemble_parms[p]))

            # Adjust the axis and labels
            ax.set_xticks(x_pos)
            ax.set_xticklabels([f'Var {i+1}' for i in range(nvar)], rotation=45)
            ax.set_ylabel('Sensitivity Index')
            ax.set_title(f'Total Sensitivity Indices for {v}')

            # Place legend outside the plot
            ax.legend(
                handles=patches,
                loc='upper left',
                bbox_to_anchor=(1, 1),
                title='Parameters'
            )

            # Save the plot
            plt.tight_layout()
            plt.savefig(UQ_output + f'/sens_tot_{v}.png', bbox_inches='tight')
            plt.close(fig)  # Close the figure to free memory
