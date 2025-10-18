import os
from crisscross.core_functions.megastructure_composition import convert_slats_into_echo_commands
from crisscross.core_functions.megastructures import Megastructure
from crisscross.slat_handle_match_evolver.tubular_slat_match_compute import multirule_oneshot_hamming
from crisscross.helper_functions import create_dir_if_empty
from crisscross.helper_functions.lab_helper_sheet_generation import prepare_all_standard_sheets
from crisscross.plate_mapping import get_cargo_plates, get_cutting_edge_plates

########################################
# NOTES

# This design uses the full 64 handle library with the H30 handle array, adapted to fit the seed in the center 
# (handles come around the seed)

########## CONFIG
# update these depending on user
experiment_folder = '/Users/stellawang/HMS Dropbox/Siyuan Wang/crisscross_team/Crisscross Designs/SW134_seed_side_growth'

target_designs = ['seed_side_growth', 'hat_with_fringe']

base_design_import_files = [os.path.join(experiment_folder, f"{f}.xlsx") for f in target_designs]
regen_graphics = False
generate_echo = True
generate_lab_helpers = True

main_plates = get_cutting_edge_plates()
cargo_plates = get_cargo_plates()

########## LOADING AND CHECKING DESIGN
for file, design_name in zip(base_design_import_files, target_designs):

    echo_folder = os.path.join(experiment_folder, design_name, 'echo_commands')
    lab_helper_folder = os.path.join(experiment_folder, design_name, 'lab_helper_sheets')
    create_dir_if_empty(echo_folder, lab_helper_folder)
    print('%%%%%%%%%%%%%%%')
    print('ASSESSING DESIGN: %s' % design_name)

    megastructure = Megastructure(import_design_file=file)
    hamming_results = multirule_oneshot_hamming(megastructure.generate_slat_occupancy_grid(), megastructure.generate_assembly_handle_grid(), request_substitute_risk_score=True)
    print('Hamming distance from imported array: %s, Duplication Risk: %s' % (hamming_results['Universal'], hamming_results['Substitute Risk']))

    ########## PATCHING PLATES
    megastructure.patch_placeholder_handles(main_plates + cargo_plates)
    megastructure.patch_flat_staples(main_plates[0])

    target_volume = 75 # nl per staple
    if generate_echo:
        echo_sheet_1 = convert_slats_into_echo_commands(slat_dict=megastructure.slats,
                                     destination_plate_name=design_name,
                                     reference_transfer_volume_nl=target_volume,
                                     output_folder=echo_folder,
                                     center_only_well_pattern=False,
                                     plate_viz_type='barcode',
                                     output_filename=f'{design_name}_echo_commands.csv')

    if generate_lab_helpers:
        prepare_all_standard_sheets(megastructure.slats, os.path.join(lab_helper_folder, f'{design_name}_experiment_helpers.xlsx'),
                                    reference_single_handle_volume=target_volume,
                                    reference_single_handle_concentration=500,
                                    echo_sheet=None if not generate_echo else echo_sheet_1,
                                    peg_concentration=2,
                                    peg_groups_per_layer=2)
