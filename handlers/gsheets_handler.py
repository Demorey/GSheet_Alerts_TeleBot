import json
import string
from itertools import zip_longest

import gspread

def spreadsheet_get_hotels(gc, spreadsheet) -> list | None:
    sheet = gc.open_by_url(spreadsheet['url'])
    worksheet = sheet.get_worksheet(0)
    worksheet_value = worksheet.get_all_cells()
    hotel_column_index = None
    zasel_column_index = None
    chel_column_index = None
    for row in worksheet_value:
        if row.value.lower().startswith("отел"):
            hotel_column_index = row.col
        elif row.value.lower() == "заселение":
            zasel_column_index = row.col
        elif row.value.lower().count("человек") != 0:
            chel_column_index = row.col
        if hotel_column_index and zasel_column_index and chel_column_index:
            break
    if hotel_column_index is None \
            or zasel_column_index is None \
            or chel_column_index is None:
        return None
    group_names = worksheet.col_values(1)[1:]
    zasel_dates = worksheet.col_values(zasel_column_index)[1:]
    chelovek = worksheet.col_values(chel_column_index)[1:]
    hotel_names = worksheet.col_values(hotel_column_index)[1:]

    zipped_list = list(zip_longest(group_names, zasel_dates, chelovek, hotel_names, fillvalue=''))

    return zipped_list


def hotel_checker(old_data: list, new_data: list) -> string:
    changes = ""
    for row in new_data:
        if row[1] != new_data[1]:
            pass
    return changes

if __name__ == '__main__':
    gc = gspread.service_account(filename='config_data/service_acc.json')

    with open('config_data/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    spreadsheet_list = config["SPREADSHEETS"]
    for i, spreadsheet in enumerate(spreadsheet_list):
        new_data = spreadsheet_get_hotels(gc, spreadsheet)
        # changes = hotel_checker(spreadsheet[i]["data"], new_data)
        # print(changes)

        config["SPREADSHEETS"][i]["data"] = new_data
        with open('config_data/config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
