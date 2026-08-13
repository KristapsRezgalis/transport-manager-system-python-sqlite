from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries
from openpyxl.utils import get_column_letter
import datetime
import copy

def add_row_to_table(filepath, sheet_name, table_name, data):   # , row_dict):
    wb = load_workbook(filepath)
    ws = wb[sheet_name]
    table = ws.tables[table_name]
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    row_dict = {
        "Nosūtītājs": data.get('sender'),
        "Adrese": f"{df_sender_company_address['adr_street'].iloc[0]}", f"{df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}", f"{df_sender_company_address['adr_country'].iloc[0]}",
        "Valsts": "Latvija",
        "Piegāde": "Mūkusalas 75",
        "Paletes": 5,
        "Svars": 800,
        "Izmērs": "80x120",
        # LDM is auto-filled by the function — don't include it here
        "Iekraušana līdz": datetime.datetime(2026, 8, 20),
        "Izkraušana līdz": datetime.datetime(2026, 8, 25),
        "Pārvadātājs": "Test Carrier SIA",
        "Transporta cena, EUR": 300,
        "SAP PO": "26402999",
        "Iepircējs": "Arnis K.",
        # CO2 kg is auto-filled too
    }

    min_col, min_row, max_col, max_row = range_boundaries(table.ref)

    header_cells = next(ws.iter_rows(min_row=min_row, max_row=min_row,
                                       min_col=min_col, max_col=max_col))
    col_map = {cell.value: cell.column for cell in header_cells}

    for key in row_dict:
        if key not in col_map:
            raise ValueError(f"'{key}' is not a real column name. Available: {list(col_map.keys())}")

    new_row_number = max_row + 1
    template_row_number = max_row  # the last existing data row — we'll copy its formatting

    def copy_format(col_num, target_cell):
        """Copies number format (and basic style) from the row above into the new cell."""
        template_cell = ws.cell(row=template_row_number, column=col_num)
        target_cell.number_format = template_cell.number_format
        target_cell.font = copy.copy(template_cell.font)
        target_cell.border = copy.copy(template_cell.border)
        target_cell.fill = copy.copy(template_cell.fill)
        target_cell.alignment = copy.copy(template_cell.alignment)

    # Write every column, applying formatting even to blank ones
    for col_num in range(min_col, max_col + 1):
        cell = ws.cell(row=new_row_number, column=col_num)
        copy_format(col_num, cell)

    # Now set the actual values on top of the copied formatting
    for column_name, value in row_dict.items():
        col_num = col_map[column_name]
        ws.cell(row=new_row_number, column=col_num, value=value)

    ws.cell(row=new_row_number, column=col_map['LDM'],
            value=f"=0.4*{table_name}[[#This Row],[Paletes]]")

    svars_col_letter = get_column_letter(col_map['Svars'])
    cena_col_letter = get_column_letter(col_map['Transporta cena, EUR'])
    ws.cell(row=new_row_number, column=col_map['CO2 kg'],
            value=f"=({svars_col_letter}{new_row_number}/1000)*{cena_col_letter}{new_row_number}*0.1")

    table.ref = f"{get_column_letter(min_col)}{min_row}:{get_column_letter(max_col)}{new_row_number}"

    wb.save(filepath)
    print(f"Added row {new_row_number}")

filepath = r"C:\Users\kristaps.rezgalis\Gemoss SIA\Transports - Dokumenti\Transports 2025.xlsx"

new_row = {
    "Nosūtītājs": "Test Sender Ltd",
    "Adrese": "Some Street 1, Country",
    "Valsts": "Latvija",
    "Piegāde": "Mūkusalas 75",
    "Paletes": 5,
    "Svars": 800,
    "Izmērs": "80x120",
    # LDM is auto-filled by the function — don't include it here
    "Iekraušana līdz": datetime.datetime(2026, 8, 20),
    "Izkraušana līdz": datetime.datetime(2026, 8, 25),
    "Pārvadātājs": "Test Carrier SIA",
    "Transporta cena, EUR": 300,
    "SAP PO": "26402999",
    "Iepircējs": "Arnis K.",
    # CO2 kg is auto-filled too
}

add_row_to_table(filepath, "Aug 2026 ", "TabulaAug2026", new_row)