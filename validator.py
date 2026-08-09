def validate(data):
    required_fields = ["item", "quantity", "amount"]

    for field in required_fields:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            return False, f"Missing or empty field: {field}"

    item = str(data["item"]).strip()
    if len(item) == 0:
        return False, "Item cannot be empty"

    try:
        quantity = int(data["quantity"])
    except (ValueError, TypeError):
        return False, f"Quantity must be a whole number, got: '{data['quantity']}'"

    if quantity <= 0:
        return False, f"Quantity must be greater than 0, got: {quantity}"

    try:
        amount = float(data["amount"])
    except (ValueError, TypeError):
        return False, f"Amount must be a number, got: '{data['amount']}'"

    if amount <= 0:
        return False, f"Amount must be greater than 0, got: {amount}"

    vendor = str(data.get("vendor", "")).strip()
    project = str(data.get("project", "")).strip()

    clean_data = {
        "item": item,
        "quantity": quantity,
        "amount": amount,
        "vendor": vendor,
        "project": project
    }
    return True, clean_data
