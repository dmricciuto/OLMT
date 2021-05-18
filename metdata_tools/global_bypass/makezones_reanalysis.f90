program makezones


!Take the CLM CRU-NCEP data and aggregate by time over the spinup period (1901-1920)
!  and "chop" it up into 24 longitundinal zones

use netcdf
implicit none
include 'mpif.h'
!include 'netcdf.h'

integer ng, res
integer v, n, i, z, y,m,j, myid, np
character(len=4) yst, startyrst, endyrst
character(len=4) mst, myidst
character(len=4) zst
character(len=1) rst
character(len=150) metvars, myforcing, forcdir, myres 
character(len=300) fname, filename_base
character(len=200) met_prefix
real data_in(30,360,124)         !248
integer*2 data_zone(1460,10800)  !2920  
integer*2 temp_zone(124,10800)   !248
real longxy(720,360), latixy(720,360)
real longxy_out(24,15000), latixy_out(24,15000)
integer count_zone(24), ncid_out(24)
integer starti(3), counti(3), dimid(2), starti_out, starti_out_year
integer ierr, ncid, varid, varids_out(24,10), ndaysm(12)
integer mask(720,360), startyear, endyear
double precision dtime(1460)    !2920
real add_offsets(7), scale_factors(7), data_ranges(7,2)
data ndaysm /31,28,31,30,31,30,31,31,30,31,30,31/

ng=62482

call MPI_init(ierr)
call MPI_Comm_rank(MPI_COMM_WORLD, myid, ierr)
call MPI_Comm_size(MPI_COMM_WORLD, np, ierr)

!Set the input data path
forcdir = '/lustre/or-hydra/cades-ccsi/proj-shared/project_acme/ACME_inputdata/atm/datm7/atm_forcing.datm7.CRUJRA.0.5d.v1.c190604'
!myforcing = 'cruncep.V8.c2017'
!Set the directory of the forcing
myforcing = 'CRUJRAV1.1.c2019.0.5x0.5'
!Set the date range and time resolution
startyear = 1901
endyear   = 2017
res       = 6      !Timestep in hours


data_ranges(1,1) =-0.04
data_ranges(1,2) = 0.04   !Precip
data_ranges(2,1) = -20.
data_ranges(2,2) = 2000.  !FSDS
data_ranges(3,1) = 175.
data_ranges(3,2) = 350.   !TBOT
data_ranges(4,1) = 0.
data_ranges(4,2) = 0.10   !QBOT
data_ranges(5,1) = 0.
data_ranges(5,2) = 1000.  !FLDS
data_ranges(6,1) = 20000.
data_ranges(6,2) = 120000.  !PBOT
data_ranges(7,1) = -1.
data_ranges(7,2) = 100.     !WIND

do v=1,7
   add_offsets(v) = (data_ranges(v,2)+data_ranges(v,1))/2.
   scale_factors(v) = (data_ranges(v,2)-data_ranges(v,1))*1.1/2**15
end do

mask(:,:)=0
!write(myidst, '(I4)') myid*3
!call system('sleep ' // myidst)
print*, 'myid', myid
if (myid .eq. 0) open(unit=8, file='zone_mappings.txt')

do v=myid+1,7,np
 print*, v
 do z=1,24
   mask(:,:)=0
   if (v .eq. 1) metvars='PRECTmms'
   if (v .eq. 2) metvars='FSDS'
   if (v .eq. 3) metvars='TBOT'
   if (v .eq. 4) metvars='QBOT'
   if (v .eq. 5) metvars='FLDS'
   if (v .eq. 6) metvars='PSRF'
   if (v .eq. 7) metvars='WIND'

   startyear = 1901
   endyear   = 2017
   res       = 6
   write(rst,'(I1)') res
   myres = trim(rst) // 'Hrly'
 
   if (v .eq. 1) met_prefix = trim(forcdir) // '/clmforc.' // trim(myforcing) // '.Prec.'
   if (v .eq. 2) met_prefix = trim(forcdir) // '/clmforc.' // trim(myforcing) // '.Solr.'
   if (v .ge. 3) met_prefix = trim(forcdir) // '/clmforc.' // trim(myforcing) // '.TPQWL.'

   !CRU-NCEP v7
   !if (v .eq. 1) met_prefix = trim(forcdir) // '/atm_forcing.datm7.' &
   !        // trim(myforcing) // '_qianFill.0.5d.V7.c160715' // '/Precip' // trim(myres) // &
   !        '/clmforc.cruncep.V7.c2016.0.5d.Prec.'
   !if (v .eq. 2) met_prefix = trim(forcdir) // '/atm_forcing.datm7.' &
   !        // trim(myforcing) // '_qianFill.0.5d.V7.c160715' // '/Solar' // &
   !        trim(myres) // '/clmforc.cruncep.V7.c2016.0.5d.Solr.'
   !if (v .ge. 3) met_prefix = trim(forcdir) // '/atm_forcing.datm7.' &
   !        // trim(myforcing) // '_qianFill.0.5d.V7.c160715' // '/TPHWL' // &
   !        trim(myres) // '/clmforc.cruncep.V7.c2016.0.5d.TPQWL.'
  

   data_in(:,:,:)=1e36
   write(startyrst,'(I4)') startyear
   write(endyrst,'(I4)') endyear
   !z = mod(myid,24)+1
   starti_out = 1

   do y=startyear,endyear
      starti_out_year = 1
      do m=1,12
         write(mst,'(I4)') 1000+m
         print*, trim(metvars), y, m
         count_zone(:)=0
         write(yst,'(I4)') y
         fname = trim(met_prefix) // yst // '-' // mst(3:4) // '.nc'
         ierr = nf90_open(trim(fname), NF90_NOWRITE, ncid)
         print*, trim(fname), ierr, v
         ierr = nf90_inq_varid(ncid, 'LONGXY', varid)
         ierr = nf90_get_var(ncid, varid, longxy)
         ierr = nf90_inq_varid(ncid, 'LATIXY', varid)
         ierr = nf90_get_var(ncid, varid, latixy)
         ierr = nf90_inq_varid(ncid, trim(metvars), varid)
         starti(1:3)  = 1
         starti(1)    = (z-1)*30+1
         counti(1)  = 30
         counti(2)  = 360
         counti(3)  = ndaysm(m)*(24/res)
   
         ierr = nf90_get_var(ncid, varid, data_in(1:counti(1),1:counti(2),1:counti(3)), starti, counti)
         print*, 'READ', ierr
         ierr = nf90_close(ncid)
         do i=1,30 !720
            do j=1,360
               if (data_in(i,j,1) .le. 1e9) mask(i,j)=1
               if (mask(i,j) == 1) then 
                  !z = (i-1)/30+1   
                  count_zone(z)=count_zone(z)+1
                  if (y .eq. startyear .and. m .eq. 1) then 
                     if (myid .eq. 0) then 
                        if (longxy((z-1)*30+i,j) .ge. 0.25) then 
                           write(8,'(2(f10.3,1x),2(I5,1x))') longxy((z-1)*30+i,j), latixy((z-1)*30+i,j), &
                                z, count_zone(z)
                        else
                           write(8,'(2(f10.3,1x),2(I5,1x))') 359.75, latixy((z-1)*30+i,j), &
                                z, count_zone(z)
                        end if
                     end if
                     longxy_out(z, count_zone(z)) = longxy((z-1)*30+i,j)
                     latixy_out(z, count_zone(z)) = latixy((z-1)*30+i,j)
                  end if
                  !print*, i,j,z, count_zone(z) 
                  temp_zone(1:ndaysm(m)*(24/res),count_zone(z)) = &
                       nint((data_in(i,j,1:ndaysm(m)*(24/res))-add_offsets(v))/scale_factors(v))
               end if
            end do
         end do
         print*, 'ZONE', z, count_zone(z)
         !if (y .eq. startyear .and. m .eq. 1 .and. myid .eq. 0) close(8)  
         
         
         !do z=mod(myid,24)+1,24,np
            write(zst,'(I4)') 1000+z
            if (y .eq. startyear .and. m .eq. 1) then 
               fname = trim(forcdir) // '/' // trim(myforcing) &
                      // '_' // trim(metvars) // '_' // startyrst // '-' // endyrst // '_z' // &
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
            do i=1,ndaysm(m)*(24/res)
               dtime(i) = (starti_out+i-1)/(24/res*1.0)-(res/24)*0.5
            end do
            starti(1) = starti_out
            counti(1) = ndaysm(m)*(24/res)
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
         starti_out_year = starti_out_year+ndaysm(m)*(24/res)
         starti_out = starti_out+ndaysm(m)*(24/res)
         !print*, starti_out
      end do    !month loop
      starti(1) = (y-startyear)*(8760/res)+1
      starti(2) = 1
      counti(1) = 8760/res
      counti(2) = count_zone(z)
      print*, y, z, v, starti(1:2)
      print*, z, counti(1:2)
      ierr = nf90_put_var(ncid_out(z), varids_out(z,4), &
                   data_zone(1:counti(1), 1:counti(2)), starti(1:2), counti(1:2))
   end do       !year loop
   ierr = nf90_close(ncid_out(z))
 end do  !zone loop
 if (myid .eq. 0) close(8)  
end do   !Variable loop
call MPI_Finalize(ierr)

end program makezones
