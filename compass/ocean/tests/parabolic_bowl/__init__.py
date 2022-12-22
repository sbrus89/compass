from compass.testgroup import TestGroup
from compass.ocean.tests.parabolic_bowl.default import Default


class ParabolicBowl(TestGroup):
    """
    A test group for parabolic bowl (wetting-and-drying) test cases
    """

    def __init__(self, mpas_core):
        """
        mpas_core : compass.MpasCore
            the MPAS core that this test group belongs to
        """
        super().__init__(mpas_core=mpas_core, name='parabolic_bowl')

        for coord_type in ['sigma', 'single_layer']:
            self.add_test_case(
                Default(test_group=self, coord_type=coord_type))
