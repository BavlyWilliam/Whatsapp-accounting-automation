from parser import parse_message
from validator import validate

test_message = """PURCHASE
Amount: 562
Item: Printer paper
Quantity: 5"""

parsed = parse_message(test_message)
is_valid, result = validate(parsed)
print("Valid:", is_valid)
print("Result:", result)
