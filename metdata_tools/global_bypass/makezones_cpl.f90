program makezones


!Take the CLM CRU-NCEP data and aggregate by time over the spinup period (1901-1920)
!  and "chop" it up into 24 longitundinal zones

use netcdf
implicit none
include 'mpif.h'
!include 'netcdf.h'

integer ng, res
integer v, d, n, i, z, y,m,j, myid, np
character(len=5) yst, startyrst, endyrst
character(len=4) mst, dst, myidst
character(len=4) zst
character(len=1) rst
character(len=50) metvars_in, metvars, myforcing, forcdir, myres 
character(len=300) fname
character(len=200) met_prefix
real data_in(50000,1,24)
integer*2 data_zone(2920,10800)  
integer*2 temp_zone(248,10800)
real longxy(48602), latixy(48602)
real longxy_out(24,15000), latixy_out(24,15000)
integer count_zone(24), ncid_out(24)
integer starti(3), counti(3), dimid(2), starti_out, starti_out_year
integer ierr, ncid, varid, varids_out(24,10), ndaysm(12)
integer mask(48602), startyear, endyear
double precision dtime(2920)
real add_offsets(14), scale_factors(14), data_ranges(14,2)
data ndaysm /31,28,31,30,31,30,31,31,30,31,30,31/

ng=62482

call MPI_init(ierr)
call MPI_Comm_rank(MPI_COMM_WORLD, myid, ierr)
call MPI_Comm_size(MPI_COMM_WORLD, np, ierr)

data_ranges(1,1) =-0.04
data_ranges(1,2) = 0.04   !rainc
data_ranges(2,1) =-0.04
data_ranges(2,2) = 0.04   !rainl
data_ranges(3,1) =-0.04
data_ranges(3,2) = 0.04   !snowc
data_ranges(4,1) =-0.04
data_ranges(4,2) = 0.04   !snowl

data_ranges(5,1) = -20.
data_ranges(5,2) = 2000.  !swndr
data_ranges(6,1) = -20.
data_ranges(6,2) = 2000.  !swvdr
data_ranges(7,1) = -20.
data_ranges(7,2) = 2000.  !swndf
data_ranges(8,1) = -20.
data_ranges(8,2) = 2000.  !swvdf

data_ranges(9,1) = 175.
data_ranges(9,2) = 350.   !TBOT
data_ranges(10,1) = 0.
data_ranges(10,2) = 0.10   !QBOT
data_ranges(11,1) = 0.
data_ranges(11,2) = 1000.  !FLDS
data_ranges(12,1) = 20000.
data_ranges(12,2) = 120000.  !PBOT
data_ranges(13,1) = -1.
data_ranges(13,2) = 100.     !WIND u
data_ranges(14,1) = -1.
data_ranges(14,2) = 100.     !WIND v

do v=1,14
   add_offsets(v) = (data_ranges(v,2)+data_ranges(v,1))/2.
   scale_factors(v) = (data_ranges(v,2)-data_ranges(v,1))*1.1/2**15
end do

mask(:)=0
write(myidst, '(I4)') myid*3
call system('sleep ' // myidst)
if (myid .eq. 0) open(unit=8, file='zone_mappings.txt')
do v=myid+1,14,np
 do z=1,24
   if (v .eq. 1) metvars_in='a2x3h_Faxa_rainc'
   if (v .eq. 2) metvars_in='a2x3h_Faxa_rainl'
   if (v .eq. 3) metvars_in='a2x3h_Faxa_snowc'
   if (v .eq. 4) metvars_in='a2x3h_Faxa_snowl'
   if (v .eq. 5) metvars_in='a2x3h_Faxa_swndr'
   if (v .eq. 6) metvars_in='a2x3h_Faxa_swvdr'
   if (v .eq. 7) metvars_in='a2x3h_Faxa_swndf'
   if (v .eq. 8) metvars_in='a2x3h_Faxa_swvdf'
   if (v .eq. 9) metvars_in='a2x3h_Sa_tbot'
   if (v .eq. 10) metvars_in='a2x3h_Sa_shum'  
   if (v .eq. 11) metvars_in='a2x3h_Faxa_lwdn'
   if (v .eq. 12) metvars_in='a2x3h_Sa_pbot'
   if (v .eq. 13) metvars_in='a2x3h_Sa_u'
   if (v .eq. 14) metvars_in='a2x3h_Sa_v'
   if (v .eq. 1) metvars='RAINC'
   if (v .eq. 2) metvars='RAINL'
   if (v .eq. 3) metvars='SNOWC'
   if (v .eq. 4) metvars='SNOWL'
   if (v .eq. 5) metvars='SWNDR'
   if (v .eq. 6) metvars='SWVDR'
   if (v .eq. 7) metvars='SWNDF'
   if (v .eq. 8) metvars='SWVDF'
   if (v .eq. 9) metvars='TBOT'
   if (v .eq. 10) metvars='QBOT'
   if (v .eq. 11) metvars='FLDS'
   if (v .eq. 12) metvars='PSRF'
   if (v .eq. 13) metvars='U'
   if (v .eq. 14) metvars='V'
   !forcdir = '/lustre/atlas/proj-shared/cli106/5v1/Forcings'
   !forcdir = './hist'
   forcdir = '/scratch2/scratchdirs/shix/E3SM_simulations/20180719_BGCEXP_BCRC_CNPRDCTC_1850SPINUP.ne30_oECv3.edison/archive/20180719_BGCEXP_BCRC_CNPRDCTC_1850SPINUP.ne30_oECv3.edison/cpl/hist'
   myforcing = 'WCYCL1850S.ne30'
   startyear = 0576
   endyear   = 0600
   res       = 3

   write(rst,'(I1)') res
   myres = trim(rst) // 'Hrly'
  
 !!  met_prefix = trim(forcdir) // '/' // &
  !     '20171011.beta2_FCT2_branch.A_WCYCL1850S.ne30_oECv3_ICG.edison.cpl.ha2x3h.' 
!  met_prefix = trim(forcdir) // '/' // &
!         '20171122.beta3rc10_1850.ne30_oECv3_ICG.edison.cpl.ha2x3h.'
   met_prefix = trim(forcdir) // '/' // &
          '20180719_BGCEXP_BCRC_CNPRDCTC_1850SPINUP.ne30_oECv3.edison.cpl.ha2x3h.'
  
   data_in(:,:,:)=1e36
   write(startyrst,'(I5)') 10000+startyear
   write(endyrst,'(I5)') 10000+endyear
   !z = mod(myid,24)+1
   starti_out = 1
   fname = './run/20171011.beta2_FCT2_branch.A_WCYCL1850S.ne30_oECv3_ICG.edison.clm2.h0.0055-02.nc'
   ierr = nf90_open(trim(fname), NF90_NOWRITE, ncid)
   print*, trim(fname), ierr, v
   ierr = nf90_inq_varid(ncid, 'lon', varid)
   ierr = nf90_get_var(ncid, varid, longxy)
   ierr = nf90_inq_varid(ncid, 'lat', varid)
   ierr = nf90_get_var(ncid, varid, latixy)

   do y=startyear,endyear
      starti_out_year = 1
      do m=1,12
       do d=1,ndaysm(m)
         write(mst,'(I4)') 1000+m
         print*, trim(metvars), y, m
         count_zone(:)=0
         write(yst,'(I5)') 10000+y
         write(dst,'(I4)') 1000+d
         fname = trim(met_prefix) // yst(2:5) // '-' // mst(3:4) // '-' // &
              dst(3:4) // '.nc'
         ierr = nf90_open(trim(fname), NF90_NOWRITE, ncid)
         print*, trim(fname), ierr, v
         ierr = nf90_inq_varid(ncid, trim(metvars_in), varid)
         starti(1:3)  = 1
         counti(1)  = 48602
         counti(2)  = 1
         counti(3)  = 24/res
   
         ierr = nf90_get_var(ncid, varid, data_in(1:counti(1),1:counti(2),1:counti(3)), starti, counti)
         print*, 'READ', ierr
         ierr = nf90_close(ncid)
         do i=1,48602
               if (data_in(i,1,1) .le. 1e9) mask(i)=1
               if (mask(i) == 1) then 
                  if (longxy(i) .ge. (z-1)*30 .and. longxy(i) .lt. z*30) then 
                     count_zone(z)=count_zone(z)+1
                     if (y .eq. startyear .and. m .eq. 1 .and. d .eq. 1 .and. myid .eq. 0) then 
                          write(8,'(2(f10.3,1x),2(I5,1x))') longxy(i), latixy(i), &
                               z, count_zone(z)
                     end if
                     longxy_out(z, count_zone(z)) = longxy(i)
                     latixy_out(z, count_zone(z)) = latixy(i)
                  end if
                  temp_zone(1:(24/res),count_zone(z)) = &
                       nint((data_in(i,1,1:(24/res))-add_offsets(v))/scale_factors(v))
               end if
         end do
         print*, 'ZONE', z, count_zone(z)
         if (y .eq. startyear .and. m .eq. 1 .and. d .eq. 1 .and. myid .eq. 0 .and. z .eq. 24) close(8)  
         
         
         !do z=mod(myid,24)+1,24,np
            write(zst,'(I4)') 1000+z
            if (y .eq. startyear .and. m .eq. 1 .and. d .eq. 1) then 
               fname = '/lustre/atlas/proj-shared/cli106/zdr/forcing/' // trim(myforcing) &
                      // '_' // trim(metvars) // '_' // startyrst(2:5) // '-' // endyrst(2:5) // '_z' // &
                    zst(3:4) // '.nc'
               ierr = nf90_create(trim(fname),cmode=or(nf90_clobber,nf90_64bit_offset),ncid=ncid_out(z))
               ierr = nf90_def_dim(ncid_out(z), 'n', count_zone(z), dimid(2))
               ierr = nf90_def_dim(ncid_out(z), 'DTIME', (endyear-startyear+1)*(8760/res), dimid(1)) 
               ierr = nf90_def_var(ncid_out(z), 'DTIME', NF90_DOUBLE, dimid(1), &
                    varids_out(z,1))
               ierr = nf90_put_att(ncid_out(z), varids_out(z,1), 'long_name', &
                    'Day of Year')
               ierr = nf90_put_att(ncid_out(z), varids_out(z,1), 'units', &
                    'Days since ' // startyrst // '-01-01 00:00')
               ierr = nf90_def_var(ncid_out(z), 'LONGXY', NF90_FLOAT, dimid(2), &
                    varids_out(z,2))
               ierr = nf90_def_var(ncid_out(z), 'LATIXY', NF90_FLOAT, dimid(2), &
                    varids_out(z,3))
               ierr = nf90_def_var(ncid_out(z), trim(metvars), NF90_SHORT, &
                    dimid(1:2), varids_out(z,4))
               ierr = nf90_put_att(ncid_out(z), varids_out(z,4), 'add_offset', &
                    add_offsets(v))
               ierr = nf90_put_att(ncid_out(z), varids_out(z,4), 'scale_factor', &
                    scale_factors(v))
               ierr = nf90_enddef(ncid_out(z))
               ierr = nf90_put_var(ncid_out(z), varids_out(z,2), &
                    longxy_out(z, 1:count_zone(z)))
               ierr = nf90_put_var(ncid_out(z), varids_out(z,3), &
                    latixy_out(z, 1:count_zone(z)))
            end if
            do i=1,(24/res)
               dtime(i) = (starti_out+i-1)/(24/res*1.0)-(res/24)*0.5
            end do
            starti(1) = starti_out
            counti(1) = (24/res)
            ierr = nf90_put_var(ncid_out(z), varids_out(z,1), &
                 dtime(1:counti(1)), starti(1:1), counti(1:1))
            starti(2) = 1
            counti(2) = count_zone(z)

            data_zone(starti_out_year:(starti_out_year+counti(1)-1),starti(2):(starti(2) &
                 +counti(2)-1)) = temp_zone(1:counti(1),1:counti(2))
            !ierr = nf90_put_var(ncid_out(z), varids_out(z,4), &
            !     temp_zone(1:counti(1), 1:count_zone(z)), starti(1:2), counti(1:2))
            !print*,'WRITEVAR', ierr
         !end do  !Zone loop
         starti_out_year = starti_out_year+(24/res)
         starti_out = starti_out+(24/res)
         !print*, starti_out
       end do  !day loop
      end do    !month loop
      starti(1) = (y-startyear)*(8760/res)+1
      starti(2) = 1
      counti(1) = 8760/res
      counti(2) = count_zone(z)
      print*, y, z, v, starti(1:2)
      !print*, z, counti(1:2)
      ierr = nf90_put_var(ncid_out(z), varids_out(z,4), &
                   data_zone(1:counti(1), 1:counti(2)), starti(1:2), counti(1:2))
   end do       !year loop
   ierr = nf90_close(ncid_out(z))
 end do  !zone loop
end do   !Variable loop
call MPI_Finalize(ierr)

end program makezones
