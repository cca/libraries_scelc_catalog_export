"""Usage:
    sharedprint.py INPUT [--output=out.mrc]
    sharedprint.py INPUT [--csv=greenglass.csv]

Process Koha MARC export for SCELC Shared Print.

The two uses above either 1) create a subset of the MARC input that's limited to
circulating items only or 2) performs a comparison between what's in the catalog
and what's in GreenGlass i.e. how many records were added and weeded.

Arguments:
    INPUT       MARC records (.mrc)

Options:
    -h --help       show this usage information
    --debug         show debug information as the script runs
    --output=FILE   output records to this file [default: out.mrc]
    --csv=CSV       GreenGlass CSV to compare input MARC file against
"""
import csv

from docopt import docopt
from pymarc import MARCReader, MARCWriter

# https://library-staff.cca.edu/cgi-bin/koha/admin/authorised_values.pl?searchfield=LOST
lost_codes = {
    "0": "",
    "1": "Lost",
    "2": "Long Overdue (Lost)",
    "3": "Lost and Paid For",
    "4": "Missing",
    "5": "Lost (On Search)",
    "6": "Claims Returned",
}

# https://library-staff.cca.edu/cgi-bin/koha/admin/authorised_values.pl?searchfield=NOT_LOAN
notforloan_codes = {
    "-3":	"Repair",
    "-2":	"In Processing",
    "-1":	"Ordered",
    "0":	"",
    "1":	"Library Use Only",
    "2":	"Staff Collection",
    "3":	"Bindery",
    "4":	"By Appointment",
    "5":	"On display",
}

# https://library-staff.cca.edu/cgi-bin/koha/admin/authorised_values.pl?searchfield=LOC
valid_locations = [
    "CART",
    "FACDEV",
    "MAIN",
    "NEWBOOK",
    "DISPLAY",
]

# https://library-staff.cca.edu/cgi-bin/koha/admin/itemtypes.pl
valid_types = [
    "BOOK",
    "SUPPL",
]

# name of column in the GreenGlass spreadsheet that contains the bib record ID
GG_ID_COLUMN = 'Bib Record Number'
# field and subfield in MARC record that contains the bib record ID
# Koha appears to store it in both 999$c & $d
MARC_ID_FIELD = '999'
MARC_ID_SUBFIELD = 'c'

def validate_item(item):
    # "item status" is an agglomeration of several things
    status = []
    # whether the _item_ we're looking at should be included
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

    # filter items based on location & type
    if item['c'] not in valid_locations:
        valid = False

    if item['y'] not in valid_types:
        valid = False

    if len(status) > 0 and options.get('--debug'):
        print('"' + record.title() + '" item status: ' + ', '.join(status))

    return valid


def main():
    total_count = 0
    valid_count = 0
    with open(options['INPUT'], 'rb') as fh:
        reader = MARCReader(fh, to_unicode=True, force_utf8=True)
        # 1) first mode: write a MARC output file
        if not options['--csv']:
            writer = MARCWriter(open('out.mrc' or options['--output'], 'wb'))
            for record in reader:
                # whether we'll include the _bib_ record in export file
                include_record = False
                # Koha stores item data in 952 fields, one per item
                for item in record.get_fields('952'):
                    valid = validate_item(item)

                    total_count += 1
                    if valid is True:
                        valid_count += 1
                        # if there's any valid item then the bib should be included
                        include_record = True

                if include_record is True:
                    writer.write(record)

            print('Total items: %i | Items included: %i' % (total_count, valid_count))
        elif options['--csv']:
            koha_record_ids = set()
            for record in reader:
                total_count += 1
                for item in record.get_fields('952'):
                    valid = validate_item(item)
                    if valid:
                        id = record.get_fields(MARC_ID_FIELD)[0].get_subfields(MARC_ID_SUBFIELD)[0]
                        koha_record_ids.add(id)
                        # stop looking at items after we find the first valid one
                        break

            csvreader = csv.DictReader(open(options['--csv'], 'r'))
            gg_record_ids = set()
            for row in csvreader:
                gg_record_ids.add(row[GG_ID_COLUMN])

            print('Total Koha Bibs: %i' % total_count)
            print('Koha Bibs with circulating items: %i ' % len(koha_record_ids))
            print('Total GreenGlass Bibs: %i' % len(gg_record_ids))
            print('Weeded Items (I in GG & not in Koha): %i' % len(gg_record_ids - koha_record_ids))
            print('Added Items (I in Koha & not in GG): %i' % len(koha_record_ids - gg_record_ids))


if __name__ == '__main__':
    options = docopt(__doc__)
    # print(options)
    main()
