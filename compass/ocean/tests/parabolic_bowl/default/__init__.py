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
    coord_type : str
        The type of vertical coordinate (``sigma``, ``single_layer``, etc.)
    """

    def __init__(self, test_group, coord_type):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.parabolic_bowl.ParabolicBowl
            The test group that this test case belongs to

        coord_type : str
            The type of vertical coordinate (``sigma``, ``single_layer``)
        """
        name = 'default'
        self.coord_type = coord_type

        subdir = f'{coord_type}/{name}'
        super().__init__(test_group=test_group, name=name,
                         subdir=subdir)

        resolutions = [5, 10, 20]
        for resolution in resolutions: 

            res_name = f'{resolution}km'

            self.add_step(InitialState(test_case=self,
                                       name=f'initial_state_{res_name}',
                                       resolution=resolution,
                                       coord_type=coord_type))
            self.add_step(Forward(test_case=self,
                                  name=f'forward_{res_name}',
                                  resolution=resolution,
                                  coord_type=coord_type))
        self.add_step(Viz(test_case=self, resolutions = resolutions))
 

    def configure(self):
        """
        Modify the configuration options for this test case.
        """

        config = self.config

#    def validate(self):
#        """
#        Validate variables against a baseline
#        """
#        variables = ['layerThickness', 'normalVelocity']
#        compare_variables(test_case=self, variables=variables,
#                          filename1='forward/output.nc')
