import subprocess
import os




def setup_sal(N,parallel=False):


  f = open('namelist.ocean','r')
  lines = f.read().splitlines()
  f.close()

  if parallel:

     for i in range(len(lines)):
       if lines[i].find('config_parallel_self_attraction_loading_order') >= 0 :
         lines[i] = '    config_parallel_self_attraction_loading_order = '+N
       if lines[i].find('config_use_parallel_self_attraction_loading') >= 0:
         lines[i] = '    config_use_parallel_self_attraction_loading = .true.'

  else:
    nLon = 2*N
    N = str(N)
    nLon = str(nLon)
    
    if not os.path.exists('mpas_mesh_scrip.nc'):
      subprocess.call('scrip_from_mpas -m mesh.nc -s mpas_mesh_scrip.nc', shell=True)
    
    if not os.path.exists('mpas_to_grid_'+N+'.nc'):
      subprocess.call("ncremap -G ttl="+N+"x"+nLon+"#latlon="+N+','+nLon+"#lat_typ=gss#lon_typ=grn_ctr -g gaussian_grid_scrip.nc", shell=True)
      subprocess.call('ESMF_RegridWeightGen -d gaussian_grid_scrip.nc -s mpas_mesh_scrip.nc -w mpas_to_grid_'+N+'.nc -i', shell=True)
      subprocess.call('ESMF_RegridWeightGen -s gaussian_grid_scrip.nc -d mpas_mesh_scrip.nc -w grid_to_mpas_'+N+'.nc -i', shell=True)
    
    subprocess.call('ln -sf mpas_to_grid_'+N+'.nc mpas_to_grid.nc', shell=True)
    subprocess.call('ln -sf grid_to_mpas_'+N+'.nc grid_to_mpas.nc', shell=True)
    

    
    for i in range(len(lines)):
      if lines[i].find('config_Nitude') >= 0 :
        lines[i] = '    config_Nitude = '+N
      if lines[i].find('config_nLongitude') >= 0 :
        lines[i] = '    config_nLongitude = '+nLon
      if lines[i].find('config_use_parallel_self_attraction_loading') >= 0:
        lines[i] = '    config_use_parallel_self_attraction_loading = .false.'
   
  f = open('namelist.ocean','w')
  f.write('\n'.join(lines))
  f.close()
  

if __name__ == "__main__":

  #nLat = 16
  #nLat = 32
  #nLat = 64
  nLat = 128
  #nLat = 256
  #nLat = 512
  #nLat = 1024
  #nLat = 2048
  #nLat = 2500
  #nLat = 4096 

  setup_sal(nLat)
