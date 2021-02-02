from builtins import print, KeyError
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from pymongo import MongoClient
import timeit
from threading import Thread
import time
import os
##########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
dbClient = client['applets']
appletcollection = dbClient.get_collection('appletcollection')
all_applet_details = appletcollection.find({})

# ##########################################################################
options = Options()
options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
serv = Service(r'/root/Tools/Firefox/geckodriver')
#
current_action_servicess = ['bitly','facebook','google_contacts','instapaper','slack','twitter','youtube','wordpress','withings','weebly',
               'toodledo','todoist','tesco','strava','medium','musixmatch','pocket','reddit','google_docs','google_drive',
               'google_sheets','instagram','fitbit','flickr','gmail','google_calendar','blogger','dropbox','diigo','evernote']
##########################################################################################################################
for service_identifier in current_action_servicess:
    foldername = 'scraped_monitoring/evalscraped_' + service_identifier  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    baseFolderName = './' + foldername + '/'
    BASE_FOLDERNAME = baseFolderName
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        for htmlf in htmlfiles:
            page_split = htmlf.split('_')
            if page_split[1] == '0.html' and len(htmlfiles) >1 :
                os.remove(BASE_FOLDERNAME + '/'+htmlf)

    except OSError as ex:
        print(ex)
        pass
##########################################################################################################################
for service_identifier in current_action_servicess:
    foldername = 'scraped_monitoring/evalscraped_' + service_identifier  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    baseFolderName = './' + foldername + '/'
    BASE_FOLDERNAME = baseFolderName
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        for htmlf in htmlfiles:
            page_split = htmlf.split('_')
            if page_split[1] == '1.html':
                os.rename(BASE_FOLDERNAME + htmlf, BASE_FOLDERNAME +  page_split[0]+'_0.html')
    except OSError as ex:
        print(ex)
        pass

##########################################################################################################################
for service_identifier in current_action_servicess:
    foldername = 'scraped_monitoring/screens/evalscraped_' + service_identifier  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    baseFolderName = './' + foldername + '/'
    BASE_FOLDERNAME = baseFolderName
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".png")]
        for htmlf in htmlfiles:
            page_split = htmlf.split('_')
            if page_split[1] == '0.png' and len(htmlfiles) >1 :
                os.remove(BASE_FOLDERNAME + '/'+htmlf)
    except OSError as ex:
        print(ex)
        pass
##########################################################################################################################
for service_identifier in current_action_servicess:
    foldername = 'scraped_monitoring/screens/evalscraped_' + service_identifier  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    baseFolderName = './' + foldername + '/'
    BASE_FOLDERNAME = baseFolderName
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".png")]
        for htmlf in htmlfiles:
            page_split = htmlf.split('_')
            if page_split[1] == '1.png':
                os.rename(BASE_FOLDERNAME + htmlf,BASE_FOLDERNAME + page_split[0]+'_0.png')
    except OSError as ex:
        print(ex)
        pass




