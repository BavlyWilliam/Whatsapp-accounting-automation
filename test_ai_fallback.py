from main import process_message


class FakeSheet:
    def append_row(self, row):
        print("Would write:", row)


fake_sheet = FakeSheet()

process_message({"sender": "Test User", "timestamp": "1:00 pm, 01/08/2026",
                "text": "Itm: Cable\nQiantity: 3\nAmout: 90\nVendor: ElectroShop"}, fake_sheet)
process_message({"sender": "Test User", "timestamp": "1:01 pm, 01/08/2026",
                "text": "الصنف: كابل\nالكمية: 3\nالسعر: 90"}, fake_sheet)
process_message({"sender": "Test User", "timestamp": "1:02 pm, 01/08/2026",
                "text": "bought 2 items of paper for 450 from Office World"}, fake_sheet)
