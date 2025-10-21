import itertools
import numpy as np
import pandas as pd
from tqdm import tqdm
from ase.optimize import FIRE
from ase.io import read, write
from ase.build import add_adsorbate
from ase.constraints import FixAtoms
from ase.io.trajectory import Trajectory


from mdgroup.utilfuncs import *


class PACE:
    
    """
    PACE (Precise & Accelerated Configuration Evaluation) class for systematic
    screening of adsorbate positions and orientations over a surface.

    Attributes:
        base (ase.Atoms): The surface structure (slab).
        adsorbate (ase.Atoms): The adsorbate molecule to place on the surface.
        division (int): Number of subdivisions in x and y directions for lateral positions.
        z_levels (list of float): List of distances above the slab to try placing the adsorbate.
        arch (str): Folder name or identifier for model architecture and file paths.
        info_column (list of str): Metadata columns for generated conformations.
        mlip_filtered_structures_path (str): Directory to store filtered/optimized structures.
        screen_data_path (str): Directory to store screening data (CSV, figures).
        traj_path (str): Directory to store trajectory files.
    """
    def __init__(self, 
                 arch,  
                 base, 
                 adsorbate, 
                 division, 
                 z_levels):
        
        """
        Initialize the PACE class with necessary inputs.

        Args:
            arch (str): Identifier for model architecture and directory prefix.
            base (ase.Atoms): Base surface (slab) structure.
            adsorbate (ase.Atoms): Adsorbate molecule to screen.
            division (int): Number of divisions along the surface plane.
            z_levels (list of float): List of heights to test above the slab.
        """
        
        self.base = base
        self.adsorbate = adsorbate
        self.division = division
        self.z_levels = z_levels
        self.arch = arch
        self.info_column = ['phi', 'theta', 'psi', 'x', 'y', 'z', 'file_name_prefix']
        self.mlip_filtered_structures_path = 'mlip_optim_structs'
        self.screen_data_path = 'screen_data'
        self.traj_path = 'trajectory_data'

    def _setup(self):

        self.adsorbate.set_cell(self.base.cell)
        lattice_parameters = [self.base.cell[i][i] for i in range(3)]
        a, b, c = lattice_parameters

        cos = np.dot(self.base.cell[0], -self.base.cell[1]) / (np.linalg.norm(self.base.cell[0]) * np.linalg.norm(self.base.cell[1]))

        pos_x = [(d * a) / (self.division - 1) for d in range(self.division)]
        pos_y = [(d * b) / (self.division - 1) for d in range(self.division)]

        return cos, pos_x, pos_y
    
    def screen(self, 
               calculator, 
               fig_save_at : str,
               euler_angles=None, 
               mlip_optimization=20,
               make_countours=5):

        """
        Main function to screen adsorbate orientations and positions on a surface.

        This includes:
        - Optimization of base and adsorbate
        - Sampling of configurations (rotation, lateral and vertical translations)
        - Pre-screening using energy calculations
        - Contour plotting of energy surfaces
        - MLIP-based re-optimization of top candidates
        - Saving of optimized conformers

        Args:
            calculator (ase.calculators.Calculator): Calculator to compute energies.
            fig_save_at (str): Path to save generated contour plots.
            euler_angles (tuple or list of list, optional): Euler angles (phi, theta, psi) to rotate adsorbate.
            mlip_optimization (int): Number of top configurations to re-optimize with MLIP.
            make_countours (int): Number of top configurations to include in contour plots.

        Returns:
            dict: Dictionary with key 'screened_structures' and value as a list of ranked ase.Atoms objects.
        """

        model_arch_name = self.arch
        create_directory_if_not_exists(model_arch_name)

        cos, x_positions, y_positions = self._setup()
        self.adsorbate.calc = calculator; self.base.calc = calculator

        create_directory_if_not_exists(model_arch_name + '/' + self.mlip_filtered_structures_path)
        create_directory_if_not_exists(model_arch_name + '/' + self.traj_path)

        print("Starting optimization of adsorbate and base")
        
        FIRE(self.adsorbate, f'{model_arch_name}/{self.mlip_filtered_structures_path}/adsorb_opt.vasp-xdatcar', logfile=None).run(steps=2000)
        FIRE(self.base, f'{model_arch_name}/{self.mlip_filtered_structures_path}/base_opt.vasp-xdatcar', logfile=None).run(steps=2000)
        
        write(filename=model_arch_name+'/'+self.mlip_filtered_structures_path + f'base_optimised.vasp', images=self.base)
        write(filename=model_arch_name+'/'+self.mlip_filtered_structures_path + f'adsorbate_optimised.vasp', images=self.adsorbate)
        # self.base.set_constraint(FixAtoms(indices=[atom.index for atom in self.base]))

        if euler_angles != None:
            phis, thetas, psis = [euler_angles]*3

        else:
            phis, thetas, psis = [[0, -45, -90, -135, -180, -225, -270, -315]]*3

        x_positions_new = []
        coordinates_data = []
        
        for y in y_positions:
            for x in x_positions:
                x = x - (cos * np.sqrt(1 - np.square(cos)) * y)
                x_positions_new.append(x)
                coordinates_data.append((x,y))
                
        assign_angles = list(itertools.product(phis, thetas, psis))
        assign_positions = list(itertools.product(self.z_levels, y_positions, x_positions_new[:len(x_positions)]))

        adsorbate_conform, all_structures = [], []
        all_other_info = []

        create_directory_if_not_exists(model_arch_name + '/' + self.screen_data_path)
        pd.DataFrame(coordinates_data, columns=['x', 'y']).to_csv(f'{model_arch_name}/{self.screen_data_path}/coordinates.csv', index=False)

        prev_z = None
        counter = 0

        print('Initiating iterations')
        for phi, theta, psi in assign_angles:
            
            dummy = self.adsorbate.copy()
            dummy.euler_rotate(phi=phi, theta=theta, psi=psi, center='COP')
            dummy.positions -= dummy.get_center_of_mass()
            adsorbate_conform.append(dummy)

        # Remove duplicate adsorbate conformations
        adsorbate_conform, (assign_angles,) = deduplicate(assign_angles, structures=adsorbate_conform, calculator=calculator)


        global traj_files
        traj_files=[]
        for z, y, x in tqdm(assign_positions, desc='Making conformations: '):
            if z != prev_z:
                counter+=1
                prev_z = z

                try:
                    file_name_prefix = ''.join(str(z).split('.'))
                except:
                    file_name_prefix = str(z)
                zlvl_images = []

                traj_file = f'{model_arch_name}/{self.traj_path}/{file_name_prefix}-lvl.traj'
                traj_files.append(traj_file)

            for adsorbate, euler_angles in (zip(adsorbate_conform, assign_angles)):
                slab = self.base.copy()
                dummy_ads = adsorbate.copy()
                dummy_ads.translate([0, 0, slab.positions[:, 2].max() - dummy_ads.positions[:, 2].min()])
                dummy_ads.positions += [x,y,z]
                # adsorbate.translate([x, y, z])
                
                system = slab+dummy_ads
                # system.extend(dummy_ads)
                
                # add_adsorbate(system=system, adsorbate=adsorbate, height=z, position=(x,y))
                system.set_pbc([True, True, False])
                system.wrap()
                system.calc = calculator
                all_structures.append(system)
                with Trajectory(traj_file, mode='a') as traj:
                    traj.write(system)
                all_other_info.append((tuple(euler_angles) + ( x, y, z, file_name_prefix)))

        print(f"Generated trajectory files: {traj_files}")

        pd.DataFrame(all_other_info, columns=self.info_column).to_csv(f'{model_arch_name}/{self.screen_data_path}/conformations_generated.csv', index=False)
        if len(self.z_levels) > 1:
            write(f'{model_arch_name}/{self.traj_path}/to_screen.vasp-xdatcar', all_structures)
        print('TO SCREEN: ', len(all_structures))

        #! Calculate energies:
        def calc_energies(structure):
            structure.calc = calculator
            return structure.get_potential_energy()

        all_energies = list(map(calc_energies, tqdm(all_structures, desc='Pre-screening (SP): ', total=len(all_structures))))

        #! Make plots:
        print(f'Stage 2 complete \n Making Countour plots of top: {make_countours} ... \n')

        if make_countours > 0:                
            
            contour_filtered_structures, contour_filtered_info = contour_plots(fig_save_path=model_arch_name + '/' + fig_save_at, 
                                                                               adsorbate=self.adsorbate, 
                                                                               base=self.base,
                                                                               list_energy=all_energies, 
                                                                               other_info=all_other_info, 
                                                                               countours=make_countours,
                                                                               read_data=model_arch_name + '/' + self.screen_data_path, 
                                                                               save_data=model_arch_name + '/' + self.screen_data_path,
                                                                               calculator=calculator, 
                                                                               info_column=self.info_column
                                                                               )
            
        #! Deduplicate and rank:        
        (all_other_info, all_structures), all_energies = rank_lists(all_other_info, all_structures, 
                                                                    ref_list=all_energies, 
                                                                    select=mlip_optimization
                                                                    )
        
        # all_energies, all_structures, all_other_info = pick_arrays(all_structures, all_other_info, energies_list=all_energies, select=mlip_optimization)

        #! MLIP Optimization        
        print(f'Initiating optimisation of top {mlip_optimization} structures.')

        if mlip_optimization > 0:
            all_structures, all_energies = mlip_optimizer(structures=all_structures, 
                                                          save_traj=model_arch_name + '/' + self.traj_path, 
                                                          calculator=calculator
                                                          )
            
            df = pd.DataFrame(all_other_info, columns=self.info_column)
            df.insert(0, 'Energy', all_energies)
            df.to_csv(f'{model_arch_name}/{self.screen_data_path}/mlip_optimized_data.csv', index=False)
            # all_structures, all_other_info = deduplicate(all_other_info, structures=all_structures)
        else:
            all_structures = contour_filtered_structures
            all_other_info = contour_filtered_info

        
        #! saving all optimized conformations:
        sorted_array = np.array(all_energies).argsort(); array_ranks = np.empty_like(sorted_array)
        array_ranks[sorted_array] = np.arange(len(all_energies))
        ranked_structures = [all_structures[idx] for idx in sorted_array]
        for i in range(len(ranked_structures)):
            write(filename=model_arch_name+'/'+self.mlip_filtered_structures_path + "/" + f'structure_{i+1}.vasp', images=ranked_structures[i])
        # write(f'{model_arch_name}/{self.mlip_filtered_structures_path}/top_{mlip_optimization}_optimized_structures', all_structures, format='vasp-xdatcar')

        print(f"{'-x-o-'*20} \n SCREENING COMPLETE \n{'-x-o-'*20}")
        
        return dict({'screened_structures': ranked_structures})