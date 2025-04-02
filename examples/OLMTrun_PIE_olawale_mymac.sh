cd ~/mygithub/E3SM_REPOS/OLMT

metdir=~/mygithub/E3SM_REPOS/pt-e3sm-inputdata/atm/datm7/1x1pt_US-PIE/cpl_bypass_US-PIE
domain=~/Documents/Works/TAI/Plum_Island_Sound_LTER/datafrom_olawale/PIE_domain_threecell.nc
surf=~/Documents/Works/TAI/Plum_Island_Sound_LTER/datafrom_olawale/PIE_surfdata_threecell_1.nc
#surf=~/Documents/Works/TAI/Plum_Island_Sound_LTER/datafrom_olawale/PIE_surfdata_threecell_1.4NADV.nc

python site_fullrun.py --site US-PLM1 --sitegroup Wetland --caseidprefix PIE_alquimia_lev1.4m_C_LocMet  \
                       --nyears_ad_spinup 200 --nyears_final_spinup 600 --tstep 1 --nyears_transient 174 \
                       --cpl_bypass --machine mymac --no_dynroot --spinup_vars  --nofire --nopftdyn --nopointdata \
                       --notrans --nofnsp --no_submit \
                       --model_root /Users/f9y/mygithub/E3SM_REPOS/E3SM_ORNL_IM \
                       --ccsm_input /Users/f9y/mygithub/E3SM_REPOS/pt-e3sm-inputdata \
                       --metdata_dir $metdir \
                       --domainfile $domain \
                       --surffile $surf \
                       --caseroot /Users/f9y/project_e3sm/cases --runroot /Users/f9y/project_e3sm/scratch/ --mpilib mpich --pio_version 2 \
                       --hist_nhtfrq_trans -1 --hist_mfilt_trans 8760 --hist_mfilt_spinup 0 --hist_nhtfrq_spinup 12 --cn_only --np 3 \
                       --trans_varlist "TOTVEGC,TOTSOMC,TOTLITC,SOIL1C_vr,SOIL2C_vr,SOIL3C_vr,SOIL4C_vr,LITR1C_vr,LITR2C_vr,LITR3C_vr,HR,GPP,NEE,NPP,SMINN,SMINN_TO_PLANT,SOILLIQ,SOILICE,H2OSOI,H2OSFC,QFLX_ADV,QFLX_TIDE,QFLX_EVAP_TOT,QVEGT,watsat,SMINN_vr,SMIN_NO3_vr,TSOI,SALINITY" \
                       --marsh \
                       --tide_forcing_file /Users/f9y/Documents/Works/TAI/Plum_Island_Sound_LTER/datafrom_olawale/PIE_tide_forcing.nc \
                       --parm_file /Users/f9y/Documents/Works/TAI/Plum_Island_Sound_LTER/datafrom_olawale/parms_PIE
 
# if coupled with pflotran via alquimia, add the following options
#                       --alquimia ~/ELM-PFLOTRAN_ROOT/REDOX-PFLOTRAN/ELM_decks/CTC_alquimia_forELM_O2consuming.in \
#                       --alquimia_ad ~/ELM-PFLOTRAN_ROOT/REDOX-PFLOTRAN/ELM_decks/CTC_alquimia_forELM_O2consuming_adspinup.in \

