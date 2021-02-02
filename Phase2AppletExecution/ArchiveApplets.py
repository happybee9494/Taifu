import requests
from pprint import pprint
import itertools
import json
import urllib.parse
from pymongo import MongoClient
from  simplejson.errors import JSONDecodeError
import timeit
from threading import Thread
import time
###########################################################################
#token = '0dfb5edac5e2201a9ece7b3908dcfd04d57522b6' #  #1b004674987164ecf6ed87c30146aa90b4c21024 #0dfb5edac5e2201a9ece7b3908dcfd04d57522b6 #c2436a9ef37d65910c1c05f6d137dbb7d79260d4
#remember_token=b9c969f8fc4d28c3207ef1b3838c75233e8246c3
token = 'b9c969f8fc4d28c3207ef1b3838c75233e8246c3'
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"', 'Content-Type':'application/json; charset=utf-8'}
###########################################################################
# 1) facebook - New photo post by you with hashtag
# 2) instagram - Any new photo by you
# 3) foursquare - New check-in with photo (applets failed before execution of the trigger)
# 4) android_photos - Any new photo
# 5) twitter - New tweet by you
# 6) flickr - Any new public photo
current_trigger_service = 'android_photos'
current_trigger = 'Any new public photo' #'New status message by you'
applet_folder_name = 'applets_'+current_trigger_service+'_1'
###################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
eventDatacollection = db.get_collection('serviceconfigdetails')
all_event_details = eventDatacollection.find({})
################################################################
authDatacollection = db.get_collection('monitorauthdetails')
all_auth_details = authDatacollection.find({})
################################################################
labelcollection = db.get_collection('clusterlabeldetails')
all_label_details = labelcollection.find({})
################################################################
dbClient = client['evalapplets']
appletcollection = dbClient.get_collection(applet_folder_name)
errorcollection = dbClient.get_collection(applet_folder_name+'_errors')


###############################################################
#################################################################


graph_url = 'https://ifttt.com/api/v3/graph'
for applet in appletcollection.find({}):
    appletid = applet['applet_id']
    disable_requst_body = {
        "query": "        mutation {\n            normalizedAppletDisable(input: {\n                applet_id: \""+appletid+"\"\n            }) {\n  "
                 "normalized_applet {\n   id\n        name\n        description\n        brand_color\n        monochrome_icon_url\n        author\n        "
                 "status\n        installs_count\n        push_enabled\n        type\n        created_at\n        last_run\n        run_count\n        speed\n        "
                 "config_type\n        by_service_owner\n        background_images {\n            background_image_url_1x\n            background_image_url_2x\n       "
                 " }\n        configurations {\n            title\nslug\ndescription\nicon_url\nrequired\nlive_configurations {\n    id\n    disabled\n}\n        "
                 "}\n        applet_feedback_by_user\n        can_push_enable\n        published\n        archived\n        author_tier\n        pro_features\n        "
                 "service_name\n        channels {\n            id\nmodule_name\nshort_name\nname\ndescription_html\nbrand_color\nmonochrome_image_url\nlrg_monochrome_image_url"
                 "\nis_hidden\nconnected\nrequires_user_authentication\ncall_to_action {\n    text\n    link\n}\norganization {\n    tier\n}\n        }\n          "
                 "underlying_applet {\n            live_applet {\n                live_applet_triggers {\n     statement_id\n    }\n }\n          }\n        }\n        "
                 "errors {\n          attribute\n          message\n        }\n            }\n        }"}

    prev_r = requests.post(graph_url, data=json.dumps(disable_requst_body), headers=post_header)
    js_dict_prev = prev_r.json()
    pprint(js_dict_prev)



enable_request_body={"query":"        mutation {\n   normalizedAppletEnable(input:{\n applet_id: \"JT2WXgtM\",\n    name: \"If New tweet by @HappyBe58516521 including retweets, then Add a task\",\n            "
                             "push_enabled: false,\n            dynamic_applet_configuration: false,\n    "
                             "stored_fields: \"{\\\"\\/triggers\\/twitter.new_tweet_by_you\\\":{\\\"include_tweets\\\":[\\\"retweets\\\"]},"
                             "\\\"\\/actions\\/toodledo.add-task\\/0\\\":{\\\"title\\\":\\\"{{UserName}} {{CreatedAt}}\\\",\\\"note\\\":"
                             "\\\"@{{UserName}} : {{Text}}<br><br>via Twitter {{LinkToTweet}}<br><br>{{CreatedAt}}\\\",\\\"tag\\\":"
                             "\\\"IFTTT, Twitter\\\",\\\"priority\\\":\\\"3\\\",\\\"folder\\\":\\\"0\\\"}}\",\n           "
                             " metadata: \"{}\",\n            allow_empty: false\n          }) {\n    normalized_applet {\n    id\n        name\n    description\n  brand_color\n        "
                             "monochrome_icon_url\n        author\n        status\n        installs_count\n        push_enabled\n        type\n        created_at\n        last_run\n"
                             "        run_count\n        speed\n        config_type\n        by_service_owner\n        background_images {\n            background_image_url_1x\n "
                             "           background_image_url_2x\n        }\n        configurations {\n            title\nslug\ndescription\nicon_url\nrequired\n"
                             "live_configurations {\n    id\n    disabled\n}\n        }\n        applet_feedback_by_user\n        can_push_enable\n        published\n        "
                             "archived\n        author_tier\n        pro_features\n        service_name\n        channels {\n id\nmodule_name\nshort_name\nname\ndescription_html\n"
                             "brand_color\nmonochrome_image_url\nlrg_monochrome_image_url\nis_hidden\nconnected\nrequires_user_authentication\ncall_to_action {\n    text\n    link\n}"
                             "\norganization {\n    tier\n}\n        }\n          underlying_applet {\n            live_applet {\n                live_applet_triggers {\n "
                             "statement_id\n                }\n            }\n          }\n        }\n        errors {\n          attribute\n          message\n        }\n            "
                             "user_token\n          }\n        }"}

