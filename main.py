from parser import parse_message
from validator import validate
from ai_fallback import ai_extract


def process_message(message, worksheet):
    data = parse_message(message["text"])

    if data is not None:
        is_valid, result = validate(data)
        if is_valid:
            _write_row(worksheet, message, result, source="template")
            return

    ai_data = ai_extract(message["text"])
    if ai_data is not None:
        is_valid, result = validate(ai_data)
        if is_valid:
            _write_row(worksheet, message, result, source="ai")
            print(
                f"AI-assisted: {message['sender']} at {message['timestamp']}")
            return

    print(
        f"Rejected ({message['sender']}, {message['timestamp']}): could not extract valid purchase data")


def _write_row(worksheet, message, result, source):
    row = [
        message["timestamp"],
        message["sender"],
        result["item"],
        result["quantity"],
        result["amount"],
        result["vendor"],
        result["project"],
        source
    ]
    worksheet.append_row(row)
    print(f"Added to sheet ({source}): {row}")
