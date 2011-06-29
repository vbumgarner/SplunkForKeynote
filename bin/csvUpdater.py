import csv
import os
import sys

class CsvUpdater(object):

    def __init__(self, path, keyFields):
        self.path = path
        self.keyFields = keyFields
        self.old_data = {}
        if os.path.exists(path):
            old_reader = csv.DictReader(open(path, 'r'))
            for row in old_reader:
#                sys.stderr.write( str(row) + "\n" )
                self.old_data[self.build_row_key(row, self.keyFields)] = row

    def commit(self, data):
        #update the data
        for row in data:
            self.old_data[self.build_row_key(row, self.keyFields)] = row

        #find the fields
        fields = set()
        for row in self.old_data.values():
            fields.update(row.keys());
        fields = sorted(fields)

        #write it out
        w = csv.writer(open(self.path, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(fields)
        for v in self.old_data.values():
            w.writerow(self.build_row(fields,v))

    def build_row_key(self, row, keyFields):
        key = ''
        for k in keyFields:
            key += row[k] + '_'
        return key

    def build_row(self,fields,d):
        r = []
        for f in fields:
            try:
                r.append( d[f] )
            except:
                r.append( '' )
        return r
