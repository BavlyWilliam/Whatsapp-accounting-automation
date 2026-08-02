from parser import parse_message

normal_message = """Item: Printer paper
Quantity: 5
Amount: 450"""

squished_message = "Item: Not Valve  66020 Quantity: 5555 Amount: 660666"

print(parse_message(normal_message))
print(parse_message(squished_message))
