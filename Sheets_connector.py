import gspread


def get_sheet(sheet_name, worksheet_name, token_file):
    gc = gspread.oauth(
        credentials_filename="credentials.json",
        authorized_user_filename=token_file
    )
    spreadsheet = gc.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet


def append_purchase_row(worksheet, clean_data):
    row = [clean_data["item"], clean_data["quantity"], clean_data["amount"]]
    worksheet.append_row(row)


if __name__ == "__main__":
    sheet = get_sheet()
    print("Connected successfully to:", sheet.title)
    print("Current rows:", len(sheet.get_all_values()))
