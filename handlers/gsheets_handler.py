import json
import logging
from itertools import zip_longest
from time import sleep
from typing import List, Any

import gspread.exceptions


async def spreadsheet_check(gc, spreadsheet_index: int, spreadsheet: dict, spreadsheet_data: dict) -> str | None:
    sheet_name = await spreadsheet_get_name(gc, spreadsheet)
    new_data = await spreadsheet_get_hotels(gc, spreadsheet)
    worksheet_name = await spreadsheet_get_worksheet_name(gc, spreadsheet)
    if type(new_data) is str and type(sheet_name) is str:
        result = new_data
        return result
    result = None
    if spreadsheet.get("data"):
        changes = await changes_check(spreadsheet["data"], new_data)
        if (changes != "" and
                worksheet_name == spreadsheet_data["SPREADSHEETS"][spreadsheet_index].get("worksheet_name",
                                                                                          worksheet_name)):
            result = "<b>⚠️ Изменения в таблице: " + sheet_name + "</b>\n\n" + changes

    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["name"] = sheet_name
    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["worksheet_name"] = worksheet_name
    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["data"] = new_data
    with open('data/spreadsheets_data.json', 'w', encoding='utf-8') as f:
        json.dump(spreadsheet_data, f, ensure_ascii=False, indent=2)

    return result


async def spreadsheet_get_name(gc, spreadsheet: dict) -> str:
    sheet = None
    sheet_name = None
    for attempt_no in range(3):
        try:
            sheet = gc.open_by_url(spreadsheet['url'])
            sheet_name = sheet.title
            if sheet_name:
                return sheet_name

        except gspread.exceptions.APIError:
            if attempt_no < 3:
                sleep(30 * (1 + attempt_no))
    if not sheet:
        logging.error("Ошибка при запросе к Google API")
        return "Ошибка при запросе к Google API"


async def spreadsheet_get_worksheet_name(gc, spreadsheet: dict) -> str:
    worksheet_name = None
    for attempt_no in range(3):
        try:
            sheet = gc.open_by_url(spreadsheet['url'])
            worksheet_name = sheet.sheet1.title
            break
        except gspread.exceptions.APIError:
            if attempt_no < 3:
                sleep(30 * (1 + attempt_no))
    return worksheet_name


async def spreadsheet_get_hotels(gc, spreadsheet: dict) -> str | None | list[Any]:
    sheet = None
    worksheet = None
    worksheet_col_names = []
    for attempt_no in range(3):
        try:
            sheet = gc.open_by_url(spreadsheet['url'])
            worksheet = sheet.get_worksheet(0)
            worksheet_col_names = worksheet.row_values(1)
            break
        except gspread.exceptions.APIError:
            if attempt_no < 3:
                sleep(30 * (1 + attempt_no))
    if not sheet or not worksheet or not worksheet_col_names:
        logging.error("Ошибка при запросе к Google API")
        return "Ошибка при запросе к Google API"

    hotel_column_index = None
    zasel_column_index = None
    chel_column_index = None
    i = 0
    try:
        for i in range(len(worksheet_col_names)):
            if worksheet_col_names[i].lower().startswith("отел"):
                hotel_column_index = i + 1
            elif worksheet_col_names[i].lower() == "заселение":
                zasel_column_index = i + 1
            elif worksheet_col_names[i].lower().count("человек") != 0:
                chel_column_index = i + 1
            if hotel_column_index and zasel_column_index and chel_column_index:
                break
        if hotel_column_index is None \
                or zasel_column_index is None \
                or chel_column_index is None:
            return None
    except IndexError:
        logging.error(f"Ошибка в таблице {spreadsheet['url']} на строке {i}")
        return f"Ошибка в таблице {spreadsheet['url']} на строке {i}"

    for attempt_no in range(3):
        try:
            group_names = worksheet.col_values(1)[1:]
            zasel_dates = worksheet.col_values(zasel_column_index)[1:]
            chelovek = worksheet.col_values(chel_column_index)[1:]
            hotel_names = worksheet.col_values(hotel_column_index)[1:]
            zipped_list = list(zip_longest(group_names, zasel_dates, chelovek, hotel_names, fillvalue=''))
            return zipped_list
        except gspread.exceptions.APIError:
            if attempt_no < 3:
                sleep(30 * (1 + attempt_no))
    if not sheet or not worksheet or not worksheet_col_names:
        logging.error("Ошибка при запросе к Google API")
        return "Ошибка при запросе к Google API"


async def changes_check(old_data: list, new_data: list) -> str:
    changes = ""
    i = 0
    while i < len(new_data):
        changes_in_row = ""

        if new_data[i][1] == "":
            i += 1
            continue
        if i > len(old_data) - 1:
            old_data.append(["", "", "", ""])

        if new_data[i][1] != old_data[i][1]:

            if new_data[i][0].lower().count("новый год"):
                old_data.insert(i, new_data[i])
                i += 1
                continue
            if new_data[i][0] == "" and new_data[i][1] == "" and new_data[i][2] == "" and new_data[i][3] == "":
                old_data.insert(i, new_data[i])
                i += 1
                continue

            # убираем удаленную строку
            if new_data[i][0] != old_data[i][0] and i < len(old_data) - 1 and new_data[i][0] == old_data[i + 1][0]:
                changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Рейс удален\n\n"
                del old_data[i]
                continue
            # Добавляем новую строку если это новый рейс
            if new_data[i][3] == "":
                old_data.insert(i, new_data[i])
                changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Добавлен доп. рейс на {new_data[i][1]}\n\n"
                i += 1
                continue

        if new_data[i][3] != old_data[i][3]:
            changes_in_row += f"- Изменен отель c {old_data[i][3]} на {new_data[i][3]}\n"
        if new_data[i][2] != old_data[i][2]:
            changes_in_row += f"- Изменилось количество человек - {new_data[i][2]}\n"
        if changes_in_row != "":
            changes += f"Группа {new_data[i][0]} / Рейс {new_data[i][1]}:\n" + changes_in_row + "\n"
        i += 1
    return changes
