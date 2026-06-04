import os

from compass.ocean.tests.hurricane.configure import configure_hurricane
from compass.ocean.tests.hurricane.init_storm.create_pointstats_file import (
    CreatePointstatsFile,
)
from compass.ocean.tests.hurricane.init_storm.interpolate_atm_forcing import (
    InterpolateAtmForcing,
)
from compass.testcase import TestCase


class InitStorm(TestCase):
    """
    A test case for creating initial conditions on a global MPAS-Ocean mesh

    Attributes
    ----------
    mesh : compass.ocean.tests.hurricane.mesh.Mesh
        The test case that creates the mesh used by this test case
    """
    def __init__(self, test_group, mesh, storm, use_lts):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.hurricane.Hurricane
            The hurricane test group that this test case belongs to

        mesh : compass.ocean.tests.hurricane.mesh.Mesh
            The test case that creates the mesh used by this test case

        storm : str
            The name of the storm to be run

        use_lts : bool
            Whether local time-stepping is used
        """

        if use_lts == 'LTS':
            name = f'init_{storm}_lts'
        elif use_lts == 'FB_LTS':
            name = f'init_{storm}_fblts'
        else:
            name = f'init_{storm}'
        self.mesh = mesh
        mesh_name = mesh.mesh_name
        subdir = os.path.join(mesh_name, name)
        super().__init__(test_group=test_group, name=name, subdir=subdir)

        self.add_step(InterpolateAtmForcing(test_case=self, mesh=mesh,
                                            storm=storm, use_lts=use_lts))
        self.add_step(CreatePointstatsFile(test_case=self, mesh=mesh,
                                           storm=storm, use_lts=use_lts))

    def configure(self):
        """
        Modify the configuration options for this test case
        """
        configure_hurricane(test_case=self, mesh=self.mesh)
