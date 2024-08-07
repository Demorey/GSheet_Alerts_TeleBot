import json
import logging
from itertools import zip_longest
from time import sleep
from typing import Any

import gspread.exceptions


async def spreadsheet_check(gc, spreadsheet_index: int, spreadsheet: dict, spreadsheet_data: dict) -> \
        dict[str, str | None]:
    error_msg = None
    sheet_data = await spreadsheet_get_data(gc, spreadsheet)
    new_data = await spreadsheet_get_rows(gc, spreadsheet)
    if type(new_data) is str and type(sheet_data["sheet_name"]) is str:
        result = new_data
        return {"error": error_msg, "changes": result}
    result = None
    if spreadsheet.get("data"):
        error, changes = await changes_check(spreadsheet["data"], new_data)
        if error:
            error_msg = f"Ошибка в таблице {sheet_data['sheet_name']}\n" + error + "\n\n"
        if (changes != "" and
                sheet_data["worksheet_name"] == spreadsheet_data["SPREADSHEETS"][spreadsheet_index].get(
                    "worksheet_name",
                    sheet_data["worksheet_name"])):
            result = "<b>⚠️ Изменения в таблице: " + sheet_data["sheet_name"] + "</b>\n\n" + changes

    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["name"] = sheet_data["sheet_name"]
    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["worksheet_name"] = sheet_data["worksheet_name"]
    spreadsheet_data["SPREADSHEETS"][spreadsheet_index]["data"] = new_data
    with open('data/spreadsheets_data.json', 'w', encoding='utf-8') as f:
        json.dump(spreadsheet_data, f, ensure_ascii=False, indent=2)

    return {"error": error_msg, "changes": result}


async def spreadsheet_get_data(gc, spreadsheet: dict) -> dict[str, Any] | str:
    sheet_data = {}
    sheet = None
    for attempt_no in range(3):
        try:
            sheet = gc.open_by_url(spreadsheet['url'])
            sheet_data["sheet_name"] = sheet.title
            sheet_data["worksheet_name"] = sheet.sheet1.title
            return sheet_data

        except gspread.exceptions.APIError:
            if attempt_no < 3:
                sleep(30 * (1 + attempt_no))
    if not sheet:
        logging.error("Ошибка при запросе к Google API")
        return "Ошибка при запросе к Google API"


async def spreadsheet_get_rows(gc, spreadsheet: dict) -> str | None | list[Any]:
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


async def changes_check(old_data: list, new_data: list) -> (str | None, str):
    changes = ""
    error = None
    i = 0
    # new_data[i][0] - имя группы
    # new_data[i][1] - дата заселения
    # new_data[i][2] - количество человек
    # new_data[i][3] - отель
    try:
        while i < len(new_data):
            changes_in_row = ""

            if list(new_data[i]) == old_data[i]:
                i += 1
                continue

            if new_data[i][0] == "" and new_data[i][1] == "" and new_data[i][2] == "" and new_data[i][3] == "":
                old_data.insert(i, list(new_data[i]))
                i += 1
                continue

            if new_data[i][1] == "":
                old_data.insert(i, list(new_data[i]))
                i += 1
                continue

            if i > len(old_data):
                old_data.append(["", "", "", ""])
                continue

            if new_data[i][0] != old_data[i][0] and i < len(old_data) - 1:
                # Добавляем новую строку если это новый рейс
                if new_data[i][3] == "":
                    old_data.insert(i, list(new_data[i]))
                    changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Добавлен доп. рейс на {new_data[i][1]}\n\n"
                    i += 1
                    continue
                ex = 0
                for j in range(i, len(old_data)):
                    if new_data[i][0] == old_data[j][0]:
                        changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Рейс удален\n\n"
                        del old_data[i]
                        ex = 1
                        break
                if ex == 0:
                    old_data.insert(i, list(new_data[i]))
                    changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Добавлен доп. рейс на {new_data[i][1]}\n\n"
                i += 1
                continue

            if new_data[i][1] != old_data[i][1]:

                # Добавляем новую строку если это новый рейс
                if new_data[i][3] == "":
                    old_data.insert(i, list(new_data[i]))
                    changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Добавлен доп. рейс на {new_data[i][1]}\n\n"
                    i += 1
                    continue

                # убираем удаленную строку
                if new_data[i][0] != old_data[i][0] and i < len(old_data) - 1:
                    for j in range(i, len(old_data)):
                        if new_data[i][0] == old_data[j][0]:
                            changes += f"Группа {old_data[i][0]} / Рейс {old_data[i][1]}:\n- Рейс удален\n\n"
                            del old_data[i]
                            break
                        if new_data[i][3] == "":
                            continue
                    continue

            if new_data[i][0].lower().count("новый год"):
                if old_data[i][0].lower().count("новый год"):
                    i += 1
                    continue
                else:
                    old_data.insert(i, new_data[i])
                    i += 1
                    continue

            if new_data[i][3] != old_data[i][3]:
                changes_in_row += f"- Изменен отель c {old_data[i][3]} на {new_data[i][3]}\n"
            if new_data[i][2] != old_data[i][2]:
                changes_in_row += f"- Изменилось количество человек - {new_data[i][2]}\n"
            if changes_in_row != "":
                changes += f"Группа {new_data[i][0]} / Рейс {new_data[i][1]}:\n" + changes_in_row + "\n"

            i += 1
    except IndexError:
        error = f"Ошибка в строке {i}"
    return error, changes
