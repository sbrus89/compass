from compass.model import run_model
from compass.step import Step


class Forward(Step):
    """
    A step for performing forward MPAS-Ocean runs as part of parabolic bowl
    test cases.
    """
    def __init__(self, test_case, resolution, name,
                 coord_type='sigma'):
        """
        Create a new test case

        Parameters
        ----------
        test_case : compass.TestCase
            The test case this step belongs to

        resolution : float
            The resolution of the test case

        name : str
            the name of the test case

        subdir : str, optional
            the subdirectory for the step.  The default is ``name``

        coord_type : str, optional
            vertical coordinate configuration
        """

        self.resolution = resolution

        super().__init__(test_case=test_case, name=name)

        self.add_namelist_file('compass.ocean.tests.parabolic_bowl',
                               'namelist.forward')

        res_name = f'{resolution}km'
        self.add_namelist_file('compass.ocean.tests.parabolic_bowl',
                               f'namelist.{res_name}.forward')
        self.add_namelist_file('compass.ocean.tests.parabolic_bowl',
                               f'namelist.{coord_type}.forward')

        self.add_streams_file('compass.ocean.tests.parabolic_bowl',
                              'streams.forward')

        input_path = f'../initial_state_{res_name}'
        self.add_input_file(filename='mesh.nc',
                            target=f'{input_path}/culled_mesh.nc')

        self.add_input_file(filename='init.nc',
                            target=f'{input_path}/ocean.nc')

        self.add_input_file(filename='graph.info',
                            target=f'{input_path}/culled_graph.info')

        self.add_model_as_input()

        #self.add_output_file(filename='output.nc')

    def setup(self):
        """
        Set up the test case in the work directory, including downloading any
        dependencies
        """
        self._get_resources()

    def constrain_resources(self, available_cores):
        """
        Update resources at runtime from config options
        """
        self._get_resources()
        super().constrain_resources(available_cores)

    def run(self):
        """
        Run this step of the testcase
        """
        run_model(self)

    def _get_resources(self):
        # get the these properties from the config options
        config = self.config
        self.ntasks = config.getint('parabolic_bowl',
                                    f'{self.resolution}km_ntasks')
        self.min_tasks = config.getint('parabolic_bowl',
                                       f'{self.resolution}km_min_tasks')
        self.openmp_threads = 1