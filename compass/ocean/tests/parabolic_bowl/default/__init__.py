from compass.testcase import TestCase
from compass.ocean.tests.parabolic_bowl.initial_state import InitialState
from compass.ocean.tests.parabolic_bowl.forward import Forward
from compass.ocean.tests.parabolic_bowl.viz import Viz
from compass.validate import compare_variables


class Default(TestCase):
    """
    The default parabolic_bowl test case

    Attributes
    ----------
    resolution : float
        The resolution of the test case in km

    coord_type : str
        The type of vertical coordinate (``sigma``, ``single_layer``, etc.)
    """

    def __init__(self, test_group, resolution, coord_type):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.parabolic_bowl.ParabolicBowl
            The test group that this test case belongs to

        resolution : float
            The resolution of the test case in km

        coord_type : str
            The type of vertical coordinate (``sigma``, ``single_layer``)
        """
        name = 'default'

        self.resolution = resolution
        self.coord_type = coord_type

        if resolution < 1.:
            res_name = f'{int(resolution*1e3)}m'
        else:
            res_name = f'{int(resolution)}km'
        subdir = f'{res_name}/{coord_type}/{name}'
        super().__init__(test_group=test_group, name=name,
                         subdir=subdir)

        self.add_step(InitialState(test_case=self, coord_type=coord_type))
        self.add_step(Forward(test_case=self, resolution=resolution,
                              coord_type=coord_type))
        #self.add_step(Viz(test_case=self))

    def configure(self):
        """
        Modify the configuration options for this test case.
        """

        resolution = self.resolution
        config = self.config

        Lx = config.getint('parabolic_bowl','Lx')
        Ly = config.getint('parabolic_bowl','Ly')

        nx = round(Lx / resolution)
        ny = round(Ly / resolution)
        dc = 1e3 * resolution

        config.set('parabolic_bowl', 'nx', f'{nx}', comment='the number of '
                   'mesh cells in the x direction')
        config.set('parabolic_bowl', 'ny', f'{ny}', comment='the number of '
                   'mesh cells in the y direction')
        config.set('parabolic_bowl', 'dc', f'{dc}', comment='the distance '
                   'between adjacent cell centers')

    def validate(self):
        """
        Validate variables against a baseline
        """
        variables = ['layerThickness', 'normalVelocity']
        compare_variables(test_case=self, variables=variables,
                          filename1='forward/output.nc')
