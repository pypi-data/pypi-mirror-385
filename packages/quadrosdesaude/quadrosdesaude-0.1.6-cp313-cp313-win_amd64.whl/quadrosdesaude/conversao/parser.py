from dbfread import FieldParser

class StringFieldParser(FieldParser):
    def parse(self, field, data):
        try:
            return data.strip().decode('latin1')
        except (ValueError, AttributeError):
            return data
