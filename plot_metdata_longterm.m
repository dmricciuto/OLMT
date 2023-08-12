% This script is used for reading and processing variables from ELM outputs
% Reading output variables
OUTDIR='/home/whf/scratch/';
RUNcase='NMTB391';
year=1984;
column_n=1
CaseName = strcat(RUNcase,'_US-GC4_ICB20TRCNPRDCTCBC');
%f2=fopen(strcat('./H2OSFC_NPP_',num2str(year),'_',RUNcase,'_vars_c',num2str(column_n),'.txt'),'wt');
f2=fopen(strcat('../runcase/results/',RUNcase,'MET_annual_35yr_',num2str(column_n),'.txt'),'wt')
ny=year-1987+1;
interval=86400/24;
for i=year:year+34
%for i=32:32
   FileName = strcat(OUTDIR,CaseName,'/run/',CaseName,'.elm.h0.',num2str(i),'-01-01-00000.nc')

   RAIN = ncread(FileName,'RAIN');
   TBOT   = ncread(FileName,'TBOT');
   RAIN = RAIN(column_n,:);
   TBOT   = TBOT(column_n,:);
   FillData = 1.0e+36;
   id=find(RAIN<FillData/10);
   RAIN_annual = sum(RAIN(id))*interval/8760 %yearly average
   id=find(TBOT<FillData/10);
   TBOT_annual = sum(TBOT(id))/8760 %yearly average
   fprintf(f2,'%d %10f %10f\n',[i TBOT_annual RAIN_annual]);
   %for j=1:length(H2OSFC)
   %  fprintf(f2,'%f %10f %10f\n',[j/24 H2OSFC(j) NPP(j)]);
   %end
end
fclose(f2)
%FileName = '/nfs/data/ccsi/proj-shared/E3SM/pt-e3sm-inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_us-gc03/GSWP3_daymet4_PRECTmms_1980-2014_z01.nc';
%RAIN_in=ncread(FileName,'PRECTmms');
%FileName = '/nfs/data/ccsi/proj-shared/E3SM/pt-e3sm-inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_us-gc03/GSWP3_daymet4_TBOT_1980-2014_z01.nc';
%TBOT_in=ncread(FileName,'TBOT');
%f2=fopen(strcat('../runcase/results/','GSWP3_daymet4_1980_2014','.txt'),'wt')
%for i=1:length(TBOT_in)
%    RAIN_in_annual(i,1)=sum(RAIN_in(((i-1)*365*8+1):i*365*8))*3*3600/8760;
%    TBOT_in_annual(i,1)=sum(TBOT_in(((i-1)*365*8+1):i*365*8))*3/8760;
%    fprintf(f2,'%d %10f %10f\n',[i*0.125+datenum(1980,1,1) RAIN_in(i) TBOT_in(i)]);
%end
%fclose(f2) 
%FileName = '/nfs/data/ccsi/proj-shared/E3SM/inputdata/atm/datm7/atm_forcing.datm7.GSWP3-w5e5.c/cpl_bypass_full/gswp_w5e5_PRECTmms_1901-2019_z19.nc';
%RAIN_in=ncread(FileName,'PRECTmms');
%RAIN_in=RAIN_in(:,9618);
%FileName = '/nfs/data/ccsi/proj-shared/E3SM/inputdata/atm/datm7/atm_forcing.datm7.GSWP3-w5e5.c/cpl_bypass_full/gswp_w5e5_TBOT_1901-2019_z19.nc';
%TBOT_in=ncread(FileName,'TBOT');
%TBOT_in=TBOT_in(:,9618);
%f2=fopen(strcat('../runcase/results/','GSWP3_w5e5_1901_2019','.txt'),'wt')
%for i=1:length(TBOT_in)
%    RAIN_in_annual(i,1)=sum(RAIN_in(((i-1)*365*4+1):i*365*4))*8*3600/8760;
%    TBOT_in_annual(i,1)=sum(TBOT_in(((i-1)*365*4+1):i*365*4))*6/8760;
%    fprintf(f2,'%d %10f %10f\n',[i*0.25+datenum(1901,1,1) RAIN_in(i) TBOT_in(i)]);
%end
%fclose(f2)
%FileName = '/nfs/data/ccsi/proj-shared/E3SM/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716/cpl_bypass_full/GSWP3_PRECTmms_1901-2014_z19.nc';
%RAIN_in=ncread(FileName,'PRECTmms');
%RAIN_in=RAIN_in(:,9618);
%FileName = '/nfs/data/ccsi/proj-shared/E3SM/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v2.c180716/cpl_bypass_full/GSWP3_TBOT_1901-2014_z19.nc';
%TBOT_in=ncread(FileName,'TBOT');
%TBOT_in=TBOT_in(:,9618);
%f2=fopen(strcat('../runcase/results/','GSWP3_1901_2014','.txt'),'wt')
%for i=1:length(TBOT_in)
%    RAIN_in_annual(i,1)=sum(RAIN_in(((i-1)*365*4+1):i*365*4))*8*3600/8760;
%    TBOT_in_annual(i,1)=sum(TBOT_in(((i-1)*365*4+1):i*365*4))*6/8760;
%    fprintf(f2,'%d %10f %10f\n',[i*0.125+datenum(1901,1,1) RAIN_in(i) TBOT_in(i)]);
%end
%fclose(f2)

