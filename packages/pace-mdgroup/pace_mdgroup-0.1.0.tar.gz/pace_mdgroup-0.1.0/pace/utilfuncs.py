import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from ase.optimize import FIRE
from ase.io import read, write
import matplotlib.pyplot as plt
from ase.build import add_adsorbate
from scipy.interpolate import griddata

# Ultility functions
def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except Exception as e:
            print(f"Failed to create directory '{directory_path}': {e}")
            raise

def pick_arrays(*list_other_info, 
                energies_list : list, 
                select : int):
    no_of_selection = select - 1
    sorted_array = np.array(energies_list).argsort()
    array_ranks = np.empty_like(sorted_array)
    array_ranks[sorted_array] = np.arange(len(energies_list))
    filtered_indices = [array_ranks[idx] for idx in range(len(array_ranks)) if array_ranks[idx] <= no_of_selection]
    unique_corresponding_list = [[lst[i] for i in filtered_indices] for lst in list_other_info]
    return [energies_list[i] for i in filtered_indices], unique_corresponding_list

def rank_lists(*all_list, 
               ref_list: list, 
               select=None):
    sorted_array = np.array(ref_list).argsort()
    sorted_array = sorted_array[:select]

    new_ref_list = [ref_list[idx] for idx in sorted_array]
    new_additional_list = [[lst[idx] for idx in sorted_array] for lst in all_list]
    print('Ranked the Lists')
    return new_additional_list, new_ref_list

def deduplicate_and_rank(*additional_lists, 
                         structures : list, 
                         energies_list : list, 
                         select : int, 
                         by_pos=True):
    no_of_selection = select - 1
    for lst in additional_lists:
        if len(structures) != len(lst):
            raise ValueError(f"structures other lists must have the same length, struct: {len(structures)} != lst: {len(lst)}")

    if by_pos:
        to_dedup = [tuple(map(tuple, structure.positions)) for structure in structures]
    else:
        to_dedup = [(ene,) for ene in energies_list]


    indexed_tuples = [(i, pos) for i, pos in enumerate(to_dedup)]

    seen = set()
    deduped_structures, dedup_ener_list =[], []
    unique_indices = []

    for index, element in indexed_tuples:
        if element not in seen:
            seen.add(element)
            deduped_structures.append(structures[index])
            dedup_ener_list.append(energies_list[index])
            unique_indices.append(index)

    new_additional_list = [np.array(lst)[np.sort(unique_indices)]
                           for lst in tqdm(additional_lists, desc='Removing duplicates', total= len(additional_lists))]

    sorted_array = np.array(energies_list).argsort()
    array_ranks = np.empty_like(sorted_array)
    array_ranks[sorted_array] = np.arange(len(energies_list))
    filtered_indices = [idx for idx in range(len(array_ranks)) if array_ranks[idx] <= no_of_selection]
    unique_corresponding_lists = []

    unique_corresponding_lists = [[lst[i] for i in filtered_indices] for lst in new_additional_list]

    return [deduped_structures[i] for i in filtered_indices], [energies_list[i] for i in filtered_indices], unique_corresponding_lists

def deduplicate(*additional_lists, 
                structures : list, 
                by_pos=True, 
                calculator):

    for lst in additional_lists:
        if len(structures) != len(lst):
            raise ValueError("structures other lists must have the same length")

    if by_pos:
        to_dedup = [tuple(map(tuple, structure.positions)) for structure in structures]
    else:
        pot_ene = []
        for structure in structures:
            structure.calc=calculator
            pot_ene.append(structure.get_potential_energy())
        to_dedup = [(ene,) for ene in pot_ene]


    indexed_tuples = [(i, pos) for i, pos in enumerate(to_dedup)]

    seen = set()
    deduped_structures =[]
    unique_indices = []

    for index, element in indexed_tuples:
        if element not in seen:
            seen.add(element)
            deduped_structures.append(structures[index])
            unique_indices.append(index)

    new_additional_list = [np.array(lst)[np.sort(unique_indices)]
                           for lst in tqdm(additional_lists, desc='Removing duplicates: ', total= len(additional_lists))]
    return deduped_structures, new_additional_list

def contour_plots(fig_save_path, 
                  list_energy, 
                  other_info, 
                  countours,
                  read_data, 
                  save_data, 
                  info_column, 
                  adsorbate, 
                  base, 
                  calculator
                  ):
    
    df = pd.read_csv(f'{read_data}/coordinates.csv')
    x_ax = df.iloc[:,0].values
    y_ax = df.iloc[:,1].values

    energies, (rest_info,) = pick_arrays(other_info, energies_list=list_energy, select=countours )

    create_directory_if_not_exists(save_data)
    
    df = pd.DataFrame(rest_info, columns=info_column)
    df.insert(0, 'Energy', energies)
    df.to_csv(f'{save_data}/single-point_screened_data.csv', index=False)

    create_directory_if_not_exists(fig_save_path)

    all_plot_energies, titles = [], []
    selected_structures = []
    #! Build molecule and create energy grid:
    for phi, theta, psi, x, y, z, file_name_prefix in rest_info:
        plot_energies = []
        for x, y in zip(x_ax, y_ax):
            titles.append(f'positions set: ({phi}-{theta}-{psi})-({x:.2f}-{y:.2f}-{z:.2f})')
            dummy = adsorbate.copy()
            dummy.euler_rotate(phi=phi, theta=theta, psi=psi, center= 'COM')
            slab = base.copy()
            add_adsorbate(slab, dummy, height=z, position=(x,y))
            slab.calc = calculator
            plot_energies.append(slab.get_potential_energy())
        
        for_selected_adsorbate = adsorbate.copy()
        for_selected_adsorbate.euler_rotate(phi=phi, theta=theta, psi=psi, center= 'COM')
        for_selected_base = base.copy()
        add_adsorbate(slab = for_selected_base, adsorbate=for_selected_adsorbate, position=(x,y), height=z)
        for_selected_base.calc = calculator
        selected_structures.append(for_selected_base)
        all_plot_energies.append(plot_energies)

    x_grid, y_grid =np.meshgrid(x_ax, y_ax)

    i = 0
    for energy_grid, title in tqdm(zip(all_plot_energies, titles), desc='Making Countours: ', total=len(all_plot_energies)):
        z = energy_grid
        zz = griddata((x_ax, y_ax), z, (x_grid, y_grid), method='cubic')
        # Plot the contour plot
        plt.figure(figsize=(10, 10))
        contour = plt.contourf(x_grid, y_grid, zz, levels=20, cmap='tab20b', alpha=1)
        plt.colorbar(contour, label='Energy')
        plt.scatter(x_ax, y_ax, c='green', s=50, alpha=0.4)
        plt.title(f'Contour Plot of phi, theta: {title}')
        plt.xlim(x_ax.min()-4, x_ax.max()+4)
        plt.ylim(y_ax.min()-4, y_ax.max()+4)
        plt.xlabel('X-axis Coordinates')
        plt.ylabel('Y-axis Coordinates')
        plt.savefig(f'{fig_save_path}/Plot-{i}.png')
        i+=1

    return selected_structures, rest_info

def mlip_optimizer(structures : list,
                   save_traj, 
                   calculator
                   ):
    optim_structs = []
    i = 0
    def optimize_structure(struct):
        nonlocal i
        i += 1
        struct.calc = calculator
        traj_file = f'{save_traj}/structure-{i}.vasp-xdatcar'
        print(f"Optimizing structure and saving trajectory to {traj_file}")
        FIRE(struct, trajectory=traj_file, logfile=None).run(steps=2000)
        optim_structs.append(struct)
        return struct.get_potential_energy()

    optim_structs_energies = list(map(optimize_structure, tqdm(structures, desc='Optimizing: ', total=  len(structures))))

    return optim_structs, optim_structs_energies