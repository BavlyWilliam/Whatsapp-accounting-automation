from parser import parse_message
from validator import validate
from Sheets_connector import get_sheet, append_purchase_row


def process_message(message, worksheet):
    data = parse_message(message["text"])
    if data is None:
        return

    is_valid, result = validate(data)
    if not is_valid:
        print(
            f"Rejected ({message['sender']}, {message['timestamp']}): {result}")
        return

    row = [
        message["timestamp"],
        message["sender"],
        result["item"],
        result["quantity"],
        result["amount"]
    ]
    worksheet.append_row(row)
    print(f"Added to sheet: {row}")
