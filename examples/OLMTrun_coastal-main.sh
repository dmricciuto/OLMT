site=BEO
metdir=$HOME/mygithub/E3SM_REPOS/pt-e3sm-inputdata/atm/datm7/Daymet_ERA5_ngee4/cpl_bypass_$site
domain=$HOME/mygithub/E3SM_REPOS/pt-e3sm-inputdata/share/domains/domain.clm/domain.lnd.7x1pt_beo-NGEE_areaC_navy.nc
surf=$HOME/mygithub/E3SM_REPOS/pt-e3sm-inputdata/lnd/clm2/surfdata_map/surfdata_7x1pt_beo-NGEE_areaC_simyr1850_c20230320-sub12+.nc
paramfile=$HOME/mygithub/E3SM_REPOS/pt-e3sm-inputdata/lnd/clm2/paramdata/clm_params_c180524-sub12+_updated20240201.nc

varlist="TOTVEGC,TOTSOMC,TOTLITC,SOIL1C_vr,SOIL2C_vr,SOIL3C_vr,SOIL4C_vr,LITR1C_vr,LITR2C_vr,LITR3C_vr,LEAFC,\
HR,ER,GPP,NEE,NPP,SMINN,SMINN_TO_PLANT,H2OSOI,H2OSFC,SOILLIQ,SOILICE,ZWT,\
QFLX_EVAP_TOT,QVEGT,watsat,TSOI,H2OSFC_TIDE,ALT,SNOW,SNOWDP,\
FCH4,FCH4TOCO2,CH4PROD,RAIN,TSA,FSAT,ZWT_PERCH,TBOT,FSDS,EFLX_LH_TOT,FSH,\
FINUNDATED,CH4_SURF_DIFF_SAT,CH4_SURF_DIFF_UNSAT,CH4_EBUL_TOTAL_SAT,CH4_EBUL_TOTAL_UNSAT,CH4_SURF_EBUL_SAT,\
CH4_SURF_EBUL_UNSAT,CH4_SURF_AERE_SAT,CH4_SURF_AERE_UNSAT,CONC_CH4_SAT,CONC_CH4_UNSAT,CONC_O2_SAT,CONC_O2_UNSAT"

python ./site_fullrun.py --site AK-BEO --sitegroup NGEEArctic --caseidprefix Alaska_defaultCH4_arctic_BAM_6 \
--nyears_ad_spinup 300 --nyears_final_spinup 400 --tstep 1 --nyears_transient 173 \
--cpl_bypass --machine mymac --no_dynroot --era5 --daymet4 --nofire --nopftdyn --nopointdata \
--model_root $HOME/mygithub/E3SM_REPOS/E3SM_ORNL_IM \
--ccsm_input $HOME/mygithub/E3SM_REPOS/pt-e3sm-inputdata \
--domainfile $domain \
--metdir $metdir \
--surffile $surf --np 7 --walltime 24 --maxpatch_pft 14 \
--mod_parm_file $paramfile \
--caseroot $HOME/project_e3sm/cases \
--runroot $HOME/project_e3sm/scratch  \
--mpilib mpich --pio_version 2 \
--hist_nhtfrq_trans -1 --hist_mfilt_trans 8760 --hist_mfilt_spinup 0 --hist_nhtfrq_spinup 12 --cn_only \
--trans_varlist $varlist

#--marsh
#--tide_forcing_file $HOME/NGEE_ELM/BEO_hydro_BC_multicell.nc


