import argparse
from pymarc import MARCReader, MARCWriter
parser = argparse.ArgumentParser()
parser.add_argument("file", help="the input MARC file")
args = parser.parse_args()

lost_codes = {
    "0": "",
    "2": "Long Overdue (Lost)",
    "1": "Lost",
    "5": "Lost (On Search)",
    "3": "Lost and Paid For",
    "4": "Missing",
}

notforloan_codes = {
    "0":	"",
    "3":	"Bindery",
    "4":	"By Appointment",
    "-2":	"In Processing",
    "1":	"Library Use Only",
    "5":	"On display",
    "-1":	"Ordered",
    "-3":	"Repair",
    "2":	"Staff Collection",
}

valid_locations = [
    "CART",
    "FACDEV",
    "MAIN",
    "NEWBOOK",
    "DISPLAY",
]

valid_types = [
    "BOOK",
    "SUPPL",
]

total_count = 0
valid_count = 0

with open(args.file, 'rb') as fh:
    reader = MARCReader(fh)
    for record in reader:
        for item in record.get_fields('952'):
            status = []
            valid = True

            # checked out, will be a date if item is checked out
            if item['q'] and item['q'] != "0":
                status.append('checked out')

            # "not for loan", variety of reasons why an item might not circ
            if item['7'] and item['7'] != "0":
                status.append(notforloan_codes[item['7']])
                valid = False

            # 1 is an item is damanged
            if item['4'] and item['4'] != "0":
                status.append('damaged')
                valid = False

            # lost, variety of codes
            if item['1'] and item['1'] != "0":
                status.append(lost_codes[item['1']])
                valid = False

            # 1 if an item has been withdrawn
            if item['0'] and item['0'] != "0":
                status.append('withdrawn')
                valid = False

            if item['c'] not in valid_locations:
                valid = False

            if item['y'] not in valid_types:
                valid = False

            # if len(status) > 0:
            #     print('"' + record.title() + '" item status: ' + ', '.join(status))

            total_count += 1
            if valid is True:
                valid_count += 1

print('Total Records: %i | Valid Records: %i' % (total_count, valid_count))