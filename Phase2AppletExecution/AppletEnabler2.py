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
token = '0dfb5edac5e2201a9ece7b3908dcfd04d57522b6'  # #1b004674987164ecf6ed87c30146aa90b4c21024
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"',
               'Content-Type': 'application/json; charset=utf-8'}
###########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
dbClient = client['applets']
appletcollection = dbClient.get_collection('appletcollection')
all_applet_details = appletcollection.find({})
############################################# LOGIN TO IFTTT # #########################################################
########################################################################################################################
def disableApplet(applet_id):
  URL_for_post_status = 'https://ifttt.com/api/v3/graph'
  disablebody = {
    "query": 'mutation {\n          normalizedAppletDisable(input:{\n            applet_id: \"'+ str(applet_id)+'\",\n            name: \"\",\n            push_enabled: false,\n            dynamic_applet_configuration: false,\n            stored_fields: \"{}\",\n            metadata: \"{}\"\n          }) {\n            normalized_applet {\n                      id\nname\ndescription\nbrand_color\nmonochrome_icon_url\nauthor\nstatus\ninstalls_count\npush_enabled\ntype\ncreated_at\nlast_run\nrun_count\nspeed\nconfig_type\nby_service_owner\nbackground_images {\n    background_image_url_1x\n    background_image_url_2x\n}\nconfigurations {\n    title\n    icon_url\n}\napplet_feedback_by_user\ncan_push_enable\n        service_name\n        channels {\n            id\nmodule_name\nshort_name\nname\ndescription_html\nbrand_color\nmonochrome_image_url\nlrg_monochrome_image_url\nis_hidden\nconnected\nrequires_user_authentication\ncall_to_action {\n    text\n    link\n}\norganization {\n    tier\n}\n        }\n              underlying_applet {\n                live_applet {\n                    live_applet_triggers {\n                        statement_id\n                    }\n                }\n              }\n            }\n            user_token\n            errors {\n              attribute\n              message\n            }\n          }\n        }'}
  r2 = requests.post(URL_for_post_status, headers=post_header, json=disablebody)
  print(r2)
  return
def enableApplet(applet_id):
  URL_for_post_status = 'https://ifttt.com/api/v3/graph'
  enablebody = {
    "query": 'mutation {\n          normalizedAppletEnable(input:{\n            applet_id: \"'+str(applet_id)+'\",\n            name: \"\",\n            push_enabled: false,\n            dynamic_applet_configuration: false,\n            stored_fields: \"{}\",\n            metadata: \"{}\"\n          }) {\n            normalized_applet {\n                      id\nname\ndescription\nbrand_color\nmonochrome_icon_url\nauthor\nstatus\ninstalls_count\npush_enabled\ntype\ncreated_at\nlast_run\nrun_count\nspeed\nconfig_type\nby_service_owner\nbackground_images {\n    background_image_url_1x\n    background_image_url_2x\n}\nconfigurations {\n    title\n    icon_url\n}\napplet_feedback_by_user\ncan_push_enable\n        service_name\n        channels {\n            id\nmodule_name\nshort_name\nname\ndescription_html\nbrand_color\nmonochrome_image_url\nlrg_monochrome_image_url\nis_hidden\nconnected\nrequires_user_authentication\ncall_to_action {\n    text\n    link\n}\norganization {\n    tier\n}\n        }\n              underlying_applet {\n                live_applet {\n                    live_applet_triggers {\n                        statement_id\n                    }\n                }\n              }\n            }\n            user_token\n            errors {\n              attribute\n              message\n            }\n          }\n        }'}
  r2 = requests.post(URL_for_post_status, headers=post_header, json=enablebody)
  print(r2)
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
      if appletData['enabled']:
        return track_action_services, action_details_list, trigger_fields_of_active_trigger
      else:
        enableApplet(appletData['applet_id'])
        newStatus = True
    else:
      print('Diableing not realted applet ...  1')
      ##################################################################################################################
      ########## If applet already disabled  contine, otherwise toggle and update database #############################
      if not appletData['enabled']:
        disableApplet(appletData['applet_id'])
        newStatus = False
      else:
        return track_action_services, action_details_list, trigger_fields_of_active_trigger

  else:
    print('Diableing not realted applet ...  2')
    ##################################################################################################################
    ########## If applet already disabled  contine, otherwise toggle and update database #############################
    if not appletData['enabled']:
      disableApplet(appletData['applet_id'])
      newStatus = False
    else:
      print('not enabled')
      return track_action_services, action_details_list, trigger_fields_of_active_trigger

  appletcollection.update({'_id': appletData['_id']}, {'$set': {'enabled': newStatus}})
  print('db updated')
  return track_action_services,action_details_list,trigger_fields_of_active_trigger

def enableOnlyRequiredApplets(trigger, trigger_service, attempt):
  s1 = timeit.default_timer()
  active_trigger = trigger
  active_trigger_service = trigger_service
  i = 0
  for appletData in all_applet_details:
    i = i + 1
    # if i <= 2000:
    #   continue
    if i%100 == 0:
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





# Time for diff library function= 252.38387497000804 => 4.20min
# final results:
# {'active_trigger': 'Any new post', 'active_trigger_service': 'blogger', 'trigger_fields_of_active_trigger': '', 'action_details_list': [{'action_service': 'go', 'action': 'Set the volume', 'action_desc': 'This action will set the volume on hearing aid.', 'action_fields': {'volume_level': 'min'}}, {'action_service': 'android_device', 'action': 'Turn on WiFi', 'action_desc': "This Action will turn off your Android device's WiFi.", 'action_fields': {}}, {'action_service': 'narro', 'action': 'Submit plain-text', 'action_desc': 'This Action will read a plain-text submission into your Narro feed. This is currently available only to Narro Pro members.', 'action_fields': {'text': '{{PostTitle}}<br>\n{{PostContent}}<br>\nvia Blogger {{PostUrl}}<br>\n{{PostPublished}}', 'title': '{{PostTitle}}'}}, {'action_service': 'diigo', 'action': 'Add a private bookmark', 'action_desc': 'This Action will add a private bookmark to your Diigo account.', 'action_fields': {'url': '{{PostUrl}}', 'tags': 'IFTTT, Blogger, {{Labels}}', 'description': '{{PostContent}}'}}, {'action_service': 'google_docs', 'action': 'Append to a document', 'action_desc': 'This action will append to a Google document as determined by the file name and folder path you specify. Once a file’s size reaches 2MB a new file will be created.\r\n', 'action_fields': {'filename': 'Any new post', 'body': '{{PostTitle}}<br>\n{{PostContent}}<br>\nvia Blogger {{PostUrl}}<br>\n{{PostPublished}}', 'path': 'IFTTT/Blogger'}}, {'action_service': 'dropbox', 'action': 'Add file from URL', 'action_desc': 'This Action will append to a text file as determined by the file name and folder path you specify. Once a file’s size reaches 2MB a new file will be created.', 'action_fields': {'url': '{{PostImageUrl}}', 'filename': 'Any new post', 'path': 'IFTTT/Blogger'}}, {'action_service': 'wordpress', 'action': 'Create a post', 'action_desc': 'This Action will create a photo post on your WordPress blog from the given URL to an image.', 'action_fields': {'title': '{{PostTitle}}', 'body': '{{PostContent}}<br>\n<br>\nfrom Blogger {{PostUrl}}<br>\nvia <a href="https://ifttt.com/?ref=da&site=wordpress">IFTTT</a>', 'categories': 'myname', 'tags': 'IFTTT, Blogger', 'post_status': 'publish'}}, {'action_service': 'tumblr', 'action': 'Create a video post ', 'action_desc': 'This Action will create an audio post on your Tumblr blog from the given URL to an MP3 file.', 'action_fields': {'video_url': '{{PostImageUrl}}', 'caption': '{{PostTitle}} {{PostUrl}}', 'tags': 'IFTTT, Blogger', 'state': 'published'}}, {'action_service': 'office_365_calendar', 'action': 'Create calendar item', 'action_desc': 'This Action creates a new item in your calendar.', 'action_fields': {'Subject': '{{PostTitle}}', 'body': '{{PostTitle}} {{PostUrl}}', 'location': 'NUS School of Computing, COM1, 13 Computing Drive, 117417', 'days': '0', 'time': '15:00:17'}}, {'action_service': 'pocket', 'action': 'Save for later', 'action_desc': 'This Action will add a new item to your Pocket queue. NOTE: If using an RSS feed Trigger, please limit the number of Pocket saves to no more than a few hundred per week', 'action_fields': {'url': '{{PostUrl}}', 'tags': 'IFTTT, Blogger, {{Labels}}'}}, {'action_service': 'bitly', 'action': 'Add a bitlink', 'action_desc': 'This Action will shorten and add a new bitlink to your bitly account.', 'action_fields': {'url': '{{PostUrl}}', 'notes': '{{PostContent}}'}}, {'action_service': 'google_calendar', 'action': 'Quick add event', 'action_desc': 'This action will create a detailed event in your Google Calendar.', 'action_fields': {'calendar': 'happybee9494@gmail.com', 'quick_add': '{{PostTitle}} {{PostUrl}}'}}, {'action_service': 'amazonclouddrive', 'action': 'Add file from URL', 'action_desc': 'This Action will upload a file from a given URL and add it to Amazon Cloud Drive at the path you specify.', 'action_fields': {'url': '{{PostImageUrl}}', 'fileName': 'Any new post', 'destination': 'IFTTT/Blogger'}}, {'action_service': 'google_sheets', 'action': 'Update cell in spreadsheet', 'action_desc': "This action will update a single cell in the first worksheet of a spreadsheet you specify. Note: a new spreadsheet is created if the file doesn't exist.", 'action_fields': {'path': 'IFTTT/Blogger', 'filename': 'Any new post', 'cell': 'myname', 'value': '{{PostTitle}} {{PostUrl}}'}}, {'action_service': 'google_drive', 'action': 'Upload file from URL', 'action_desc': 'This action will download a file at a given URL and add it to Google Drive at the path you specify. NOTE: 30 MB file size limit.\r\n', 'action_fields': {'url': '{{PostImageUrl}}', 'filename': 'Any new post', 'path': 'IFTTT/Blogger'}}, {'action_service': 'cisco_spark', 'action': 'Create a Spark room', 'action_desc': 'This Action will archive a room in Spark.', 'action_fields': {'title': '{{PostTitle}}'}}, {'action_service': 'telegram', 'action': 'Send video', 'action_desc': 'This action will send an mp3 to a Telegram chat.', 'action_fields': {'chat_id': '0', 'video_url': '{{PostImageUrl}}', 'caption': '{{PostTitle}} {{PostUrl}}'}}, {'action_service': 'coqon', 'action': 'Fire rule in coqon', 'action_desc': 'This action will fire the associated rule on our coqon box.', 'action_fields': {'action_code': 'code123'}}, {'action_service': 'google_contacts', 'action': 'Create new contact', 'action_desc': 'This Action will create a new contact in Google Contacts.', 'action_fields': {'full_name': 'myname', 'which_group': 'http://www.google.com/m8/feeds/groups/happybee9494%40gmail.com/base/6', 'phone_number': '+6594864587', 'email': 'happybee9494@gmail.com', 'address': 'NUS School of Computing, COM1, 13 Computing Drive, 117417', 'job_title': 'myname', 'company': 'myname', 'notes': '{{PostTitle}} {{PostUrl}}', 'upload_photo': '{{PostImageUrl}}'}}, {'action_service': 'office_365_contacts', 'action': 'Add new contact', 'action_desc': 'This Action adds a new contact to your Office 365 account.', 'action_fields': {'name': 'Any new post', 'emailaddress': 'happybee9494@gmail.com', 'businessphone': 'myname', 'companyname': 'myname'}}, {'action_service': 'onedrive', 'action': 'Create text file', 'action_desc': 'This Action will download a file at a given URL and add it to OneDrive at the path you specify. NOTE: 30 MB file size limit.', 'action_fields': {'filename': 'Any new post', 'path': 'IFTTT/Blogger', 'content': '{{PostTitle}}<br>\n{{PostContent}}<br>\nvia Blogger {{PostUrl}}<br>\n{{PostPublished}}'}}, {'action_service': 'particle', 'action': 'Publish an event', 'action_desc': 'This Action will call a function on one of your Devices, triggering an action in the physical world.', 'action_fields': {'topic': '{{PostTitle}}', 'contents': '{{PostTitle}} {{PostUrl}}', 'public': 'public'}}, {'action_service': 'strava', 'action': 'Update weight', 'action_desc': 'This Action will update your weight on Strava.', 'action_fields': {'new_weight': '100', 'weight_unit': 'kg'}}, {'action_service': 'email', 'action': 'Send me an email', 'action_desc': 'This Action will send you an HTML based email. Images and links are supported.', 'action_fields': {'subject': '{{PostTitle}}', 'body': '{{PostContent}}<br>\n<br>\nvia Blogger {{PostUrl}}'}}, {'action_service': 'maker_webhooks', 'action': 'Make a web request', 'action_desc': 'This action will make a web request to a publicly accessible URL. NOTE: Requests may be rate limited.', 'action_fields': {'url': 'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing', 'method': 'GET', 'content_type': 'application/json', 'body': 'a description of the event'}}, {'action_service': 'github', 'action': 'Create an issue', 'action_desc': 'This Action will create a new issue for the repository you specify.', 'action_fields': {'repository': 'myname', 'issueTitle': '{{PostTitle}}', 'issueBody': '<b>{{PostTitle}}</b><br>\n{{PostContent}}<br>\n<br>\nvia Blogger {{PostUrl}}<br>\n{{PostPublished}}'}}, {'action_service': 'fitbit', 'action': 'Log your weight', 'action_desc': 'This Action will log a new weight measurement to Fitbit.', 'action_fields': {'weight': '100', 'weight_unit': 'kilograms'}}, {'action_service': 'office_365_mail', 'action': 'Send email', 'action_desc': 'This Action will send an email from your Office 365 mail account.', 'action_fields': {'Recipients': 'myname', 'Subject': '{{PostTitle}}', 'Body': '{{PostTitle}}<br>\n{{PostContent}}<br>\nvia Blogger {{PostUrl}}<br>\n{{PostPublished}}'}}, {'action_service': 'deezer', 'action': 'Add playlist to favorites', 'action_desc': 'This Action will search for a track you specify and add the first matching result to your playlist.', 'action_fields': {'input': '{{PostTitle}}'}}, {'action_service': 'musixmatch', 'action': 'Add a track to favorites', 'action_desc': 'This Action will search for a track you specify and add the first matching result to your favorites on Musixmatch.', 'action_fields': {'search_query': '{{PostTitle}}', 'artist_name': 'myname'}}, {'action_service': 'ios_calendar', 'action': 'Create a calendar event', 'action_desc': 'This action creates a new event in the calendar you specify.', 'action_fields': {'calendar_name': 'myname', 'title': '{{PostTitle}}', 'location': 'NUS School of Computing, COM1, 13 Computing Drive, 117417', 'start_date': '15-10-2019', 'duration': '5', 'notes': '{{PostTitle}} {{PostUrl}}', 'url': '{{PostUrl}}', 'alert': '15 minutes'}}, {'action_service': 'soundcloud', 'action': 'Upload a private track', 'action_desc': 'This Action will upload a new private track from the URL you specify.', 'action_fields': {'url': 'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing', 'track_name': '{{PostTitle}}', 'track_description': '{{PostTitle}} {{PostUrl}}', 'tags': 'IFTTT, Blogger'}}, {'action_service': 'spotify', 'action': 'Add track to a playlist', 'action_desc': 'This Action will search for a track and add the first result to a playlist you specify.', 'action_fields': {'playlist': 'Any new post', 'search_query': '{{PostTitle}} {{PostUrl}}', 'artist_name': 'myname'}}, {'action_service': 'newsblur', 'action': 'Save a story', 'action_desc': 'This Action will attempt to add a new site from a feed or page URL.', 'action_fields': {'story_title': '{{PostTitle}}', 'story_url': '{{PostUrl}}', 'story_content': '{{PostTitle}}<br>\n{{PostContent}}<br>\nvia Blogger {{PostUrl}}<br>\n{{PostPublished}}', 'user_tags': 'IFTTT, Blogger'}}, {'action_service': 'ios_reminders', 'action': 'Add reminder to list', 'action_desc': 'This Action will add a new reminder to the list you specify.', 'action_fields': {'title': '{{PostTitle}}', 'list': 'myname', 'priority': '0', 'alarm_date': '15-10-2019'}}, {'action_service': 'ios_photos', 'action': 'Add photo to album', 'action_desc': 'This Action will save a new photo to the album you specify.', 'action_fields': {'photo_url': '{{PostImageUrl}}', 'album': 'myname'}}, {'action_service': 'evernote', 'action': 'Create a link note', 'action_desc': 'This Action will create a new note with an audio attachment in the notebook you specify.', 'action_fields': {'link_url': '{{PostUrl}}', 'body': '{{PostContent}}', 'notebook': 'IFTTT Blogger', 'tags': 'IFTTT, Blogger, {{Labels}}'}}, {'action_service': 'flickr', 'action': 'Upload public photo from URL', 'action_desc': 'This Action will upload a new public photo, from a given URL to an image, to your Flickr photostream.', 'action_fields': {'photo_url': '{{PostImageUrl}}', 'title': '{{PostTitle}}', 'description': 'via Blogger {{PostUrl}}', 'tags': 'ifttt'}}, {'action_service': 'sms', 'action': 'Send me an SMS', 'action_desc': 'This Action will send an SMS to your mobile phone.', 'action_fields': {'message': 'Blogger post: {{PostTitle}} {{PostUrl}}'}}, {'action_service': 'stockimo', 'action': 'Upload a photo', 'action_desc': 'This Action will upload a new photograph to your Stockimo collection from the .jpg or .jpeg URL specified. NOTE: Only .jpg or .jpeg file extensions allowed', 'action_fields': {'URL': '{{PostImageUrl}}'}}, {'action_service': 'twitter', 'action': 'Post a tweet with image', 'action_desc': 'This Action will update your bio and optionally tweet about it. NOTE: Please adhere to Twitter’s Rules and Terms of Service.', 'action_fields': {'tweet': '{{PostTitle}}', 'photo_url': '{{PostImageUrl}}'}}, {'action_service': 'beeminder', 'action': 'Charge me', 'action_desc': "This Action will charge your credit card the specified amount. If you don't have a credit card on file with Beeminder, or if there's a problem trying to charge it, we'll email you to let you know.", 'action_fields': {'amount': '100'}}, {'action_service': 'toodledo', 'action': 'Add a note', 'action_desc': 'This Action will add a new note to the folder you specify.', 'action_fields': {'title': '{{PostTitle}}', 'note': '{{PostContent}}<br>\n<br>\nvia Blogger {{PostUrl}}', 'folder': '0'}}, {'action_service': 'reddit', 'action': 'Submit a new link', 'action_desc': 'This Action will submit a new link on reddit. NOTE: reddit karma is required.', 'action_fields': {'title': '{{PostTitle}}', 'link': '{{PostUrl}}', 'subreddit': 'myname'}}, {'action_service': 'sina_weibo', 'action': 'Publish a new post', 'action_desc': 'This Action will publish a new post to Weibo.', 'action_fields': {'status': '{{PostTitle}} {{PostUrl}}', 'image_url': '{{PostImageUrl}}'}}, {'action_service': 'todoist', 'action': 'Create task', 'action_desc': 'This Action will create a new task in the project you specify.', 'action_fields': {'project_id': '2233344330', 'task_content': '{{PostTitle}} {{PostUrl}}', 'note': 'a brief desc of the event', 'due_date': '15-10-2019', 'priority': '1'}}]}
# ['go', 'android_device', 'narro', 'diigo', 'google_docs', 'dropbox', 'wordpress', 'tumblr', 'office_365_calendar', 'pocket', 'bitly', 'google_calendar', 'amazonclouddrive', 'google_sheets', 'google_drive', 'cisco_spark', 'telegram', 'coqon', 'google_contacts', 'office_365_contacts', 'onedrive', 'particle', 'strava', 'email', 'maker_webhooks', 'github', 'fitbit', 'office_365_mail', 'deezer', 'musixmatch', 'ios_calendar', 'soundcloud', 'spotify', 'newsblur', 'ios_reminders', 'ios_photos', 'evernote', 'flickr', 'sms', 'stockimo', 'twitter', 'beeminder', 'toodledo', 'reddit', 'sina_weibo', 'todoist']
