% This script is used for reading and processing variables from ELM outputs
% Reading output variables
% And write time series to a txt file
OUTDIR='/home/whf/scratch/';%this is the path to yout output file on CADES
RUNcase='NMTB39d';
year=2018;%the year you want to look at
column_n=1;%1st column is high marsh, 2nd column is low marsh
CaseName = strcat(RUNcase,'_US-GC4_ICB20TRCNPRDCTCBC');
%below is the name of the output file with variable you want
%f2=fopen(strcat('./H2OSFC_newNPP_',num2str(year),'_',RUNcase,'_vars_c',num2str(column_n),'.txt'),'wt');
%f2=fopen(strcat(RUNcase,'NPP_annual_35yr_',num2str(column_n),'.txt'),'wt')
ny=year-1987+1;
interval=86400;%output time interval, here is 1 hour, change it to 86400 is you have daily data
for i=1998:2003 % you can edit the loop if you want multiple years
%for i=32:32
   FileName = strcat(OUTDIR,CaseName,'/run/',CaseName,'.elm.h0.',num2str(i),'-01-01-00000.nc')

   AGNPP = ncread(FileName,'AGNPP');
   NPP   = ncread(FileName,'NPP');
   AGNPP = AGNPP(column_n,:);
   NPP   = NPP(column_n,:);
   BGNPP = ncread(FileName,'BGNPP');
   BGNPP = BGNPP(column_n,:);
   H2OSFC=ncread(FileName,'H2OSFC');
   H2OSFC=H2OSFC(column_n,:)/1000;
   FillData = 1.0e+36;
   %below lines are to remove NaN values
   id=find(AGNPP<FillData/10);
   AGNPP_annual = sum(AGNPP(id))*interval
   id=find(NPP<FillData/10);
   NPP_annual   = sum(NPP(id))*interval
   id=find(BGNPP<FillData/10);
   BGNPP_annual = sum(BGNPP(id))*interval
   f2=fopen(strcat('./H2OSFC_newNPP_',num2str(i),'_',RUNcase,'_vars_c',num2str(column_n),'.txt'),'wt');
   for j=1:length(H2OSFC)
     fprintf(f2,'%f %10f\n',[j AGNPP(j)+BGNPP(j)]);%write two columns first column is in hours, 2nd column is the total NPP
   end
   fclose(f2)
end
figure
