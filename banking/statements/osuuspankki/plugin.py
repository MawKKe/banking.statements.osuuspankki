# -*- encoding: utf-8 -*-
import csv
import decimal
from banking.statements.plugin import CSVReaderPlugin
from banking.statements.config import FIELDS
from banking.statements.util import logger, ColumnMismatchError


# csv format, from circa 2004
class OPDialect(csv.Dialect):
   "Definitions for reading information from Osuuspankki account statements"

   delimiter = ";"
   doublequote = False
   escapechar = None
   lineterminator = "\r\n"
   quotechar = '"'
   quoting = csv.QUOTE_MINIMAL
   skipinitialspace = None


# circa 2004
MAPPING_V1 = {
   "date":'Tap.pv', "amount":u'Määrä\xa0EUROA' ,"description":"Selitys",
   "account": "Saajan tilinumero",
   "reference":"Viite", "message":"Viesti"
}

# until at least 2011
MAPPING_V2 = {
   "date":u'Arvopäivä', "amount":u'Määrä\xa0EUROA',
   "description":u"Selitys", "account": u"Saajan tilinumero ja pankin BIC",
   "reference":u"Viite", "message":u"Viesti"
}


class OPReaderPlugin(CSVReaderPlugin):
   ""

   # encoding the statement file is in
   ENCODING = "1252"

   def __init__(self, linestream, dialect=OPDialect(), debug=False):
      CSVReaderPlugin.__init__(self, linestream, debug=debug, dialect=dialect)

      for mapping in [MAPPING_V1, MAPPING_V2]:
         mappedcolumns = [mapping[commonfield] for commonfield in FIELDS]
         logger.debug("trying: %s" % mappedcolumns)
         if set(mappedcolumns).issubset(set(self.fieldnames)):
            self._mapping = mapping
            self._columns = [col.encode(self.ENCODING) for col in mappedcolumns]

      if not self._mapping:
         raise Exception("plugin cannot handle rows: \n\n%s\n" % str(self.fieldnames))


   def format_record(self, row):
      data = [row[colname] for colname in self._columns]
      data[1] = decimal.Decimal(data[1].replace(',','.'))
      return tuple(data)


