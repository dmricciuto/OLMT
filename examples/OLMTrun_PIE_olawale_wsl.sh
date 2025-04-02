cd ~/models/OLMT

metdir=~/pt-e3sm-inputdata/atm/datm7/1x1pt_US-PIE/cpl_bypass_US-PIE
domain=~/mydata/PIEsites_bsulman/datafrom_olawale/PIE_domain_threecell.nc
#surf=~/mydata/PIEsites_bsulman/datafrom_olawale/PIE_surfdata_threecell_1.nc
surf=~/mydata/PIEsites_bsulman/datafrom_olawale/PIE_surfdata_thereecell_1.4NADV.nc

python site_fullrun.py --site US-PLM1 --sitegroup Wetland --caseidprefix PIE_alquimia_Elev1m_C_LocMet  \
                       --nyears_ad_spinup 100 --nyears_final_spinup 100 --tstep 1 --nyears_transient 174 \
                       --cpl_bypass --machine wsl --no_dynroot --spinup_vars  --nofire --nopftdyn --nopointdata \
                       --model_root /home/fmyuan/models/E3SM_tai --ccsm_input /home/fmyuan/pt-e3sm-inputdata \
                       --metdata_dir $metdir \
                       --domainfile $domain \
                       --surffile $surf \
                       --caseroot ~/project_e3sm/cases --runroot ~/e3sm_scratch/runs  --mpilib openmpi --pio_version 2 \
                       --hist_nhtfrq_trans -1 --hist_mfilt_trans 8760 --hist_mfilt_spinup 0 --hist_nhtfrq_spinup 12 --cn_only --np 3 \
                       --trans_varlist "TOTVEGC,TOTSOMC,TOTLITC,SOIL1C_vr,SOIL2C_vr,SOIL3C_vr,SOIL4C_vr,LITR1C_vr,LITR2C_vr,LITR3C_vr,soil_O2,HR,GPP,NEE,NPP,SMINN,SMINN_TO_PLANT,DIC_vr,SOILLIQ,SOILICE,H2OSOI,H2OSFC,QFLX_ADV,QFLX_EVAP_TOT,QVEGT,watsat,chem_dt,soil_pH,DOC_vr,DIC_vr,DOC_RUNOFF,DIC_RUNOFF,CH4FLUX_ALQUIMIA,soil_Fe2,soil_FeOxide,soil_sulfate,soil_sulfide,soil_FeS,CH4_vr,SMINN_vr,SMIN_NO3_vr,TSOI,soil_salinity,SALINITY" \
                       --alquimia ~/ELM-PFLOTRAN_ROOT/REDOX-PFLOTRAN/ELM_decks/CTC_alquimia_forELM_O2consuming.in \
                       --alquimia_ad ~/ELM-PFLOTRAN_ROOT/REDOX-PFLOTRAN/ELM_decks/CTC_alquimia_forELM_O2consuming_adspinup.in \
                       --marsh \
		       --tide_forcing_file ~/mydata/PIEsites_bsulman/datafrom_olawale/PIE_tide_forcing.nc \
		       --parm_file ~/mydata/PIEsites_bsulman/datafrom_olawale/parms_PIE
 

