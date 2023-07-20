% This script is used for reading and processing variables from ELM outputs
% Reading output variables
OUTDIR='/home/whf/scratch/';
RUNcase='EM05';
year=2018;
column_n=2
ensemble_n=30;
CaseName = strcat(RUNcase,'_US-GMX_ICB20TRCNPRDCTCBC');
%f2=fopen(strcat('../runcase/results/H2OSFC_newNPP_',num2str(year),'_',RUNcase,'_vars_c',num2str(column_n),'.txt'),'wt');
%f2=fopen(strcat(RUNcase,'NPP_annual_35yr_',num2str(column_n),'.txt'),'wt')
ny=year-1987+1;
interval=3600;
for j=1:ensemble_n
  for i=year:year
  %for i=32:32
     Surf_file=strcat(OUTDIR,'/UQ/',CaseName,'/g000',num2str(j,'%02d'),'/surfdata_000',num2str(j,'%02d'),'.nc')
     organic=ncread(Surf_file,'ORGANIC');
     organic=organic(column_n,1);
     clm_file=strcat(OUTDIR,'/UQ/',CaseName,'/g000',num2str(j,'%02d'),'/clm_params_000',num2str(j,'%02d'),'.nc')
     organic_max=ncread(clm_file,'organic_max');
     organic_pct(j)=organic/organic_max;
     FileName = strcat(OUTDIR,'/UQ/',CaseName,'/g000',num2str(j,'%02d'),'/',CaseName,'.elm.h0.',num2str(i),'-01-01-00000.nc')
     AGNPP = ncread(FileName,'AGNPP');
     AGNPP = AGNPP(column_n,:);
     BGNPP = ncread(FileName,'BGNPP');
     BGNPP = BGNPP(column_n,:);
     FillData = 1.0e+36;
     id=find(AGNPP<FillData/10);
     AGNPP_annual(j) = sum(AGNPP(id))*interval;
     id=find(BGNPP<FillData/10);
     BGNPP_annual(j) = sum(BGNPP(id))*interval;
     NPP_annual(j)=AGNPP_annual(j)+BGNPP_annual(j);
   end
end
[organic_pct_sort,id]=sort(organic_pct);
organic_pct_sort'
AGNPP_annual(id)'
BGNPP_annual(id)'
NPP_annual(id)'
%AGNPP_annual=mean(AGNPP_annual)
%BGNPP_annual=mean(BGNPP_annual)
%NPP_annual=mean(NPP_annual)
