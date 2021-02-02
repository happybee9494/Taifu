from builtins import print

import mysql.connector

#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////

sql = "SELECT * FROM existing_applets_run1"
mycursor.execute(sql)
results_values = mycursor.fetchall()
rc = mycursor.rowcount
print(rc)

for values in results_values:
    if 'Auth Required' in values[5] and 'No Auth Required' not in values[5]:
        print()




