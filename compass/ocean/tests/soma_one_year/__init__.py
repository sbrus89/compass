from compass.ocean.tests.soma.soma_ensemble import SomaEnsemble
from compass.ocean.tests.soma.soma_test_case import SomaTestCase
from compass.testgroup import TestGroup


class Soma(TestGroup):
    """
    A test group for Simulating Ocean Mesoscale Activity (SOMA) test cases
    """
    def __init__(self, mpas_core):
        """
        mpas_core : compass.MpasCore
            the MPAS core that this test group belongs to
        """
        super().__init__(mpas_core=mpas_core, name='soma')

        for resolution in ['4km', '8km', '16km', '32km']:
            self.add_test_case(
                SomaTestCase(test_group=self, resolution=resolution,
                             with_particles=False,
                             with_surface_restoring=False, long=False,
                             three_layer=False))

            self.add_test_case(
                SomaTestCase(test_group=self, resolution=resolution,
                             with_particles=False,
                             with_surface_restoring=False, long=True,
                             three_layer=False))

            if resolution == '32km':
                self.add_test_case(
                    SomaTestCase(test_group=self, resolution=resolution,
                                 with_particles=True,
                                 with_surface_restoring=False, long=False,
                                 three_layer=False))

            self.add_test_case(
                SomaTestCase(test_group=self, resolution=resolution,
                             with_particles=False,
                             with_surface_restoring=True, long=False,
                             three_layer=False))

            self.add_test_case(
                SomaTestCase(test_group=self, resolution=resolution,
                             with_particles=False,
                             with_surface_restoring=False, long=False,
                             three_layer=True))
            self.add_test_case(
                SomaEnsemble(test_group=self, resolution=resolution,
                             with_particles=False,
                             with_surface_restoring=False, long=True,
                             three_layer=False))
