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
###################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
pcollection = db.get_collection('defaultprivacy')
eventDatacollection = db.get_collection('serviceconfigdetails2')

current_services = ['bitly','facebook','google_contacts','instapaper','slack', 'date_and_time','maker_webhooks','twitter','youtube','wordpress','withings','weebly',
               'toodledo','todoist','tesco','strava','medium','musixmatch','pocket','reddit','google_docs','google_drive',
               'google_sheets','instagram','fitbit','flickr','gmail', 'email','google_calendar','blogger','dropbox','diigo','evernote',
                'ios_health', 'if_notifications','android_device', 'location','do_button', 'android_phone','android_messages', 'voip_calls','line', 'do_camera',
                'ios_photos', 'ios_reading_list','foursquare', 'android_battery','android_photos', 'qualitytime','ios_reminders', 'ios_contacts','do_note']


# for serv in current_services:
#     servinfor = {}
#     triggers = []
#     actions = []
#     for st in eventDatacollection.find({}):
#         servicename = st['module_name'].split('.')[0]
#         event = st['module_name'].split('.')[1]
#         eventtype = st['type']
#         if serv == servicename:
#             if eventtype == 'trigger':
#                 triggers.append(event)
#             if eventtype == 'action':
#                 actions.append(event)
#     # servinfor['service'] = serv
#     # servinfor['triggers'] = len(set(triggers))
#     # servinfor['triggers_list'] = triggers
#     # servinfor['actions'] = len(set(actions))
#     # servinfor['actions_list'] = actions
#     pcollection.update({'service_idnetifier': serv},
#                       {'$set': {'trigger_size': len(set(triggers)), 'action_size': len(set(actions))}}, upsert=True)

##############################################################################
# pcollection.update({'service_idnetifier': 'evernote'},
#                   {'$set': {'has_privacy_configs': True, 'default_privacy': 'private'}}, upsert=True)
#
# pcollection.update({'service_idnetifier': 'diigo'},
#                   {'$set': {'has_privacy_configs': True, 'default_privacy': 'public'}}, upsert=True)
#
# pcollection.update({'service_idnetifier': 'qualitytime'},
#                   {'$set': {'has_privacy_configs': False, 'default_privacy': 'private'}}, upsert=True)
#
# pcollection.update({'service_idnetifier': 'reddit'},
#                   {'$set': {'has_privacy_configs': False, 'default_privacy': 'public'}}, upsert=True)

for cs in current_services:
    for c in db.get_collection('categories').find({}):
        category = c['category']
        cservices = c['services']
        if cs in cservices:
            pcollection.update({'service_idnetifier': cs},
                               {'$set': {'category': category}}, upsert=True)

allcat = []
for c in db.get_collection('defaultprivacy').find({}):
    item = c['category']
    allcat.append(item)

# allcat = list(set(allcat))
# print(allcat)
allcat = ['photo_&_video', 'blogging', 'cloud_storage', 'notes', 'social_networks', 'notifications', 'task_management_&_to-dos', 'shopping', 'location', 'mobile_devices_&_accessories', 'contacts', 'time_management_&_tracking', 'developer_tools', 'calendars_&_scheduling', 'music', 'communication', 'email', 'health_&_fitness', 'bookmarking']

for ac in allcat:
    allsizea = 0
    for rec in  db.get_collection('defaultprivacy').find({'category':ac, 'has_privacy_configs': False, 'default_privacy': 'public'  }):
        acts = rec['action_size']
        trs = rec['trigger_size']
        allsizea = allsizea + acts + trs

    #print(x.count())
    #print(allsizea)

