import json
from importlib import resources

import mpas_tools.ocean.coastal_tools as ct
import numpy as np
from scipy import interpolate

from compass.ocean.mesh.floodplain import FloodplainMeshStep
from compass.ocean.tests.hurricane.mesh.devr45to5rr1.medial_axis import (
    average_close_points,
    extract_longest_centerline_per_label,
    generate_offset_points_variable,
    plot_linestrings,
    write_init_jigsaw_file,
)
from compass.ocean.tests.tides.mesh.vr45to5 import VRTidesMesh


class DEVR45to5rr1BaseMesh(VRTidesMesh, FloodplainMeshStep):

    def __init__(self, test_case, pixel, name='base_mesh', subdir=None,
                 elev_file='RTopo_2_0_4_GEBCO_v2023_30sec_pixel.nc',
                 spac_dhdx=0.1, spac_hmin=10.0, spac_hmax=75.0, spac_hbar=60.0,
                 ncell_nwav=60, ncell_nslp=0,
                 filt_sdev=3.0, filt_halo=50, filt_plev=0.325):

        VRTidesMesh.__init__(self, test_case, pixel, name, subdir,
                                                 elev_file,
                                                 spac_dhdx, spac_hmin, spac_hmax, spac_hbar,
                                                 ncell_nwav, ncell_nslp,
                                                 filt_sdev, filt_halo, filt_plev)
        FloodplainMeshStep.__init__(self, test_case, name, subdir)

        self.add_input_file(filename='crm_vol1_2023_nc3.nc',
                            target='crm_vol1_2023_nc3.nc',
                            database='bathymetry_database')

        self.add_input_file(filename='crm_vol2_2023_nc3.nc',
                            target='crm_vol2_2023_nc3.nc',
                            database='bathymetry_database')

    def setup(self):

        package = self.__module__
        filename = 'map.geojson'
        with resources.open_text(package, filename) as geojson_file:
            self.geojson_features = json.load(geojson_file)['features']
        super().setup()

    """
    A step for creating DEQU120at30cr10rr2 meshes
    """
    def region_multiplier(self, xgrid):
        """
        Create cell width array for this mesh on a regular latitude-longitude
        grid

        Returns
        -------
        cellWidth : numpy.array
            m x n array of cell width in km

        lon : numpy.array
            longitude in degrees (length n and between -180 and 180)

        lat : numpy.array
            longitude in degrees (length m and between -90 and 90)
        """
        km = 1000.0

        params = ct.default_params
        params['ddeg'] = xgrid[1] - xgrid[0]

        # QU 120 background mesh and enhanced Atlantic (30km)
        params["mesh_type"] = "QU"
        params["dx_max_global"] = 1.0
        params["region_box"] = ct.Atlantic
        params["restrict_box"] = ct.Atlantic_restrict
        params["plot_box"] = ct.Western_Atlantic
        params["dx_min_coastal"] = .99
        params["trans_width"] = 5000.0 * km
        params["trans_start"] = 500.0 * km

        cell_width, lon, lat = ct.coastal_refined_mesh(params)

        # Northeast refinement (10km)
        params["region_box"] = ct.Delaware_Bay
        params["plot_box"] = ct.Western_Atlantic
        params["dx_min_coastal"] = 0.5
        params["trans_width"] = 600.0 * km
        params["trans_start"] = 400.0 * km

        cell_width, lon, lat = ct.coastal_refined_mesh(
            params, cell_width, lon, lat)

        # Delaware regional refinement (6km)
        params["region_box"] = ct.Delaware_Region
        params["plot_box"] = ct.Delaware
        params["dx_min_coastal"] = 0.25
        params["trans_width"] = 175.0 * km
        params["trans_start"] = 75.0 * km

        cell_width, lon, lat = ct.coastal_refined_mesh(
            params, cell_width, lon, lat)

        # Delaware Bay high-resolution (2km)
        Delaware_restrict = {"include": [np.array([[-75.853, 39.732],
                                                   [-74.939, 36.678],
                                                   [-71.519, 40.156],
                                                   [-74.784, 40.296]]),
                                         np.array([[-76.024, 37.188],
                                                   [-75.214, 36.756],
                                                   [-74.512, 37.925],
                                                   [-75.274, 38.318]])],
                             "exclude": []}
        params["region_box"] = ct.Delaware_Bay
        params["plot_box"] = ct.Delaware
        params["restrict_box"] = Delaware_restrict
        params["dx_min_coastal"] = 0.125
        params["trans_width"] = 100.0 * km
        params["trans_start"] = 17.0 * km

        cell_width, lon, lat = ct.coastal_refined_mesh(
            params, cell_width, lon, lat)

        return cell_width, lon, lat


    def build_cell_width_lat_lon(self):

        km = 1000.0

        cell_width, xgrid, ygrid = super().build_cell_width_lat_lon()
        print(cell_width.shape)

        multiplier, lon, lat = self.region_multiplier(xgrid)
        print(multiplier.shape)

        cell_width = np.multiply(multiplier, cell_width)

        variable_name = 'z'
        threshold = 0  # Adjust threshold based on your data
        xvar = 'lon'
        yvar = 'lat'
        nc_files = ['crm_vol1_2023_nc3.nc','crm_vol2_2023_nc3.nc']
        #nc_files = ['crm_vol1_2023_nc3.nc']
        geojson_file = 'map.geojson'
        tol_frac = 0.5

        self.opts.init_file = 'init.msh'

        spacing = interpolate.RegularGridInterpolator((lon, lat), np.sqrt(3.0) * cell_width.T)

        points_combined = []
        for nc_file in nc_files:
            centerlines, mask, X, Y = extract_longest_centerline_per_label(
                nc_file, self.geojson_features, topo_var=variable_name,
                threshold=threshold, x_var=xvar, y_var=yvar
            )
            print("X")
            print(X.shape)
            print("mask")
            print(mask.shape)
            print("n cetnerlines")
            print(len(centerlines))

            points = generate_offset_points_variable(centerlines, spacing)
            print("points")
            print(points.shape)
            points_avg = average_close_points(points, spacing, tol_frac)
            print("points_avg")
            print(points_avg.shape)
            points_combined.append(points_avg)
            plot_linestrings(centerlines, mask, X, Y, points, points_avg)
        points_combined = np.concatenate(points_combined)
        print(points_combined.shape)
        write_init_jigsaw_file(points_combined, 'init.msh')

        return cell_width, lon, lat
