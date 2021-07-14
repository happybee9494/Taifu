import requests
from pprint import pprint
import itertools
import json
import urllib.parse
from pymongo import MongoClient
import timeit
import time
from Taifu.BehaviorMonitoring_NoiseTemplates.tatester.tatester.spiders.MonitoringJavaScriptAction import monitoring
URL_for_apple_execution_history = "https://buffalo-android.ifttt.com/grizzly/me/feed/"
token = 'b9c969f8fc4d28c3207ef1b3838c75233e8246c3'#'0dfb5edac5e2201a9ece7b3908dcfd04d57522b6' #  #1b004674987164ecf6ed87c30146aa90b4c21024 #0dfb5edac5e2201a9ece7b3908dcfd04d57522b6 #c2436a9ef37d65910c1c05f6d137dbb7d79260d4
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"', 'Content-Type':'application/json; charset=utf-8'}
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
mutation = 'video'
current_trigger_service = 'twitter'
applet_folder_name = 'applets_'+current_trigger_service+'_1'
###############################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
###############################################
db = client[applet_folder_name]
scollection = db.get_collection('succeed'+mutation)
fcollection = db.get_collection('failed'+mutation)
###############################################
dbClient = client['evalapplets']
appletcollection = dbClient.get_collection(applet_folder_name)
###############################################
# client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
# db = client.get_database('services')
# collection = db.get_collection('authdetails')
# all_auth_details = collection.find({})
# all_credentials_in_db = {}
########################################################################################################################
def updateAppletExecutionHistory(feed, successCol, failedCol):
    succeed = []
    for item in feed:
        results = {}
        context_text = None
        applet_result = None
        applet_id = None
        trigger_data = None
        applet_status_data = None
        location = None
        for ik, iv in item.items():
            if ik == 'grizzly':
                trigger_data = iv
                for ak, av in iv.items():
                    if ak == 'applet_id':
                        applet_id = av
                    if ak == 'content_text':
                        context_text = av
            if ik == 'item_type':
                applet_result = iv
            if ik == 'location':
                location = iv
            if ik == 'ife':
                applet_status_data = iv

        results['applet_id'] = applet_id
        results['context_text'] = context_text
        results['trigger_data'] = trigger_data
        results['applet_status_data'] = applet_status_data
        results['location'] = location
        #print(applet_id)
        applet_belongs_to_current_triggerservice = appletcollection.find({'applet_id': applet_id})
        #print(applet_belongs_to_current_triggerservice)
        for aapp in applet_belongs_to_current_triggerservice:
            print('related success execution found ^-^ !!!')
            if applet_result == 'success':
                data = successCol.find({'applet_id': applet_id, 'context_text': context_text})
                if data.count() > 0:
                    for record in data:
                        if not record['monitored']:
                            results['monitored'] = False
                            results['analyzed'] = False  # scrapped?
                            results['action_data'] = {}
                            results['applet_knowledge'] = {}
                            succeed.append(applet_id)
                            successCol.update(record, results, upsert=True)
                else:
                    results['monitored'] = False
                    results['analyzed'] = False  # scrapped?
                    results['action_data'] = {}
                    results['applet_knowledge'] = {}
                    succeed.append(applet_id)
                    successCol.update(results, results, upsert=True)
            elif applet_result == 'error':
                print('related failed execution found')
                try:
                    failedCol.insert_one(results)
                except Exception:
                    pass

    return succeed


successList = ['diigo', 'google_docs', 'cisco_spark', 'fitbit', 'narro', 'google_calendar', 'wordpress', 'pocket', 'email', 'particle', 'strava', 'google_sheets', 'twitter']

def monitorfeed(actions_to_monitor):
    for action in actions_to_monitor:
        print(action)
        action_service = action['action_service']
        action_name = action['action']
        # action_desc = action['action_desc']
        appletID = action['applet']

        default_start_no = 1
        default_end_no = 2
        action_services_to_monitor = [action_service]
        # monitoring(default_start_no, default_end_no, action_services_to_monitor)
        print('monitoring done: ' + str(action_service))

        ######## after monitored update iftttmonitor db
        data = scollection.find({'applet_id': appletID})
        print(data)
        if data.count() > 0:
            for record in data:
                print('here')
                # oldrecord = record
                # record['monitored'] = True
                ### THIS STEP SHOULD BE SUCCESSFULL FOR THE ANALYSEDMONITORED PAGES TO BE CONINTIED...
                scollection.update({'_id': record['_id']},
                                   {'$set': {"monitored": True, 'action_data': {'action_service': action_service}}})

############
# first crawling of moniotring just after the
############
####################################################################################
####################################################################################
####################################################################################
for i in range(10000):
    r = requests.get(URL_for_apple_execution_history, headers=header)
    js_dict = r.json()
    feed = js_dict['feed']
    #pprint(feed)
    appletsToMonitor = updateAppletExecutionHistory(feed, scollection, fcollection)
    time.sleep(2)
    ## 1)
    ##################################################################################
    actions_to_monitor = []
    #### Next find the action services to monitor by quering the applets database
    for appletID in appletsToMonitor:
        applet_details = appletcollection.find({'applet_id': appletID})
        for adetaisl in applet_details:
            adata = {}
            adata['applet'] = appletID
            adata['action_service'] = adetaisl['action_service']
            adata['action'] = adetaisl['action']
            # adata['action_desc'] = adetaisl['action_desc']
            actions_to_monitor.append(adata)
    if actions_to_monitor:
        print(actions_to_monitor)
    else:
        print(str(i) +' no related applets found...yet')
    ##################################################################################
