#### This script should enable the applets that are non-conflicting.
#### For example, the applet choose a TS, trigger and an AS , action
#### The applets enabled should be only the particular trigger from the selected TS
#### Every other appplet should be diabled to avoid chain applet executions and
import requests
import time
import timeit
from threading import Thread
import time
from pprint import pprint
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
threads = []
active_trigger = ''
active_trigger_service = ''
results = {}
trigger_fields_of_active_trigger = ''
action_details_list = []
track_action_services = []
#############################################################################################
# ENABLE A SET OF APPLETS FOR A CHOSEN TRIGGER AND TRIGGER SERVICE
#############################################################################################
###########################################################################
# c2436a9ef37d65910c1c05f6d137dbb7d79260d4 wijitha.mahadewa@gmail.com
# 0dfb5edac5e2201a9ece7b3908dcfd04d57522b6 happybee9494@gmail.com
# 1b004674987164ecf6ed87c30146aa90b4c21024
###########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
dbClient = client['applets']
appletcollection = dbClient.get_collection('appletcollection')
all_applet_details = appletcollection.find({})
############################################# LOGIN TO IFTTT # #########################################################
options = Options()
options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
serv = Service(r'/root/Tools/Firefox/geckodriver')
browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
browser.get('https://ifttt.com/login?wp_=1')

username = browser.find_element_by_id("user_username")
password = browser.find_element_by_id("user_password")
username.send_keys("happybee9494@gmail.com")
password.send_keys("happyBEE@94")
browser.find_element_by_name("commit").click()
print('Logged In')
########################################################################################################################
def genURLPart(applet_id,applet_title):
  clean_applet_title = applet_title.strip().lower()
  clean_applet_title = clean_applet_title.replace('@','-').replace(',','').replace('.','-').replace("'","-")
  clean_applet_title = clean_applet_title.replace(' ', '-')
  clean_applet_title = clean_applet_title.replace('--', '-')
  genURL = str(applet_id)+ "-"+clean_applet_title
  # print(genURL)
  return genURL

def toggleAppletConnection(applet_id,applet_title):
  print('toggleAppletConnection')
  applet_connect_url = genURLPart(applet_id, applet_title)
  browser.get('https://ifttt.com/applets/' + str(applet_connect_url))
  time.sleep(10)
  element = WebDriverWait(browser, 100).until(EC.element_to_be_clickable((By.CLASS_NAME, "connect_button__connect-button__3_96C")))#.send_keys(Keys.RETURN)
  element.click()
  time.sleep(10)
  ## TODO: can check if a text exist on the resulting page to confirm
  return

def toggleApplet(active_trigger,active_trigger_service,appletData,track_action_services,action_details_list,trigger_fields_of_active_trigger,attempt):
  action_details = {}
  if (appletData['trigger'].strip() == active_trigger.strip()) and (
          appletData['trigger_service'].strip() == active_trigger_service.strip()):
    print('Enabling realted applet ... ')
    trigger_fields_of_active_trigger = appletData['trigger_fields']
    action_details['action_service'] = appletData['action_service']
    action_details['action'] = appletData['action']
    action_details['action_desc'] = appletData['action_desc']
    action_details['action_fields'] = appletData['action_fields']
    track_action_services.append(appletData['action_service'])
    # print(track_action_services)
    # print(track_action_services.count(appletData['action_service']))
    if track_action_services.count(appletData['action_service']) == attempt:
      ##################################################################################################################
      ########## If applet already enabled contine, otherwise toggle and update database ###############################
      action_details_list.append(action_details)
      if appletData['eanbled']:
        return track_action_services, action_details_list, trigger_fields_of_active_trigger
      else:
        toggleAppletConnection(appletData['applet_id'], appletData['applet_title'])
        newStatus = True
    else:
      print('Diableing not realted applet ...  1')
      ##################################################################################################################
      ########## If applet already disabled  contine, otherwise toggle and update database #############################
      if appletData['eanbled']:
        toggleAppletConnection(appletData['applet_id'], appletData['applet_title'])
        newStatus = False
      else:
        return track_action_services, action_details_list, trigger_fields_of_active_trigger

  else:
    print('Diableing not realted applet ...  2')
    ##################################################################################################################
    ########## If applet already disabled  contine, otherwise toggle and update database #############################
    if not appletData['eanbled']:
      toggleAppletConnection(appletData['applet_id'], appletData['applet_title'])
      newStatus = False
    else:
      print('not enabled')
      return track_action_services, action_details_list, trigger_fields_of_active_trigger

  doc = {
    'applet_id': appletData['applet_id'],
    'applet_title': appletData['applet_title'],
    'applet_desc': appletData['applet_desc'],
    'trigger_service': appletData['trigger_service'],
    'trigger': appletData['trigger'],
    'trigger_desc': appletData['trigger_desc'],
    'trigger_fields': appletData['trigger_fields'],
    'action_service': appletData['action_service'],
    'action': appletData['action'],
    'action_desc': appletData['action_desc'],
    'action_fields': appletData['action_fields'],
    'eanbled': appletData['eanbled']
  }
  updateddoc = {
    'applet_id': appletData['applet_id'],
    'applet_title': appletData['applet_title'],
    'applet_desc': appletData['applet_desc'],
    'trigger_service': appletData['trigger_service'],
    'trigger': appletData['trigger'],
    'trigger_desc': appletData['trigger_desc'],
    'trigger_fields': appletData['trigger_fields'],
    'action_service': appletData['action_service'],
    'action': appletData['action'],
    'action_desc': appletData['action_desc'],
    'action_fields': appletData['action_fields'],
    'eanbled': newStatus
  }
  appletcollection.update(doc, updateddoc, upsert=True)
  print('db updated')
  return track_action_services,action_details_list,trigger_fields_of_active_trigger

def enableOnlyRequiredApplets(trigger, trigger_service, attempt):
  s1 = timeit.default_timer()
  active_trigger = trigger
  active_trigger_service = trigger_service
  i = 0
  for appletData in all_applet_details:
    i = i + 1
    if i <= 2000:
      continue
    if i%20 == 0:
      time.sleep(25)

    print('came here ' + str(i))
    process = Thread(target=toggleApplet,args=[active_trigger, active_trigger_service, appletData, track_action_services, action_details_list,trigger_fields_of_active_trigger,
                 attempt])
    process.start()
    threads.append(process)
    e1 = timeit.default_timer()
    print('Time for diff library function= ' + str(e1 - s1))

  for process in threads:
    process.join()

  results['active_trigger'] = active_trigger
  results['active_trigger_service'] = active_trigger_service
  results['trigger_fields_of_active_trigger'] = trigger_fields_of_active_trigger
  results['action_details_list'] = action_details_list
  print('final results: ')
  print(results)
  return results





