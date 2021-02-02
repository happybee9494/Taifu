from Taifu.Phase2AppletExecution import AppletEnabler2
from Taifu.BehaviorMonitoring_NoiseTemplates.tatester.tatester.spiders.MonitoringJavaScriptAction import monitoring
#############################################################################################
# ENABLE A SET OF APPLETS AND OUTPUT ALL THE ACTION_SERVICES RELATED TO THE ENABLED APPLETS
#############################################################################################
trigger_service = 'android_photos' #blogger'
trigger = 'Any new photo'
results = AppletEnabler2.enableOnlyRequiredApplets(trigger, trigger_service, 1)


active_trigger = results['active_trigger']
active_trigger_service = results['active_trigger']
trigger_fields_of_active_trigger = results['trigger_fields_of_active_trigger']
action_details_list = results['action_details_list']
action_name_list = []
for actionD in action_details_list:
    action_service = actionD['action_service']
    action =  actionD['action']
    action_desc = actionD['action_desc']
    action_fields = actionD['action_fields']
    action_name_list.append(action_service)
print(action_name_list)
###################################################################################
##  SCRAPE THE BEFORE INSTANCE FOR EACH ACTION SERVICE ############################
# for action_service in action_name_list:
#     default_start_no = 0
#     default_end_no = 1
#     if action_service != 'twitter':
#         continue
#     action_services_to_monitor = [action_service]
#     monitoring(default_start_no, default_end_no, action_services_to_monitor)
#     print('monitoring done: ' + str(action_service))
#############################################################################################
#############################################################################################
# diigo
# Add a public bookmark
# This Action will add a private bookmark to your Diigo account.
# {'url': 'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing', 'tags': 'ifttt', 'description': 'a description of the event'}
# narro
# Submit an article
# This Action will read a plain-text submission into your Narro feed. This is currently available only to Narro Pro members.
# {'url': 'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing', 'title': 'a brief desc of the event'}
# pocket
# Save for later
# This Action will add a new item to your Pocket queue. NOTE: If using an RSS feed Trigger, please limit the number of Pocket saves to no more than a few hundred per week
# {'url': 'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing', 'tags': 'ifttt'}
# airtable
# Create a new record
# This Action will create a new record in a table of your choosing.
# {'base_id': 'appGND5aO4UGjLFsV', 'table_id_or_name': 'myname', 'record_content': 'a description of the event'}
# google_calendar
# Quick add event
# This action will create a detailed event in your Google Calendar.
# {'calendar': 'happybee9494@gmail.com', 'quick_add': 'a brief desc of the event'}
# google_docs
# Create a document
# This action will append to a Google document as determined by the file name and folder path you specify. Once a file’s size reaches 2MB a new file will be created.
#
# {'filename': 'myname', 'body': 'a brief desc of the event', 'path': 'myfolder'}
# google_sheets
# Add row to spreadsheet
# This action will update a single cell in the first worksheet of a spreadsheet you specify. Note: a new spreadsheet is created if the file doesn't exist.
# {'filename': 'myname', 'formatted_row': 'myname', 'path': 'myfolder'}
# coqon
# Fire rule in coqon
# This action will fire the associated rule on our coqon box.
# {'action_code': 'code123'}
# github
# Create an issue
# This Action will create a new issue for the repository you specify.
# {'repository': 'myname', 'issueTitle': 'a brief desc of the event', 'issueBody': 'a description of the event'}
# particle
# Publish an event
# This Action will call a function on one of your Devices, triggering an action in the physical world.
# {'topic': 'myname', 'contents': 'a brief desc of the event', 'public': 'public'}
# maker_webhooks
# Make a web request
# This action will make a web request to a publicly accessible URL. NOTE: Requests may be rate limited.
# {'url': 'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing', 'method': 'GET', 'content_type': 'application/json', 'body': 'a description of the event'}
# fitbit
# Log your weight
# This Action will log a new weight measurement to Fitbit.
# {'weight': '100', 'weight_unit': 'kilograms'}
# reddit
# Submit a new text post
# This Action will submit a new link on reddit. NOTE: reddit karma is required.
# {'title': 'a brief desc of the event', 'text': 'a brief desc of the event', 'subreddit': 'myname'}
# twitter
# Post a tweet
# This Action will update your bio and optionally tweet about it. NOTE: Please adhere to Twitter’s Rules and Terms of Service.
# {'tweet': 'a brief desc of the event'}