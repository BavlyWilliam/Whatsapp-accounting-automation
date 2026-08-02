import re


def parse_message(message_text):
    pattern = r"(\w+)\s*:\s*(.*?)(?=\s+\w+\s*:|$)"
    matches = re.findall(pattern, message_text.strip())

    data = {}
    for key, value in matches:
        key = key.strip().lower()
        value = value.strip()
        if key and value:
            data[key] = value

    if not data:
        return None

    return data
