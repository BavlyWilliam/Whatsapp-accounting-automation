from main import process_message


class FakeSheet:
    def append_row(self, row):
        print("Would write:", row)


fake_sheet = FakeSheet()

process_message({"sender": "Test User", "timestamp": "1:00 pm, 01/08/2026",
                "text": "Item: Paper\nQuantity: 6 hrs\nAmount: 450"}, fake_sheet)
process_message({"sender": "Test User", "timestamp": "1:01 pm, 01/08/2026",
                "text": "bought some printer paper today for 450, got 5 of them"}, fake_sheet)
process_message({"sender": "Test User",
                "timestamp": "1:02 pm, 01/08/2026", "text": "pptc"}, fake_sheet)
