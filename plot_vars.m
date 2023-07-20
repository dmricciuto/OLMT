% This script is used for reading and processing variables from ELM outputs
% Reading output variables
OUTDIR='/home/whf/scratch/';
RUNcase='NMTB39b';
year=2018;
column_n=1
CaseName = strcat(RUNcase,'_US-GC4_ICB20TRCNPRDCTCBC');
f2=fopen(strcat('../runcase/results/H2OSFC_newNPP_',num2str(year),'_',RUNcase,'_vars_c',num2str(column_n),'.txt'),'wt');
%f2=fopen(strcat(RUNcase,'NPP_annual_35yr_',num2str(column_n),'.txt'),'wt')
ny=year-1987+1;
interval=3600;
for i=year:year
%for i=32:32
   FileName = strcat(OUTDIR,CaseName,'/run/',CaseName,'.elm.h0.',num2str(i),'-01-01-00000.nc')

   LEAFC = ncread(FileName,'LEAFC');
   AGNPP = ncread(FileName,'AGNPP');
   NPP   = ncread(FileName,'NPP');
   AGNPP = AGNPP(column_n,:);
   NPP   = NPP(column_n,:);
   TLAI  = ncread(FileName,'TLAI');
   BGNPP = ncread(FileName,'BGNPP');
   BGNPP = BGNPP(column_n,:);
   H2OSFC=ncread(FileName,'H2OSFC');
   H2OSFC=H2OSFC(column_n,:)/1000;
   ZWT=ncread(FileName,'ZWT');
   %ZWT=ZWT(1,:);
   FillData = 1.0e+36;
   id=find(LEAFC<FillData/10);
   LEAFC_annual(i) = sum(LEAFC(id));
   id=find(AGNPP<FillData/10);
   AGNPP_annual = sum(AGNPP(id))*interval
   id=find(NPP<FillData/10);
   NPP_annual   = sum(NPP(id))*interval
   id=find(TLAI<FillData/10);
   TLAI_annual(i)  = sum(TLAI(id));
   id=find(BGNPP<FillData/10);
   BGNPP_annual = sum(BGNPP(id))*interval
   %fprintf(f2,'%d %10f %10f %10f\n',[i NPP_annual AGNPP_annual BGNPP_annual]);
   for j=1:length(H2OSFC)
     fprintf(f2,'%f %10f %10f\n',[j/24 H2OSFC(j) AGNPP(j)+BGNPP(j)]);
   end
end
fclose(f2)
figure
plot(AGNPP)
%AGNPP_annual=mean(AGNPP_annual)
%BGNPP_annual=mean(BGNPP_annual)
%NPP_annual=mean(NPP_annual)
