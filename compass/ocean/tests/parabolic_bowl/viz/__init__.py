import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import subprocess
from scipy.interpolate import LinearNDInterpolator

from compass.step import Step


class Viz(Step):
    """
    A step for visualizing parabolic bowl results and
    comparing with analytical solution

    Attributes
    ----------
    """
    def __init__(self, test_case, resolutions):
        """
        Create the step

        Parameters
        ----------
        test_case : compass.TestCase
            The test case this step belongs to
        """
        super().__init__(test_case=test_case, name='viz')

        self.resolutions = resolutions

        for res in resolutions:
            self.add_input_file(filename=f'output_{res}km.nc',
                                target=f'../forward_{res}km/output.nc')

    def run(self):
        """
        Run this step of the test case
        """

        # Pointwise timeseries plots 
        points = self.config.get('parabolic_bowl_viz', 'points')
        points = points.replace('[','').replace(']','').split(',')
        points = np.asarray(points, dtype=float).reshape(-1, 2)
        points = points*1000

        fig, ax = plt.subplots(nrows=len(points),ncols=1)

        for res in self.resolutions:
            ds = xr.open_dataset(f'output_{res}km.nc')

            time = [dt.datetime.strptime(x.decode(),'%Y-%m-%d_%H:%M:%S') for x in ds.xtime.values]
            t = np.asarray([(x-time[0]).total_seconds() for x in time])
            

            xy = np.vstack((ds.xCell.values, ds.yCell.values)).T
            interp = LinearNDInterpolator(xy, ds.ssh.values.T)
            
            for i, pt in enumerate(points):

                ssh = interp(pt).T
                ax[i].plot(t/86400, ssh, label=f'{res}km')

        for i, pt in enumerate(points):
            ssh_exact = self.exact_solution('zeta', pt[0], pt[1], t)
            ax[i].plot(t/86400,ssh_exact, label='exact')

        for i, pt in enumerate(points):
            ax[i].set_xlabel('t (days)')
            ax[i].set_ylabel('ssh (m)')
            ax[i].set_title(f'Point ({pt[0]/1000}, {pt[1]/1000})')
            if i == len(points)-1:
              lines, labels = ax[i].get_legend_handles_labels()
          
        fig.tight_layout()
        fig.legend(lines, labels, loc='lower center',ncol=4)
        fig.savefig(f'points.png')#, bbox_inches='tight')

        # RMSE plots
        comparisons = self.config.get('parabolic_bowl_viz', 'error_compare')
        comparisons = comparisons.replace('[','').replace(']','').replace(' ','').split(',')
        comparisons.insert(0,'.')
        #comparisons.insert(0,self.test_case.name)
        comparisons.insert(0,'subgrid_ramp')
        comparisons = np.asarray(comparisons, dtype=object).reshape(-1, 2)

        fig, ax = plt.subplots(nrows=1,ncols=1)

        max_rmse = 0
        for j, comp in enumerate(comparisons):
            rmse = np.zeros(len(self.resolutions))
            for i, res in enumerate(self.resolutions):

                rmse[i] = self.compute_rmse(f'{comp[1]}/output_{res}km.nc')
                if rmse[i] > max_rmse:
                    max_rmse = rmse[i]

            ax.loglog(self.resolutions, rmse, linestyle='-', marker='o', label=comp[0])


        rmse_1st_order = np.zeros(len(self.resolutions))
        rmse_1st_order[0] = max_rmse
        for i in range(len(self.resolutions)-1):
          rmse_1st_order[i+1] = rmse_1st_order[i]/2.0

        ax.loglog(self.resolutions, np.flip(rmse_1st_order), linestyle='-', color='k', alpha=.25, label='1st order')

        ax.set_xlabel('Cell size (km)')
        ax.set_ylabel('RMSE (m)')
           
        ax.legend(loc='lower right') 
        fig.tight_layout()
        fig.savefig(f'error.png')

    def compute_rmse(self, filename):

        ds = xr.open_dataset(filename)

        time = [dt.datetime.strptime(x.decode(),'%Y-%m-%d_%H:%M:%S') for x in ds.xtime.values]
        ind = time.index(dt.datetime.strptime('0001-01-03_18:00:00', '%Y-%m-%d_%H:%M:%S'))

        ssh = ds.ssh.values[ind,:]
        t = (time[ind]-time[0]).total_seconds()
        ssh_exact = self.exact_solution('zeta', ds.xCell.values, ds.yCell.values, t)
        rmse = np.sqrt(np.mean(np.square(ssh-ssh_exact)))

        return rmse

    def exact_solution(self, var, x, y, t):

        config = self.config

        f = config.getfloat('parabolic_bowl', 'coriolis_parameter')
        eta0 = config.getfloat('parabolic_bowl', 'eta_max')
        b0 = config.getfloat('parabolic_bowl', 'depth_max')
        omega = config.getfloat('parabolic_bowl', 'omega')
        g = config.getfloat('parabolic_bowl', 'gravity')

        x = np.array(x)
        y = np.array(y)
        t = np.array(t)

        x = np.atleast_1d(x)
        y = np.atleast_1d(y)
        t = np.atleast_1d(t)
       
        if t.size > 1:
            x = np.resize(x, t.shape)
            y = np.resize(y, t.shape)

# paraminit.val = (paraminit.h0 + paraminit.zeta0)^2 ;
# paraminit.CC = (paraminit.val - paraminit.h0^2.0)/(paraminit.val + paraminit.h0^2.0) ;
# paraminit.Lb =  sqrt(8.0*paraminit.gg*paraminit.h0/ ... 
#    (paraminit.omeg0*paraminit.omeg0 - paraminit.ff*paraminit.ff)) ;
# L2 = Lb*Lb ;
# r2 = xx.*xx + yy.*yy ;
# num = 1 - CC*CC ;
# den = 1.0/(1.0 - CC*cos(omeg0*t)) ;
# hh0 = h0*( den*sqrt(num) - den*den*(r2/L2)*num ) ; 
# hh0( hh0 < eps_dry ) = 0 ; 

# invL = (1.0)/(param.Lb*param.Lb) ;
# r2 = x.*x + y.*y ;
# bxy = param.h0*(1.0 - invL*r2) ;

        eps = 1.0e-12
        r = np.sqrt(np.square(x) + np.square(y))
        L = np.sqrt(8.0*g*b0/(omega**2 - f**2))
        C = ((b0 + eta0)**2 - b0**2)/((b0 + eta0)**2 + b0**2)
        b = b0*(1.0 - r**2/L**2)
        num = 1.0 - C**2
        den = 1.0/(1.0 - C*np.cos(omega*t))
        h = b0*(den*np.sqrt(num) - den**2*(r**2/L**2)*num)
        h[h<eps] = 0.0 

        if var == 'h':
#         soln = hh0 ;
            soln = h

        elif var == 'zeta':
#         soln = h0*( den*sqrt(num) - ... 
#             1.0 - (r2/L2)*(den*den*num - 1.0) ) ; 
#     
#         idx = find( hh0 < eps_dry ) ; 
#         if ( ~isempty(idx) )
#             soln(idx) = -bxy(idx) ; 
#         end 
            soln = b0*(den*np.sqrt(num) - 1.0 - (r**2/L**2)*(den**2*num - 1.0))
            soln[h<eps] = -b[h<eps]

        elif var == 'u':
#         soln = 0.5*den*( omeg0*xx*CC*sin(omeg0*t) - ff*yy*(sqrt(num) ... 
#             + CC*cos(omeg0*t) - 1.0) ) ; 
#     
#         soln( hh0 < eps_dry ) = 0 ; 
            soln = 0.5*den*(omega*x*C*np.sin(omega*t) - f*y*(np.sqrt(num) + C*np.cos(omega*t) - 1.0))
            soln[h<eps] = 0

        elif var == 'v':
#         soln = 0.5*den*( omeg0*yy*CC*sin(omeg0*t) + ff*xx*(sqrt(num) ... 
#             + CC*cos(omeg0*t) - 1.0) ) ; 
#     
#         soln( hh0 < eps_dry ) = 0 ; 
            soln = 0.5*den*(omega*y*C*np.sin(omega*t) + f*x*(np.sqrt(num) + C*np.cos(omega*t) - 1.0))
            soln[h<eps] = 0

        elif var == 'r':
#         soln = Lb*sqrt( (1 - CC*cos( omeg0*t))/sqrt(1 - CC*CC) ) ; 
            soln = L*np.sqrt((1.0 - C*np.cos(omega*t))/np.sqrt(1.0 - C**2))

        else:
            print('Variable name not supported')

        return soln
