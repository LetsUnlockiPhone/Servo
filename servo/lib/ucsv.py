"""
Borrwed from
http://stackoverflow.com/questions/1846135/python-csv-library-with-unicode-utf-8-support-that-just-works
"""

import csv
import codecs

class UnicodeCsvReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next() 
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num


class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwargs):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwargs)
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwargs)


def read_excel_file(f):
    dialect = csv.Sniffer().sniff(codecs.EncodedFile(f, "utf-8").read(1024))
    #f.open()
    return UnicodeCsvReader(codecs.EncodedFile(f, "utf-8"),
                            "utf-8", dialect=dialect)

def main():
    import sys
    with codecs.open(sys.argv[1], 'rUb') as csvfile:
        reader = read_excel_file(csvfile)
        for row in reader:
            print u', '.join(row)


if __name__ == '__main__':
    main()
