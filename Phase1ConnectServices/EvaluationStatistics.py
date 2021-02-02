from builtins import  KeyError, property
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import WebDriverException, ElementNotInteractableException, \
    UnexpectedAlertPresentException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from pymongo import MongoClient
import os
import re
import timeit

############################################# DATABASE CONNECTION #####################################################
#client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client.get_database('services')
collection = db.get_collection('authdetails')
evalcollection = db.get_collection('evalauth')
catcollection = db.get_collection('categories')
newexappletstats = db.get_collection('userstats')
selectedservices = db.get_collection('selected')
newauthcollection = db.get_collection('evalauthdetails')
newnewauthcollection = db.get_collection('newevalauthdetails')
# for doc in newauthcollection.find({}):
#     newnewauthcollection.insert(doc)
#######################################################################################################################
can = []
maycan = []
paid = []
mobileapp = []
devicedata = []
clienterror = []
mobileappanddevicedata = []
query1 = evalcollection.find({'removed_service':False, 'linked':False})#, 'error':'no_credentials'})
print('false linked: ' +  str(query1.count()))
for rec in query1:
    #print(rec['service_idnetifier'])
    service = rec['service_idnetifier']
    for authc in collection.find({'service_idnetifier': service}):
        if service == authc['service_idnetifier']:
            try:
                ar = authc['register']
                if ar == 'can':
                    can.append(rec['service_idnetifier'])
                if ar == 'maycan':
                    maycan.append(rec['service_idnetifier'])
                if ar == 'paid':
                    paid.append(rec['service_idnetifier'])
                if ar == 'mobileapp':
                    mobileapp.append(rec['service_idnetifier'])
                if ar == 'devicedata':
                    devicedata.append(rec['service_idnetifier'])
                if ar == 'mobileappanddevicedata':
                    mobileappanddevicedata.append(rec['service_idnetifier'])
                if ar == 'clienterror':
                    clienterror.append(rec['service_idnetifier'])
            except KeyError:
                continue
                #print(service)
# print('can: ' + str(len(can)))
# print('maycan: ' + str(len(maycan)))
# print('paid: ' + str(len(paid)))
# print('mobileapp: ' + str(len(mobileapp)))
# print('devicedata: ' + str(len(devicedata)))
# print('mobileappanddevicedata: ' + str(len(mobileappanddevicedata)))
# print('clienterror: ' + str(len(clienterror)))
################################### TOTAL LINKED SERVICES AND UNIQUE CATEGORIES ########################################
query2 = evalcollection.find({'removed_service':False, 'linked':True})
# print(query2.count())
# uniquecategories = []
# for rec in query2:
#     #print(rec['category'])
#     uniquecategories.append(rec['category'])
# print(set(uniquecategories))
# print(len(set(uniquecategories)))
# ###################################################
# for rec in query2:
#     print(rec['service_idnetifier'])
################################################### LINKED TYPE ##############
def loginTypePrint(serviceList):
    credentials = []
    auto = []
    simple = []
    for serv in serviceList:
        query2 = evalcollection.find({'removed_service': False, 'linked': True, 'service_idnetifier':serv})
        for rec in query2:
            try:
                lt = rec['logintype']
                print(lt)
                # print(rec['logintype'])
                if lt == 'credentials':
                    credentials.append(rec['service_idnetifier'])
                if lt == 'auto':
                    auto.append(rec['service_idnetifier'])
                if lt == 'simple_connect':
                    simple.append(rec['service_idnetifier'])
            except KeyError:
                print(rec['service_idnetifier'])
                #print('-')
    print('credentails: ' + str(len(credentials)))
    print(credentials)
    print('auto: ' + str(len(auto)))
    print('simple: ' + str(len(simple)))


###################################################
def formTypePrint(serviceList):
    formForm = []
    googleForm = []
    noForm = []
    divFormTwoStep = []
    for serv in serviceList:
        query2 = evalcollection.find({'removed_service': False, 'linked': True, 'service_idnetifier':serv})

        for rec in query2:
            lt = rec['formtype']
            #print(rec['formtype'])
            if lt == 'formForm':
                formForm.append(rec['service_idnetifier'])
            if lt == 'googleForm':
                googleForm.append(rec['service_idnetifier'])
            if lt == 'divFormTwoStep':
                divFormTwoStep.append(rec['service_idnetifier'])
            if lt == 'noForm':
                noForm.append(rec['service_idnetifier'])
    print('formForm: ' + str(len(formForm)))
    print(formForm)
    print('googleForm: ' + str(len(googleForm)))
    print(noForm)
    print('noForm: ' + str(len(noForm)))
    print('divFormTwoStep: ' + str(len(divFormTwoStep)))
#####################################################
def usernameypePrint(serviceList):
    formForm = []
    googleForm = []
    noForm = []
    divFormTwoStep = []
    for serv in serviceList:
        query2 = evalcollection.find({'removed_service': False, 'linked': True, 'service_idnetifier':serv})

        for rec in query2:
            try:
                lt = rec['authtype']
                #print(rec['authtype'])
                # if lt == 'formForm':
                #     formForm.append(rec['service_idnetifier'])
                # if lt == 'googleForm':
                #     googleForm.append(rec['service_idnetifier'])
                # if lt == 'divFormTwoStep':
                #     divFormTwoStep.append(rec['service_idnetifier'])
                # if lt == 'noForm':
                #     noForm.append(rec['service_idnetifier'])
            except KeyError:
                #print('-')
                continue


    # print('formForm: ' + str(len(formForm)))
    # print('googleForm: ' + str(len(googleForm)))
    # print('noForm: ' + str(len(noForm)))
    # print('divFormTwoStep: ' + str(len(divFormTwoStep)))


###################################################
# for rec in query2:
#     if rec['logintype'] == 'credentials':
#         try:
#             lt = rec['authbtntagattr']
#             print(lt)
#         except KeyError:
#             print('######## '+ rec['service_idnetifier'])
########################################################################################################################
#max 77
# query3 = catcollection.find({'linkedsize':{'$gte': 0}}) # 	Matches values that are greater than or equal to a specified value.
# print(query3.count())
# query30 = catcollection.find({'linkedsize':0}) # 	Matches values that are greater than or equal to a specified value.
# print(query30.count())
#################################################
# onetofifteen = []
# sizteentothirty = []
# thirtyonetofourtyfive = []
# fourtysiztosixty = []
# sixtytoseventyfiveormore = []
# for rec in catcollection.find({}):
#     size = rec['size']
#     servce = rec['category']
#     if size>=0 and size <= 15:
#         onetofifteen.append(servce)
#     elif size>=16 and size <= 30:
#         sizteentothirty.append(servce)
#     elif size>=31 and size <= 45:
#         thirtyonetofourtyfive.append(servce)
#     elif size>=46 and size <= 60:
#         fourtysiztosixty.append(servce)
#     elif size>=61:
#         sixtytoseventyfiveormore.append(servce)
# print('results: ')
# print('onetofifteen: ' + str(len(onetofifteen)))
# print('sizteentothirty: ' + str(len(sizteentothirty)))
# print('thirtyonetofourtyfive: ' + str(len(thirtyonetofourtyfive)))
# print('fourtysiztosixty: ' + str(len(fourtysiztosixty)))
# print('sixtytoseventyfiveormore: ' + str(len(sixtytoseventyfiveormore)))
#################################################
############################################ update remainning  in CATEGORY dataset ####################################
query4 = evalcollection.find({'removed_service':False, 'linked':False})
# query41 = catcollection.find({})
# unlinkedservics = []
# for res in query4:
#     servinres = res['service_idnetifier']
#     unlinkedservics.append(servinres)
#
# for rec in query41:
#     category = rec['category']
#     allservics = rec['services']
#     unlinkedincategory = []
#     for s in allservics:
#         if s in unlinkedservics:
#             unlinkedincategory.append(s)
#
#     catcollection.find_one_and_update({'category': category}, {"$set": {"remaining": unlinkedincategory}}, upsert=True)
########################################################################################################################
########################################## filter the services based on applet installations ###########################
query5 = newexappletstats.find({'installations':{'$gte': 1000}})
print('result size:  ' +  str(query5.count()))
# serviceset = []
# actionserviceset  = []
# for res5 in query5:
#     ts = res5['trigger_service']
#     ass = res5['action_service']
#     serviceset.append(res5['trigger_service'])
#     actionserviceset.append(res5['action_service'])
#     #################################################
#     for res6 in catcollection.find({}):
#         categ = res6['category']
#         servclist = res6['services']
#         if ts in servclist:
#             cts = 0
#             for res7 in selectedservices.find({"service_idnetifier": ts}):
#                 cts = cts + 1
#                 if res5['installations'] > res7['installations']:
#                     selectedservices.find_one_and_update({"service_idnetifier": ts}, {"$set": {'category': categ, 'type': 'trigger','installations':res5['installations']}}, upsert=True)
#             if cts == 0 :
#                 selectedservices.find_one_and_update({"service_idnetifier": ts}, {
#                     "$set": {'category': categ, 'type': 'trigger', 'installations': res5['installations']}},
#                                                      upsert=True)
#         if ass in servclist:
#             cass = 0
#             for res7 in selectedservices.find({"service_idnetifier": ass}):
#                 cass = cass + 1
#                 if res5['installations'] > res7['installations']:
#                     selectedservices.find_one_and_update({"service_idnetifier": ass}, {"$set": {'category': categ, 'type': 'action','installations':res5['installations']}}, upsert=True)
#             if cass == 0:
#                 selectedservices.find_one_and_update({"service_idnetifier": ass}, {
#                     "$set": {'category': categ, 'type': 'action', 'installations': res5['installations']}}, upsert=True)
##################################################
# print(set(serviceset))
# print(len(set(serviceset)))
# print('###########################')
# print(set(actionserviceset))
# print(len(set(actionserviceset)))
# print(len(set(actionserviceset + serviceset)))
#######################################################################################################################
#######################################check which categories cover ###################################################
# alltracservice = set(actionserviceset + serviceset)
# print('alltracservice size:  ' + str(len(set(alltracservice))))
# query6 = catcollection.find({})
# includedcat = []
# for res6 in query6:
#     categ = res6['category']
#     servclist = res6['services']
#     for sl in servclist:
#         if sl in alltracservice:
#             includedcat.append(categ)
# print('###########################')
# print(set(includedcat))
# print(len(set(includedcat)))
print('#############################################################################################################')
#######################################################################################################################
# query7 = selectedservices.find({})
# connected = []
# for res77 in query7:
#     #print(res77['installations'])
#     s = res77['service_idnetifier']
#     eq = evalcollection.find({'service_idnetifier': res77['service_idnetifier']})
#     for eqr in eq:
#         selectedservices.find_one_and_update({"service_idnetifier": s}, { "$set": {'linked':eqr['linked']}}, upsert=True)
#         if not eqr['linked']:
#             areq = collection.find({'service_idnetifier': res77['service_idnetifier']})
#             for are in areq:
#                 try:
#                     selectedservices.find_one_and_update({"service_idnetifier": s},
#                                                          {"$set": {'register': are['register']}}, upsert=True)
#                     selectedservices.find_one_and_update({"service_idnetifier": s}, {"$set": {'reason': are['reason']}},
#                                                          upsert=True)
#                 except KeyError:
#                     selectedservices.find_one_and_update({"service_idnetifier": s},
#                                                          {"$set": {'register': 'not tried yet'}}, upsert=True)
#
#         else:
#             connected.append(s)
# print(set(connected))
# print(len(set(connected)))
#######################################check selected servies are connected ############################################
########################################################################################################################
query7 = selectedservices.find({'linked': True})
connected = []
for res77 in query7:

    try:
        sss = res77['service_idnetifier']
        connected.append(sss)
        # for rec770 in evalcollection.find({'service_idnetifier': sss}):
        #     print(rec770['time'])
        ###
        # for rec770 in collection.find({'service_idnetifier': sss}):
        #     if rec770['reason'] == '':
        #         connected.append(sss)
        ###
        for rec771 in newnewauthcollection.find({'service_idnetifier': sss}):
            print(rec771['average_time_to_scrape_with_login'])
        #connected.append(res77['service_idnetifier'])#category service_idnetifier  reason  register type linked installations
    except KeyError:
        print('- ')
        #connected.append(sss)
        continue

# for xx in set(connected):
#     print(xx)
print(connected)
print(len(connected))
print('###################################################')
#loginTypePrint(connected)
print('###################################################')
loginTypePrint(connected)
print('###################################################')
#usernameypePrint(connected)
print('###################################################')
### SELECTED WITH NO POSSIBLE REASONS: 84
#['withings', 'fitbit', 'strava', 'ios_health', 'google_sheets', 'if_notifications', 'google_calendar', 'instagram', 'twitter', 'google_drive', 'dropbox', 'wordpress', 'flickr', 'blogger', 'onedrive', 'android_device', 'adafruit', 'location', 'do_button', 'android_phone', 'android_messages', 'voip_calls', 'optus_smart_living', 'feed', 'instapaper', 'pocket', 'nytimes', 'date_and_time', 'slack', 'space', 'do_camera', 'ifttt', 'todoist', 'hacker_news', 'app_store', 'reddit', 'ios_photos', 'pew_research', 'time', 'who', 'bea', 'ios_reading_list', 'rachio_iro', 'facebook', 'foursquare', 'android_wear', 'android_battery', 'android_photos', 'soundcloud', 'weebly', 'maker_webhooks', 'brainyquote', 'qualitytime', 'square', 'usda', 'grants', 'npr', 'wikipedia', 'ios_reminders', 'ios_contacts', 'google_docs', 'google_contacts', 'weather', 'toodledo', 'finance', 'foxnews', 'nsf', 'propublica', 'giphy', 'diigo', 'musixmatch', 'evernote', 'email', 'gmail', 'spotify', 'sec', 'do_note', 'medium', 'epa', 'loc', 'onenote', 'tesco', 'dos', 'songkick']


googleformlist = ['google_sheets', 'google_calendar', 'google_drive', 'blogger', 'soundcloud', 'google_docs', 'google_contacts', 'evernote', 'gmail','bitly']
formformlist = ['withings', 'fitbit', 'strava',  'instagram', 'twitter', 'dropbox',  'flickr',    'instapaper',  'slack', 'space',  'todoist', 'reddit', 'ios_photos', 'ios_reading_list', 'facebook', 'foursquare', 'android_wear',  'qualitytime', 'toodledo', 'diigo', 'musixmatch', 'spotify', 'tesco']
noformlist  = ['location', 'optus_smart_living', 'nytimes', 'ifttt', 'hacker_news', 'app_store', 'pew_research', 'time', 'who', 'bea', 'weebly', 'maker_webhooks', 'brainyquote', 'usda', 'grants', 'npr', 'wikipedia', 'weather', 'finance', 'foxnews', 'nsf', 'propublica', 'giphy', 'email', 'sec', 'medium', 'epa', 'loc', 'dos', 'songkick']
