from builtins import print
import requests
from pprint import pprint
import mysql.connector
import itertools
import json
import urllib.parse


# # api-endpoint
# URL = "https://buffalo-android.ifttt.com/grizzly/me/diy/services/" + service_identifier
#
# sending get request and saving the response as response object
token = 'c2436a9ef37d65910c1c05f6d137dbb7d79260d4' #  #1b004674987164ecf6ed87c30146aa90b4c21024
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"', 'Content-Type':'application/json; charset=utf-8'}
# r = requests.get(URL, headers=header)
# js_dict = r.json()

#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////


URL_for_trigger_data = "https://buffalo-android.ifttt.com/grizzly/me/feed/"
r = requests.get(URL_for_trigger_data, headers=header)
js_dict = r.json()
pprint(js_dict)

feed_items = js_dict['feed']

for feed in feed_items:
    id = feed['id']
    sql = "SELECT feed_id FROM ifttt_feed WHERE feed_id = " + "'" + str(id) + "'"
    mycursor.execute(sql)
    results_values = mycursor.fetchall()
    rc = mycursor.rowcount
    print(rc)

    if str(feed['item_type']) == 'system':
        continue
    else:
        if rc < 1:
            try:
                appletid = feed['common']['personal_recipe_id']
                sql = "SELECT trigger_service,action_service,applet_title, applet_desc, trigger_name,action_name,trigger_fields,action_fields, trigger_desc,action_desc FROM applets WHERE applet_id = " + "'" + str(
                    appletid) + "d'"
                mycursor.execute(sql)
                results_values = mycursor.fetchall()
                row_headers = [x[0] for x in mycursor.description]
                json_data = []
                for result in results_values:
                    json_data.append(dict(zip(row_headers, result)))
                applet_data = json.dumps(json_data)

                # ////////////////Add database record ////////////////////
                sql = """INSERT INTO ifttt_feed (feed_id, applet_id,applet_data,status, common_info,location, created_date, ife, full_feed_message) VALUES (%s,%s,%s,%s,%s, %s,%s, %s,  %s)"""
                val = (
                    id, str(appletid), str(applet_data), str(feed['item_type']), str(feed['common']),
                    str(feed['location']),
                    str(feed['created_at']), str(feed['ife']), str(feed))
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")
            except KeyError:
                print('Keyerror')









