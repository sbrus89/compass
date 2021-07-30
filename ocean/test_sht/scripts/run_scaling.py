#!/usr/bin/env python

# This script was generated from setup_testcases.py as part of a config file

import sys
import os
import shutil
import glob
import subprocess
import setup_sal


dev_null = open('/dev/null', 'w')

cores = ['36','72','144','288','576','1080']
nLat = ['128','256','512','1024']
nOrder = ['150','100','75','50']

parallel = False

for p in range(2):

  parallel = not parallel

  if parallel:
    N = nOrder
  else:
    N = nLat
  
  for n in N:
  
    setup_sal.setup_sal(n,parallel)
  
    for np in cores:
      
      # Run command is:
      # gpmetis graph.info 36
      subprocess.check_call(['gpmetis', 'graph.info', np])
      print("\n")
      print("     *****************************")
      print("     ** Starting model run step **")
      print("     *****************************")
      print("\n")
      os.environ['OMP_NUM_THREADS'] = '1'
      
      # Run command is:
      # srun -n 1 ./ocean_model -n namelist.ocean -s streams.ocean
      subprocess.check_call(['srun', '-n', np, './ocean_model', '-n',
                             'namelist.ocean', '-s', 'streams.ocean'])
      print("\n")
      print("     *****************************")
      print("     ** Finished model run step **")
      print("     *****************************")
      print("\n")
   
      if parallel: 
        subprocess.check_call(['mv', 'log.ocean.0000.out', 'log.ocean.0000.out_nLat_'+n+'_nCores_'+np])
      else:
        subprocess.check_call(['mv', 'log.ocean.0000.out', 'log.ocean.0000.out_N_'+n+'_nCores_'+np])
