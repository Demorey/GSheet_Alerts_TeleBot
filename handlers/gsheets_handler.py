import json
from itertools import zip_longest


async def spreadsheet_check(gc, spreadsheet_index: int, spreadsheet: dict, spreadsheet_data: dict) -> str | None:
    sheet_name = await spreadsheet_get_name(gc, spreadsheet)
    new_data = await spreadsheet_get_hotels(gc, spreadsheet)
    result = None
    if spreadsheet.get("data"):
        changes = await changes_check(spreadsheet["data"], new_data)
        if changes != "":
            result = "<b>⚠️ Изменения в таблице: " + sheet_name + "</b>\n\n" + changes

    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["name"] = sheet_name
    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["data"] = new_data
    with open('data/spreadsheets_data.json', 'w', encoding='utf-8') as f:
        json.dump(spreadsheet_data, f, ensure_ascii=False, indent=2)

    return result


async def spreadsheet_get_name(gc, spreadsheet: dict) -> str:
    sheet = gc.open_by_url(spreadsheet['url'])
    worksheet = sheet.get_worksheet(0)
    sheet_name = worksheet.acell("A1").value
    return sheet_name


async def spreadsheet_get_hotels(gc, spreadsheet: dict) -> str and list:
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
        # Пропускаем строку если ее не успели заполнить
        if new_data[i][1] == "":
            continue

        # убираем удаленную строку
        if (len(new_data) < len(old_data)) and (new_data[i][0] != old_data[i][0] or new_data[i][1] != old_data[i][1]):
            changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Рейс удален\n\n"
            del old_data[i]
            i -= 1
            continue

        if new_data[i][1] != old_data[i][1] and new_data[i][3] == "":
            old_data.insert(i, new_data[i])
            changes_in_row += f"- Добавлен доп. рейс на {new_data[i][1]}\n"
        if new_data[i][3] != old_data[i][3]:
            changes_in_row += f"- Изменен отель c {old_data[i][3]} на {new_data[i][3]}\n"
        if new_data[i][2] != old_data[i][2]:
            changes_in_row += f"- Изменилось количество человек - {new_data[i][2]}\n"
        if changes_in_row != "":
            changes += f"Группа {new_data[i][0]} / Рейс {new_data[i][1]}:\n" + changes_in_row + "\n"
    return changes
