from importlib.resources import read_text

from jinja2 import Template
from mpas_tools.logging import check_call
from mpas_tools.scrip.from_mpas import scrip_from_mpas

from compass import Step


class WavesScripFile(Step):
    """
    A step for creating the scrip file for the wave mesh
    """
    def __init__(self, test_case, wave_culled_mesh, ocean_mesh,
                 name='scrip_file', subdir=None):

        super().__init__(test_case=test_case, name=name, subdir=subdir)

        ocean_mesh_path = ocean_mesh.steps['initial_state'].path
        self.add_input_file(
            filename='ocean_mesh.nc',
            work_dir_target=f'{ocean_mesh_path}/initial_state.nc')

        wave_culled_mesh_path = wave_culled_mesh.path
        self.add_input_file(
            filename='wave_mesh_culled.msh',
            work_dir_target=f'{wave_culled_mesh_path}/wave_mesh_culled.msh')

    def setup(self):

        super().setup()

        template = Template(read_text(
            'compass.ocean.tests.global_ocean.wave_mesh',
            'scrip_file.template'))

        text = template.render()
        text = f'{text}\n'

        with open(f'{self.work_dir}/scrip.nml', 'w') as file:
            file.write(text)

    def run(self):
        """
        Create scrip files for wave mesh
        """
        local_filename = 'ocean_mesh_scrip.nc'
        scrip_from_mpas('ocean_mesh.nc', local_filename)

        check_call('ocean_scrip_wave_mesh', logger=self.logger)