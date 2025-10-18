import numpy as np
import pandas as pd
import os

from crisscross.core_functions.megastructure_composition import convert_slats_into_echo_commands
from crisscross.core_functions.megastructures import Megastructure
from crisscross.core_functions.plate_handling import generate_new_plate_from_slat_handle_df
from crisscross.core_functions.slat_design import generate_standard_square_slats, attach_cargo_handles_to_core_sequences, generate_patterned_square_cco
from crisscross.slat_handle_match_evolver.tubular_slat_match_compute import multirule_precise_hamming
from crisscross.slat_handle_match_evolver.random_hamming_optimizer import generate_handle_set_and_optimize
from crisscross.core_functions.slats import Slat
from crisscross.helper_functions.standard_sequences import simpsons_anti, simpsons
from crisscross.helper_functions import create_dir_if_empty
from crisscross.plate_mapping.plate_constants import (octahedron_patterning_v1, cargo_plate_folder,
                                                      nelson_quimby_antihandles, h2_biotin_direct)
from crisscross.plate_mapping import get_plateclass, get_standard_plates

########################################
# script setup
output_folder = '/Users/matt/Documents/Shih_Lab_Postdoc/research_projects/optical_computers/design_feb_2024'
output_folder = '/Users/matt/Documents/Shih_Lab_Postdoc/research_projects/crisscross_code/scratch/design_testing_area/optical_pattern_testing'

create_dir_if_empty(output_folder)

np.random.seed(8)
read_handles_from_file = True
read_cargo_patterns_from_file = True
########################################

########################################
# cargo definitions
cargo_1 = 'Bart'
cargo_2 = 'Edna'
cargo_biotin = 'Nelson'
crossbar_linkages = ['Homer', 'Krusty', 'Lisa', 'Marge', 'Patty', 'Quimby', 'Smithers']

# mapping sequences to numbers
crossbar_anti_map = {i + 4: simpsons_anti[crossbar_linkages[i]][:10] for i in range(7)}
crossbar_map = {i + 11: simpsons[crossbar_linkages[i]][-10:] for i in
                range(7)}  # due to reverse complement system, need to take sequence from back
cargo_map = {1: simpsons_anti[cargo_1], 2: simpsons_anti[cargo_2], 3: simpsons_anti[cargo_biotin]}

# mapping names to numbers
crossbar_anti_names = {i + 4: f'10mer-anti{crossbar_linkages[i]}' for i in range(7)}
crossbar_names = {i + 11: f'10mer-{crossbar_linkages[i]}' for i in range(7)}
cargo_names = {1: f'anti{cargo_1}', 2: f'anti{cargo_2}', 3: f'anti{cargo_biotin}'}
cargo_names = {**cargo_names, **crossbar_anti_names, **crossbar_names}

cargo_key_for_new_system = {**cargo_names,
                            **{i + 11: f'{crossbar_linkages[i]}-10mer' for i in range(7)},
                            **{i + 4: f'anti{crossbar_linkages[i]}-10mer' for i in range(7)}}

########################################

########################################
# Plate sequences
# Plate sequences
core_plate, crisscross_antihandle_y_plates, crisscross_handle_x_plates, seed_plate, center_seed_plate, combined_seed_plate = get_standard_plates()
########################################

########################################
# Shape generation and crisscross handle optimisation
slat_array, _ = generate_standard_square_slats(32)
# optimize handles
if read_handles_from_file:
    handle_array = np.loadtxt(os.path.join(output_folder, 'optimized_handle_array.csv'), delimiter=',').astype(
        np.float32)
    handle_array = handle_array[..., np.newaxis]
    result = multirule_precise_hamming(slat_array, handle_array)
    print('Hamming distance from file-loaded design: %s' % result['Universal'])
else:
    handle_array = generate_handle_set_and_optimize(slat_array, unique_sequences=32, max_rounds=3)
    np.savetxt(os.path.join(output_folder, 'optimized_handle_array.csv'), handle_array.squeeze().astype(np.int32), delimiter=',',
               fmt='%i')
########################################

########################################
# prepares cargo pattern
cargo_pattern = generate_patterned_square_cco('diagonal_octahedron_top_corner')
cdf = attach_cargo_handles_to_core_sequences(cargo_pattern, cargo_map, core_plate, slat_type='Y', handle_side=2)
cdf.sort_values(by=['Cargo ID', 'Slat Pos. ID'], inplace=True)
cdf['Category'] = cdf['Cargo ID']
cdf['Handle Side'] = 'h2'

# prepares biotin pattern (full attachment to allow for later adjustment) - not required, Stella already has strands
# biotin_pattern = np.ones((32, 32)) * 3
# biotin_df = attach_cargo_handles_to_core_sequences(biotin_pattern, cargo_map, core_plate, slat_type='X', handle_side=2)
# biotin_df['Category'] = 3
# biotin_df['Handle Side'] = 'h2'
########################################

########################################
# prepares crossbar attachment pattern (pre-made in another script)
crossbar_pattern = np.zeros((32, 32))

crossbar_1_start_stop = {}
for index, sel_pos in enumerate(  # crossbar 1
        [[21.0, 2.0], [18.0, 6.0], [15.0, 10.0], [12.0, 14.0], [9.0, 18.0], [6.0, 22.0], [3.0, 26.0]]):
    if index == 0:
        crossbar_1_start_stop[1] = sel_pos[::-1]  # reversed to match np.where system
    if index == 6:
        crossbar_1_start_stop[32] = sel_pos[::-1]
    crossbar_pattern[int(sel_pos[1]), int(sel_pos[0])] = index + 4

crossbar_2_start_stop = {}
for index, sel_pos in enumerate(  # crossbar 2
        [[31.0, 6.0], [28.0, 10.0], [25.0, 14.0], [22.0, 18.0], [19.0, 22.0], [16.0, 26.0], [13.0, 30.0]]):
    if index == 0:
        crossbar_2_start_stop[1] = sel_pos[::-1]  # reversed to match np.where system
    if index == 6:
        crossbar_2_start_stop[32] = sel_pos[::-1]

    crossbar_pattern[int(sel_pos[1]), int(sel_pos[0])] = index + 4  # incremented by 4 to match with cargo map

crossbar_df = attach_cargo_handles_to_core_sequences(crossbar_pattern, crossbar_anti_map, core_plate, slat_type='X',
                                                     handle_side=2)
crossbar_df['Category'] = 4
crossbar_df['Handle Side'] = 'h2'
crossbar_df.sort_values(by=['Slat Pos. ID'], inplace=True)

# the actual crossbar is defined as a 1x32 array with the attachment staples on the H5 side and biotin staples on the H2 side
single_crossbar_pattern = np.ones((1, 32)) * -1
for index, pos in enumerate([0, 5, 10, 15, 20, 25, 30]):  # as defined by previous script
    single_crossbar_pattern[:, pos] = index + 11

single_crossbar_df = attach_cargo_handles_to_core_sequences(single_crossbar_pattern, crossbar_map, core_plate,
                                                            slat_type='X', handle_side=5)
single_crossbar_df['Category'] = 5
single_crossbar_df['Handle Side'] = 'h5'
########################################

########################################
# combines all patterns, add names and adds the extra biotin anchor strand
full_attachment_df = pd.concat((cdf, crossbar_df, single_crossbar_df))

full_attachment_df.replace({'Cargo ID': cargo_names}, inplace=True)
full_attachment_df['Name'] = full_attachment_df['Cargo ID'] + '_' + full_attachment_df[
    'Handle Side'] + '_cargo_handle_' + full_attachment_df['Slat Pos. ID'].astype(str)
full_attachment_df['Description'] = full_attachment_df['Handle Side'] + ' attachment for slat position ' + \
                                    full_attachment_df[
                                        'Slat Pos. ID'].astype(str) + ', with the ' + full_attachment_df[
                                        'Cargo ID'] + ' cargo strand.'
full_attachment_df.loc[-1] = [f'Biotin-{cargo_biotin}', '/5Biosg/ttt' + simpsons[cargo_biotin], -1, 6, 'N/A',
                              'biotin_anchor',
                              f'Complement for anti{cargo_biotin}, with biotin attached.']  # extra strand to attach to all cargo locations

print('Total new sequences required: %s' % len(full_attachment_df))
########################################

########################################
# generates new cargo plate or reads from file
if read_cargo_patterns_from_file:
    cargo_plate = get_plateclass('GenericPlate', octahedron_patterning_v1, cargo_plate_folder)
else:
    # exports sequences to a new plate
    generate_new_plate_from_slat_handle_df(full_attachment_df, output_folder, 'new_cargo_strands.xlsx',
                                           restart_row_by_column='Category', data_type='2d_excel', plate_size=384)
    idt_plate = generate_new_plate_from_slat_handle_df(full_attachment_df, output_folder,
                                                       'idt_order_new_cargo_strands.xlsx',
                                                       restart_row_by_column='Category', data_type='IDT_order',
                                                       plate_size=384)
    idt_plate.columns = ['well', 'name', 'sequence', 'description']
    cargo_plate = get_plateclass('OctahedronPlate', octahedron_patterning_v1,
                                 output_folder,
                                 pre_read_plate_dfs=[idt_plate])

nelson_plate = get_plateclass('GenericPlate', nelson_quimby_antihandles, cargo_plate_folder)
biotin_plate = get_plateclass('DirectBiotinPlate', h2_biotin_direct, cargo_plate_folder)
########################################
# preparing seed placements
insertion_seed_array = np.arange(16) + 1
insertion_seed_array = np.pad(insertion_seed_array[:, np.newaxis], ((0, 0), (4, 0)), mode='edge')

corner_seed_array = np.zeros((32, 32))
corner_seed_array[0:16, 0:5] = insertion_seed_array

center_seed_array = np.zeros((32, 32))
center_seed_array[8:24, 13:18] = insertion_seed_array

########################################
# Preparing first design - cargo on top, crossbar on bottom
megastructure = Megastructure(slat_array, layer_interface_orientations=[2, (5, 5), 2])
megastructure.assign_assembly_handles(handle_array, crisscross_handle_x_plates, crisscross_antihandle_y_plates)
megastructure.assign_seed_handles(corner_seed_array, seed_plate)
megastructure.assign_cargo_handles_with_array(cargo_pattern, cargo_key_for_new_system, cargo_plate, layer='top')
megastructure.assign_cargo_handles_with_array(crossbar_pattern, cargo_key_for_new_system, cargo_plate, layer='bottom')

# custom slat for crossbar system TODO: is there a way to integrate this into the Megastructure class? YES - JUST USE NEW CARGO DICT SYSTEM
crossbar_slat_1 = Slat('crossbar_slat_1', 0, crossbar_1_start_stop)
crossbar_slat_2 = Slat('crossbar_slat_2', 0, crossbar_2_start_stop)

for i in range(32):
    if single_crossbar_pattern[0, i] != -1:
        sel_plate = cargo_plate
        cargo_id = single_crossbar_pattern[0, i]
        seq = sel_plate.get_sequence(i + 1, 5, cargo_id)
        well = sel_plate.get_well(i + 1, 5, cargo_id)
        plate_name = sel_plate.get_plate_name(i + 1, 5, cargo_id)

        crossbar_slat_1.set_handle(i + 1, 5, seq, well, plate_name,
                                   descriptor='Cargo Plate %s, Crossbar Handle %s' % (plate_name, cargo_id))
        crossbar_slat_2.set_handle(i + 1, 5, seq, well, plate_name,
                                   descriptor='Cargo Plate %s, Crossbar Handle %s' % (plate_name, cargo_id))

    # full biotin layer (anti-Nelson)
    crossbar_slat_1.set_handle(i + 1, 2,
                               nelson_plate.get_sequence(i + 1, 2, 3),
                               nelson_plate.get_well(i + 1, 2, 3),
                               nelson_plate.get_plate_name(i + 1, 2, 3),
                               descriptor='Cargo Plate %s, Nelson Handle' % nelson_plate.get_plate_name())
    crossbar_slat_2.set_handle(i + 1, 2,
                               nelson_plate.get_sequence(i + 1, 2, 3),
                               nelson_plate.get_well(i + 1, 2, 3),
                               nelson_plate.get_plate_name(i + 1, 2, 3),
                               descriptor='Cargo Plate %s, Nelson Handle' % nelson_plate.get_plate_name())

megastructure.slats['crossbar_1'] = crossbar_slat_1
megastructure.slats['crossbar_2'] = crossbar_slat_2

megastructure.patch_flat_staples(core_plate)
megastructure.create_standard_graphical_report(os.path.join(output_folder, 'crossbar_mega_graphics'))

convert_slats_into_echo_commands(megastructure.slats, 'optical_base_plate',
                                 output_folder, 'all_echo_commands_with_crossbars_updated_version.csv')
########################################
# alternate design 1: nelson-biotin on the underside, with no crossbars
biotin_underside_pattern = np.zeros_like(crossbar_pattern)
biotin_underside_pattern[0, :] = 3
biotin_underside_pattern[-1, :] = 3

alt_1_megastructure = Megastructure(slat_array, layer_interface_orientations=[2, (5, 5), 2])
alt_1_megastructure.assign_assembly_handles(handle_array, crisscross_handle_x_plates, crisscross_antihandle_y_plates)
alt_1_megastructure.assign_seed_handles(center_seed_array, center_seed_plate)
alt_1_megastructure.assign_cargo_handles_with_array(cargo_pattern, cargo_key_for_new_system, cargo_plate, layer='top')
alt_1_megastructure.assign_cargo_handles_with_array(biotin_underside_pattern, cargo_key_for_new_system, nelson_plate,
                                                    layer='bottom')
alt_1_megastructure.patch_flat_staples(core_plate)
alt_1_megastructure.create_standard_graphical_report(os.path.join(output_folder, 'alt_1_graphics'))

convert_slats_into_echo_commands(alt_1_megastructure.slats, 'optical_base_plate',
                                 output_folder, 'all_echo_commands_biotin_nelson_no_crossbars.csv')

########################################
# alternate design 2: direct biotins on the underside, no crossbars
biotin_underside_pattern = np.zeros_like(crossbar_pattern)
biotin_underside_pattern[:, 0] = 3
biotin_underside_pattern[:, -1] = 3

alt_2_megastructure = Megastructure(slat_array, layer_interface_orientations=[2, (5, 5), 2])
alt_2_megastructure.assign_assembly_handles(handle_array, crisscross_handle_x_plates, crisscross_antihandle_y_plates)
alt_2_megastructure.assign_seed_handles(center_seed_array, center_seed_plate)
alt_2_megastructure.assign_cargo_handles_with_array(cargo_pattern, cargo_key_for_new_system, cargo_plate, layer='top')
alt_2_megastructure.assign_cargo_handles_with_array(biotin_underside_pattern, {3: 'biotin'}, biotin_plate,
                                                    layer='bottom')
alt_2_megastructure.patch_flat_staples(core_plate)
alt_2_megastructure.create_standard_graphical_report(os.path.join(output_folder, 'alt_2_graphics'))

convert_slats_into_echo_commands(alt_2_megastructure.slats, 'optical_base_plate',
                                 output_folder, 'all_echo_commands_direct_biotin_no_crossbars.csv')
