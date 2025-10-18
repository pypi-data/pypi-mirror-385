import os
from collections import defaultdict
from string import ascii_uppercase
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill


from crisscross.helper_functions import plate96, plate384


def add_data_to_plate_df(letters, column_total, data_dict):
    """
    Creates an empty plate (i.e. with rows/columns premade) and inserts provided data dict,
    leaving all empty cells blank.
    :param letters: Letters to use for rows.
    :param column_total: Total amount of columns (numbers)
    :param data_dict: Nested dictionary containing data to input into plate
    (keys are letters, values are dictionaries with numbers as keys)
    :return: Updated plate
    """
    plate_df = pd.DataFrame(index=letters, columns=[str(i) for i in range(1, column_total + 1)])

    if len(data_dict) == 0:
        return plate_df
    else:
        plate_df.update(pd.DataFrame.from_dict(data_dict, orient='index'))
        return plate_df


def read_dna_plate_mapping(filename, data_type='2d_excel', plate_size=384):
    """
    Reads a DNA plate mapping file and returns a dataframe with the data.
    :param filename: Filename to read (full path)
    :param data_type: Type of data - currently only supports 2d_excel and IDT_order
    :param plate_size: Either 96 or 384-well plate sizes
    :return: Dataframe containing all data
    """
    if plate_size == 96:
        plate = plate96
    else:
        plate = plate384

    # this format consists of each sequence in a 2D array, with names and descriptions in separate sheets
    if data_type == '2d_excel':
        all_data = pd.ExcelFile(filename)
        names = all_data.parse("Names", index_col=0)
        sequences = all_data.parse("Sequences", index_col=0)
        descriptions = all_data.parse("Descriptions", index_col=0)
        combined_dict = {}
        for entry in plate:
            n, s, d = names[entry[1:]][entry[0]], sequences[entry[1:]][entry[0]], descriptions[entry[1:]][entry[0]]
            valid_vals = [pd.isna(n), pd.isna(s), pd.isna(d)]
            if sum(valid_vals) == 3:  # all 3 cells are empty
                continue
            elif sum(valid_vals) > 0:  # not all cells of the same ID are full
                raise RuntimeError('The sequence file provided has an inconsistency in entry %s' % entry)

            # if all cells are full, add data to dictionary
            combined_dict[entry] = {'well': entry,
                                    'name': n,
                                    'sequence': s,
                                    'description': d}

        return pd.DataFrame.from_dict(combined_dict, orient='index')

    elif data_type == 'IDT_order':
        all_data = pd.read_excel(filename)
        all_data.columns = ['well', 'name', 'sequence', 'description']
        return all_data
    elif data_type == '#-CAD':
        all_data = pd.read_excel(filename, sheet_name='All Data')
        return all_data
    else:
        raise ValueError('Invalid data type for plate input')


def export_standardized_plate_sheet(data_df, folder, filename, plate_size=384):

    full_data_df = data_df.copy()
    if plate_size == 96:
        max_col = 12
        letters = [a for a in ascii_uppercase[:8]]
    else:
        max_col = 24
        letters = [a for a in ascii_uppercase[:16]]

    name_dict = defaultdict(dict)
    category_dict = defaultdict(dict)

    # prepares categories for 2D layout
    for seq_num, row in data_df.iterrows():
        letter_id, num_id = row['well'][0], row['well'][1:]
        if row['name'] != 'NON-SLAT OLIGO' and not pd.isna(row['name']):
            category = row['name'].split('-')[0]
            if 'ASSEMBLY' in category:
                category_dict[letter_id][num_id] = 'A'
            elif 'SEED' in category:
                category_dict[letter_id][num_id] = 'S'
            elif 'CARGO' in category:
                category_dict[letter_id][num_id] = 'C'
            elif 'FLAT' in category:
                category_dict[letter_id][num_id] = 'F'
        else:
            category_dict[letter_id][num_id] = 'X'

        name_dict[letter_id][num_id] = row['name']

    name_dict = add_data_to_plate_df(letters, max_col, name_dict)
    category_dict = add_data_to_plate_df(letters, max_col, category_dict)

    # plugs empty wells in data df with empty strings
    all_wells = [f"{letter}{num}" for letter in letters for num in range(1, max_col + 1)]
    full_data_df = full_data_df.set_index('well').reindex(all_wells)
    full_data_df = full_data_df.reset_index()

    with pd.ExcelWriter(os.path.join(folder, filename), engine='xlsxwriter') as writer:
        # Write the data to separate sheets
        full_data_df.to_excel(writer, sheet_name='All Data', index=False)
        name_dict.to_excel(writer, sheet_name='2D Layout', index_label=filename.split('.')[0])
        category_dict.to_excel(writer, sheet_name='2D Label', index_label=filename.split('.')[0])

        workbook = writer.book

        ### Format for grey fill
        grey_fill = workbook.add_format({'bg_color': '#DDDDDD'})

        ### Alternating grey rows for '2D Layout'
        layout_sheet = writer.sheets['2D Layout']
        layout_df = name_dict.copy()
        for row_num in range(len(layout_df)):
            if row_num % 2 == 0:
                layout_sheet.set_row(row_num + 1, None, grey_fill)  # +1 because header is row 0

        ### Apply color codes in '2D Label'
        label_sheet = writer.sheets['2D Label']
        label_df = category_dict.copy()

        # Define color formats
        format_A = workbook.add_format({'bg_color': '#FF0000'})  # Red
        format_S = workbook.add_format({'bg_color': '#00FF00'})  # Green
        format_C = workbook.add_format({'bg_color': '#0000FF'})  # Blue
        format_F = workbook.add_format({'bg_color': '#A9A9A9'})  # Dark Grey
        format_X = workbook.add_format({'bg_color': '#D3D3D3'})  # Light Grey

        # Apply cell formats based on value
        for row_num, row in enumerate(label_df.itertuples(index=False), start=1):
            for col_num, value in enumerate(row, start=1):
                fmt = None
                if value == 'A':
                    fmt = format_A
                elif value == 'S':
                    fmt = format_S
                elif value == 'C':
                    fmt = format_C
                elif value == 'F':
                    fmt = format_F
                elif value == 'X':
                    fmt = format_X
                if fmt:
                    label_sheet.write(row_num, col_num, value, fmt)

        ### Auto-fit all columns
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            # Get the correct dataframe for the sheet
            df = {
                'All Data': full_data_df,
                '2D Layout': name_dict,
                '2D Label': category_dict
            }[sheet_name]

            # If index is included, insert it as the first "column"
            if df.index.name or df.index.names != [None]:
                df = df.reset_index()

            for idx, col in enumerate(df.columns):
                # Convert all values in column to string and find the max length
                series = df[col].astype(str)
                max_length = max(series.map(len).max(), len(str(col)))
                worksheet.set_column(idx, idx, max_length + 2)  # NO offset now


def generate_new_plate_from_slat_handle_df(data_df, folder, filename, restart_row_by_column=None,
                                           data_type='2d_excel', plate_size=384, plate_name=None,
                                           scramble_names=False, output_generic_cargo_plate_mapping=False):
    """
    Generates a new plate from a dataframe containing sequences, names and notes, then saves it to file.
    TODO: make faster and more elegant.
    :param data_df: Main sequence data to export containing sequence, name and description.
    :param folder: Output folder.
    :param filename: Output filename.
    :param restart_row_by_column: Set this to a column name to restart the row number when the value changes.
    :param data_type: Either 2d_excel (2d output array) or IDT_order (for IDT order form).
    :param plate_size: 96 or 384
    :param plate_name: Name of the plate (used for IDT order form)
    :param scramble_names: If true, scrubs all identifiable names when preparing an IDT order output
    :param output_generic_cargo_plate_mapping: If true, outputs the generic cargo plate mapping naming schemes
    to the 'names' sheet so that the generic cargo plate system can be used directly from the generated file
    :return: final dataframe that's saved to file
    """
    if plate_size == 96:
        plate = plate96
        max_col = 12
        letters = [a for a in ascii_uppercase[:8]]
    else:
        plate = plate384
        max_col = 24
        letters = [a for a in ascii_uppercase[:16]]

    name_dict = defaultdict(dict)
    seq_dict = defaultdict(dict)
    desc_dict = defaultdict(dict)
    idt_order_dict = defaultdict(list)
    row_num = 0
    column_num = 0
    row_restart_tracker = None

    for seq_num, row in data_df.iterrows():
        if restart_row_by_column is not None:  # allows a new row to restart when a specific column changes
            if row_restart_tracker and row_restart_tracker != row[restart_row_by_column]:
                row_num += 1
                column_num = 0
            row_restart_tracker = row[restart_row_by_column]
        plate_id = plate[row_num * max_col + column_num]
        letter_id, num_id = plate_id[0], plate_id[1:]

        if row['Name'] != 'SKIP':  # a 'skip' name can be used to manually skip a well position
            seq_dict[letter_id][num_id] = row['Sequence']
            name_dict[letter_id][num_id] = row['Name']
            desc_dict[letter_id][num_id] = row['Description']

            idt_order_dict['WellPosition'].append(plate_id)
            idt_order_dict['Name'].append(row['Name'])
            idt_order_dict['Sequence'].append(row['Sequence'])
            idt_order_dict['Notes'].append(row['Description'])

        column_num += 1

        if column_num == max_col:  # tracking when column number should repeat
            row_num += 1
            column_num = 0

    if data_type == '2d_excel':  # three different sheets for sequences, names and descriptions
        seq_dict = add_data_to_plate_df(letters, max_col, seq_dict)
        name_dict = add_data_to_plate_df(letters, max_col, name_dict)
        desc_dict = add_data_to_plate_df(letters, max_col, desc_dict)
        with pd.ExcelWriter(os.path.join(folder, filename)) as writer:
            seq_dict.to_excel(writer, sheet_name='Sequences', index_label=filename.split('.')[0])

            if output_generic_cargo_plate_mapping:
                name_dict.to_excel(writer, sheet_name='Names', index_label='name_side_position')
            else:
                name_dict.to_excel(writer, sheet_name='Names', index_label=filename.split('.')[0])

            desc_dict.to_excel(writer, sheet_name='Descriptions', index_label=filename.split('.')[0])
        return seq_dict
    elif data_type == 'IDT_order':  # all details in one sheet
        output_df = pd.DataFrame.from_dict(idt_order_dict, orient='columns')
        if scramble_names:
            output_df['Notes'] = ''
            output_df['Name'] = ['OLIGO' + str(i) for i in range(len(output_df))]

        with pd.ExcelWriter(os.path.join(folder, filename)) as writer:
            output_df.to_excel(writer, sheet_name=plate_name if plate_name is not None else 'IDT Order', index=False)
        return output_df
    else:
        raise ValueError('Invalid data type for plate input')


# just for testing
if __name__ == '__main__':

    in_name = ['3247.xls', '3248.xls', '3249.xls', '3250.xls', '3251.xls', '3252.xls']
    out_name = ['P3247_SW_xslat_handles.xlsx', 'P3248_SW_xslat_handles.xlsx', 'P3249_SW_xslat_handles.xlsx',
                'P3250_SW_yslat_handles.xlsx', 'P3251_CW_yslat_handles.xlsx', 'P3252_SW_yslat_handles.xlsx']
    sheet_name = ['P3247_SW', 'P3248_SW', 'P3249_SW', 'P3250_SW', 'P3251_CW', 'P3252_SW']

    for inn, outn, sheetn in zip(in_name, out_name, sheet_name):
        seed_plate_corner = read_dna_plate_mapping('/Users/matt/Desktop/%s' % inn, data_type='IDT_order')

        plate = plate384
        max_row = 24
        letters = [a for a in ascii_uppercase[:16]]

        name_dict = defaultdict(dict)
        seq_dict = defaultdict(dict)
        desc_dict = defaultdict(dict)
        row_num = 0
        for index, row in seed_plate_corner.iterrows():
            letter_id = row['well'][0]
            num_id = row['well'][1:]
            seq_dict[letter_id][num_id] = row['sequence']
            name_dict[letter_id][num_id] = row['name']
            desc_dict[letter_id][num_id] = row['description']

        seq_dict = add_data_to_plate_df(letters, max_row, seq_dict)
        name_dict = add_data_to_plate_df(letters, max_row, name_dict)
        desc_dict = add_data_to_plate_df(letters, max_row, desc_dict)

        with pd.ExcelWriter('/Users/matt/Desktop/%s' % outn) as writer:
            seq_dict.to_excel(writer, sheet_name='Sequences', index_label=sheetn)
            name_dict.to_excel(writer, sheet_name='Names', index_label=sheetn)
            desc_dict.to_excel(writer, sheet_name='Descriptions', index_label=sheetn)
