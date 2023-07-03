import json
from itertools import zip_longest

import gspread


def spreadsheet_get_hotels(gc, spreadsheet) -> list:
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


async def changes_check(old_data: list, new_data: list) -> str:
    changes = ""
    for i in range(len(new_data)):
        changes_in_row = ""
        if new_data[i][1] != old_data[i][1] and new_data[i][3] == "":
            old_data.insert(i, new_data[i])
            changes_in_row += f"- Добавлен доп. рейс на {new_data[i][1]}\n"
        if new_data[i][3] != old_data[i][3]:
            changes_in_row += f"- Изменен отель - {new_data[i][3]}\n"
        if new_data[i][2] != old_data[i][2]:
            changes_in_row += f"- Изменилось количество человек - {new_data[i][2]}\n"
        if changes_in_row != "":
            changes += f"Группа {new_data[i][0]} / Рейс {new_data[i][1]}:\n" + changes_in_row + "\n"
    return changes
