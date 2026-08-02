def validate(data):
    required_fields = ["item", "quantity", "amount"]

    for field in required_fields:
        if field not in data or not data[field].strip():
            return False, f"Missing or empty field: {field}"

    item = data["item"].strip()
    if len(item) == 0:
        return False, "Item cannot be empty"

    try:
        quantity = int(data["quantity"])
    except ValueError:
        return False, f"Quantity must be a whole number, got: '{data['quantity']}'"

    if quantity <= 0:
        return False, f"Quantity must be greater than 0, got: {quantity}"

    try:
        amount = float(data["amount"])
    except ValueError:
        return False, f"Amount must be a number, got: '{data['amount']}'"

    if amount <= 0:
        return False, f"Amount must be greater than 0, got: {amount}"

    clean_data = {
        "item": item,
        "quantity": quantity,
        "amount": amount
    }
    return True, clean_data
