import xlrd
from pymongo import MongoClient

# Workbook location
loc = (.../SERVICE_CONFIGURATION details.xls')

# Open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
print('No of records: '+str(sheet.nrows))
###########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
collection = db.get_collection('serviceconfigdetails')
collection.remove({})

###########################################################################
#  value(row no, column no)
for i in range(sheet.nrows):
    if i == 0:
        continue
    serviceID = sheet.cell_value(i,1)
    eventType = sheet.cell_value(i,2)
    eventName = sheet.cell_value(i,3)
    eventDesc = sheet.cell_value(i,4)
    doc = {
        'service_idnetifier': serviceID,
        'eventType': eventType,
        'eventName': eventName,
        'eventDesc': eventDesc
    }
    collection.update(doc, doc, upsert=True)





