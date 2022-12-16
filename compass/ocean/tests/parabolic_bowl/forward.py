from compass.model import run_model
from compass.step import Step


class Forward(Step):
    """
    A step for performing forward MPAS-Ocean runs as part of parabolic bowl
    test cases.
    """
    def __init__(self, test_case, resolution, name='forward', subdir=None,
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

        super().__init__(test_case=test_case, name=name, subdir=subdir)

        self.add_namelist_file('compass.ocean.tests.parabolic_bowl',
                               'namelist.forward')
        if resolution < 1.:
            res_name = f'{int(resolution*1e3)}m'
        else:
            res_name = f'{int(resolution)}km'
        self.add_namelist_file('compass.ocean.tests.parabolic_bowl',
                               f'namelist.{res_name}.forward')
        self.add_namelist_file('compass.ocean.tests.parabolic_bowl',
                               f'namelist.{coord_type}.forward')

        self.add_streams_file('compass.ocean.tests.parabolic_bowl',
                              'streams.forward')

        input_path = '../initial_state'
        self.add_input_file(filename='mesh.nc',
                            target=f'{input_path}/culled_mesh.nc')

        self.add_input_file(filename='init.nc',
                            target=f'{input_path}/ocean.nc')

        self.add_input_file(filename='graph.info',
                            target=f'{input_path}/culled_graph.info')

        self.add_model_as_input()

        self.add_output_file(filename='output.nc')

    def setup(self):
        """
        Set up the test case in the work directory, including downloading
        and dependencies
        """

        self.ntasks = self.config.getint('parabolic_bowl', 'forward_ntasks')
        self.min_tasks = self.config.getint('parabolic_bowl', 'forward_min_tasks')
        self.threads = self.config.getint('parabolic_bowl', 'forward_threads')
