import xlrd
from pymongo import MongoClient

# Workbook location
loc = ('.../FIELD_LABEL.xls')

# Open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
print('No of records: '+str(sheet.nrows))
###########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
collection = db.get_collection('clusterlabeldetails')
collection.remove({})
#######################

###########################################################################
#  value(row no, column no)
for i in range(sheet.nrows):
    if i == 0:
        continue
    textField = sheet.cell_value(i,1)
    cleanedField = sheet.cell_value(i,2)
    label = sheet.cell_value(i,3)

    doc = {
        'textField': textField,
        'cleanedField': cleanedField,
        'label': label,
    }
    collection.update(doc, doc, upsert=True)





