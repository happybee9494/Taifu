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
token = '0dfb5edac5e2201a9ece7b3908dcfd04d57522b6' #  #1b004674987164ecf6ed87c30146aa90b4c21024 #0dfb5edac5e2201a9ece7b3908dcfd04d57522b6 #c2436a9ef37d65910c1c05f6d137dbb7d79260d4
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"', 'Content-Type':'application/json; charset=utf-8'}
###########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
eventDatacollection = db.get_collection('serviceconfigdetails')
all_event_details = eventDatacollection.find({})
################################################################
authDatacollection = db.get_collection('authdetails')
all_auth_details = authDatacollection.find({})
################################################################
labelcollection = db.get_collection('clusterlabeldetails')
all_label_details = labelcollection.find({})
################################################################
dbClient = client['evalapplets']
appletcollection = dbClient.get_collection('appletcollection14')

########################## SERVICE #########################################
trigger_results =[]
action_results = []
for event in all_event_details:
    eventData = []
    eventData.append(event['service_idnetifier'])
    eventData.append(event['eventName'])
    if event['eventType'] == 'trigger':
        trigger_results.append(eventData)
    elif event['eventType'] == 'action':
        action_results.append(eventData)
############################ AUTHENTICATED #################################
all_auth_details_list  = []
for authService in all_auth_details:
    serviceID = authService['service_idnetifier']
    connected = authService['connected']
    if connected:
        all_auth_details_list.append(serviceID)
############################# CLUSTER DATA #################################
all_label_details_list  = {}
for fieldText in all_label_details:
    textField = fieldText['textField']
    label = fieldText['label']
    if label:
        all_label_details_list[textField] = label
all_label_details_list = dict((k.lower(), v.lower()) for k,v in all_label_details_list.items())
###########################################################################
def getValue(cluster_label, field_label):

    if cluster_label == 'option':
        return 'NA'
    if cluster_label == 'url':
        return  'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing'
    if cluster_label == 'description':
        return  'a description of the event'
    if cluster_label == 'time':
        return  '15:00:17'
    if cluster_label == 'keyword':
        return  'ifttt'
    if cluster_label == 'percentage':
        return  '55'
    if cluster_label == 'temperature':
        return  '86F'
    if cluster_label == 'short description':
        return  'a brief desc of the event'
    if cluster_label == 'phonenumber':
        return  '+6594864587'
    if cluster_label == 'folder':
        return  'myfolder'
    if cluster_label == 'address':
        return  '120607'
    if cluster_label == 'brightness':
        return  '800'
    if cluster_label == 'duration':
        return  '5'
    if cluster_label == 'name':
        return  'myname'
    if cluster_label == 'color':
        return  'red'
    if cluster_label == 'price':
        return  '55'
    if cluster_label == 'threshold':
        return  '50'
    if cluster_label == 'username':
        return  'wijitha.mahadewa@gmail.com'
    if cluster_label == 'command':
        return  'turn on light'
    if cluster_label == 'code or token':
        return  'code123'
    if cluster_label == 'expression':
        return  '([A-Z])\w+/g'
    if cluster_label == 'attachment':
        return  'https://drive.google.com/file/d/16huU6aiQcppAqVG4td9XCNge7BnlYsJd/view?usp=sharing'
    if cluster_label == 'speed':
        return  '20'
    if cluster_label == 'query':
        return  'ifttt'
    if cluster_label == 'position':
        return  'static'
    if cluster_label == 'pressure':
        return  '80'
    if cluster_label == 'destination':
        return  'ifttt'
    if cluster_label == 'humidity':
        return  '40'
    if cluster_label == 'number':
        return  '65'
    if cluster_label == 'value':
        return  '100'
    if cluster_label == 'id':
        return  'id123'
    if cluster_label == 'location':
        return  '120607'
    if cluster_label == 'date':
        return  '15-10-2019'
    if cluster_label == 'day':
        return  'Tuesday'
    if cluster_label == 'email':
        return  '*****@gmail.com'

def updateDBOrDeleteDuplication(appletcollection,applet_title,applet_id,applet_desc,trigger_service,trigger,trigger_desc,trigger_fields,action_service,action,action_desc,action_fields):
    appletFound = appletcollection.find({'applet_title': applet_title})
    foundList = []
    for found in appletFound:
        foundList.append(found)
        URL_for_trigger_data = "https://buffalo-android.ifttt.com/grizzly/me/applets/" + str(applet_id)
        print('Deleting...')
        print(URL_for_trigger_data)
        r = requests.delete(URL_for_trigger_data, headers=header)  # ----------------->
        continue

    if len(foundList) == 0:
        print('add to db')
        doc = {
            'applet_id': applet_id,
            'applet_title': applet_title,
            'applet_desc': applet_desc,
            'trigger_service': trigger_service,
            'trigger': trigger,
            'trigger_desc': trigger_desc,
            'trigger_fields': trigger_fields,
            'action_service': action_service,
            'action': action,
            'action_desc': action_desc,
            'action_fields': action_fields,
            'enabled': False,
        }
        appletcollection.update(doc, doc, upsert=True)

        print("record inserted. "+ str(appletcollection.count()))
    return

def triggerConfiguration(trigger,trigger_service):
    print('TRIGGER INPUTS ....')
    request1 = None
    # POST fields for preview request
    trigger_id = None
    trigger_fields = {}
    trigger_service_id = None
    push_enabled = False
    applet_creation_pause_by_trigger = False
    trigger_desc = None
    return_trigger_module_name = None
    try:
        URL_for_trigger_data = "https://buffalo-android.ifttt.com/grizzly/me/diy/services/" + trigger_service
        r = requests.get(URL_for_trigger_data, headers=header)
        js_dict = r.json()
        print('########### trigger config 1')
        print(URL_for_trigger_data)
        print(r)
        print(js_dict)
        # ############################# get the trigger configuration information and assign vales to the fields ###########################
        trigger_permission = js_dict['trigger_permissions']
        for tp in trigger_permission:
            trigger_desc = tp['description']
            trigger_in_tp = tp['name']
            # ################################### find the fields set match with the selected trigger #######################################
            if trigger_in_tp == trigger:  # 'Button press':#
                t_id = tp['id']
                t_module_name = tp['module_name']
                return_trigger_module_name = t_module_name
                t_fields = tp['fields']
                field_value_set = None
                options_available = False
                other_field_available = False
                trigger_fields = {}
                if t_fields:
                    t = 0
                    for tf in t_fields:
                        t += 1
                        f = t_fields[tf]
                        f_field_type = f['field_type']
                        f_required = f['required']
                        f_name = f['name']
                        f_label = f['label'].lower()
                        #################################################################################################################
                        # based on field types assign values for the fields
                        if f_field_type == 'option':
                            options_available = True
                            f_options_static = f['options_static']
                            try:
                                f_resolve_options = f['resolve_options']
                                geturlttriggeroptions = 'https://buffalo-android.ifttt.com' + str(f_resolve_options)
                                r = requests.get(geturlttriggeroptions, headers=header)
                                options_js_dict = r.json()
                                print('########### trigger config 2')
                                print(geturlttriggeroptions)
                                print(r)
                                print(options_js_dict)
                                for key in options_js_dict:
                                    field_set_key = key
                                    if options_js_dict.get(key) == None:
                                        options_not_availabe = True
                                    else:
                                        values = options_js_dict.get(key)
                                        # choose a value from the list of options
                                        for v in values:
                                            if not field_value_set:
                                                field_value_set = '[' + field_set_key + ']=' + v['value']
                                            else:
                                                field_value_set = field_value_set + ',' + '[' + field_set_key + ']=' + \
                                                                  v['value']
                                            trigger_fields[field_set_key] = v['value']
                                            if f_required and v['value'] == "":
                                                applet_creation_pause_by_trigger = True

                            except KeyError:
                                print('no options to resolve')

                        elif f_field_type == 'location':
                            other_field_available = True
                            field_key = f_name
                            value = '1.2966° N, 103.7764° E'  # // nus location
                            field_value_set = field_value_set + ',' + '[' + field_key + ']=' + value
                            trigger_fields[field_key] = value
                        elif f_field_type == 'location-area':
                            other_field_available = True
                            field_key = f_name
                            value = 'NUS School of Computing, COM1, 13 Computing Drive, 117417'
                            field_value_set = field_value_set + ',' + '[' + field_key + ']=' + value
                            trigger_fields[field_key] = value
                        elif f_field_type == 'date-and-time':
                            other_field_available = True
                            field_key = f_name
                            value = 'October 23, 2019 at 01:01PM'
                            field_value_set = field_value_set + ',' + '[' + field_key + ']=' + value
                            trigger_fields[field_key] = value
                        elif f_field_type == 'miniutes-past-hour':
                            other_field_available = True
                            field_key = f_name
                            value = '20'
                            field_value_set = field_value_set + ',' + '[' + field_key + ']=' + value
                            trigger_fields[field_key] = value
                        elif f_field_type == 'option-multi':
                            other_field_available = True
                        elif f_field_type == 'text':
                            text_type = all_label_details_list[f_label]
                            text_value = getValue(text_type, f_label)
                            print('f_label: ' + str(f_label))
                            other_field_available = True
                            field_key = f_name
                            print(type(field_key))
                            print(type(text_value))
                            print(type(field_value_set))

                            if not field_value_set:
                                field_value_set = '[' + field_key + ']=' + str(text_value)
                            else:
                                field_value_set = field_value_set + ',' + '[' + field_key + ']=' + str(text_value)

                            trigger_fields[field_key] = text_value
                        elif f_field_type == 'time-of-day':
                            other_field_available = True
                            field_key = f_name
                            value = '01:01PM'
                            field_value_set = field_value_set + ',' + '[' + field_key + ']=' + value
                            trigger_fields[field_key] = value
                print(field_value_set)
                #################################################################################################################

                if field_value_set and options_available:
                    field_value_set_quoted = urllib.parse.quote('[' + field_set_key + ']=' + field_value_set,
                                                                '=')  # omit = sign from quoting
                    request1 = 'https://buffalo-android.ifttt.com/grizzly/me/diy/triggers/' + t_module_name + '/validate?fields' + field_value_set  # GET

                elif other_field_available:
                    field_value_set_quoted = urllib.parse.quote(field_value_set, '=')  # omit = sign from quoting
                    request1 = 'https://buffalo-android.ifttt.com/grizzly/me/diy/triggers/' + t_module_name + '/validate?fields' + field_value_set_quoted  # GET
                else:
                    request1 = 'no fields'
                trigger_id = t_id
                trigger_service_id = trigger_service


    except KeyError:
        print('no trigger_permission')
    return trigger_fields,push_enabled,trigger_id,trigger_service_id,trigger_desc,request1,applet_creation_pause_by_trigger,return_trigger_module_name

def actionConfiguration(action, action_service,return_trigger_module_name):
    action_id = None
    action_fields = {}
    action_service_id = None
    request11 = None
    action_desc = None
    applet_creation_pause_by_action = None
    print('ACTION INPUTS...')
    try:
        URL_for_action_data = "https://buffalo-android.ifttt.com/grizzly/me/diy/services/" + action_service
        r = requests.get(URL_for_action_data, headers=header)
        js_dict = r.json()
        print('########### action config 1')
        print(URL_for_action_data)
        print(js_dict)
        options_available = False
        text_available = False
        action_fields = {}
        applet_creation_pause_by_action = False
        # ############################# get the action configuration information and assign vales to the fields ############################
        action_permissions = js_dict['action_permissions']
        for ap in action_permissions:
            action_desc = ap['description']
            action_ap_name = ap['name']
            # ################################### find the fields set match with the selected action #######################################
            if action_ap_name == action:  # 'Blink lights':#
                a_id = ap['id']
                a_module_name = ap['module_name']
                a_fields = ap['fields']
                ################################ get the default fields for the action #####################################################
                request1b= 'https://buffalo-android.ifttt.com/grizzly/me/diy/actions/' + a_module_name + '/default_fields_for/'+return_trigger_module_name  # GET
                defaultKeyValue_response = requests.get(request1b, headers=header)
                defaultKeyValue = defaultKeyValue_response.json()
                print('########### action config 2')
                print(request1b)
                print(defaultKeyValue)
                ############################################################################################################################
                field_value_set = None
                if a_fields:
                    a = 0
                    for af in a_fields:
                        print(af)
                        f = a_fields[af]
                        f_name = f['name']
                        a += 1
                        f_field_type = f['field_type']
                        f_required = f['required']
                        f_label = f['label'].lower()
                        #################################################################################################################
                        # based on field types assign values for the fields
                        if f_field_type == 'option':
                            options_available = True
                            f_options_static = f['options_static']
                            try:
                                f_resolve_options = f['resolve_options']
                                geturl_actionoptions = 'https://buffalo-android.ifttt.com' + str(f_resolve_options)
                                r = requests.get(geturl_actionoptions, headers=header)
                                options_js_dict = r.json()
                                print('########### action config 3')
                                print(geturl_actionoptions)
                                print(options_js_dict)
                                for key in options_js_dict:
                                    field_set_key = key
                                    if options_js_dict.get(key) == None:
                                        options_not_availabele = True
                                    else:
                                        values = options_js_dict.get(key)
                                        # choose a value from the list of options
                                        #print(values)
                                        for v in values:
                                            if not field_value_set:
                                                field_value_set = '[' + field_set_key + ']=' + v['value']
                                            else:
                                                field_value_set = field_value_set + ',' + '[' + field_set_key + ']=' + \
                                                                  v['value']
                                            #print(field_value_set)
                                            action_fields[field_set_key] = v['value']
                                            if f_required and v['value'] == "":
                                                #print('option value is not available')
                                                applet_creation_pause_by_action = True
                                            break
                            except KeyError:
                                print('no options to resolve')
                        # ####################### not an option field #################################################
                        # ######### set values from the default #######################################################
                        elif f_field_type == 'text':
                            text_available = True
                            field_key = f_name
                            ## if value is provided in default_field set -> get value from there #####################
                            if f_name in defaultKeyValue:
                                text_value = defaultKeyValue[f_name]
                            ## else ask from input oracle for the value ##############################################
                            else:
                                text_type = all_label_details_list[f_label]
                                text_value = getValue(text_type, f_label)
                            # if default field not availab e##########################################################
                            if text_value.strip() == '':
                                text_type = all_label_details_list[f_label]
                                text_value = getValue(text_type, f_label)
                            # #########################################################################################
                            if not field_value_set:
                                field_value_set = '[' + field_key + ']=' + str(text_value)
                            else:
                                field_value_set = field_value_set + ',' + '[' + field_key + ']=' + str(text_value)
                            action_fields[field_key] = text_value

                print(field_value_set)
                #################################################################################################################
                if field_value_set and options_available:
                    field_value_set_quoted = urllib.parse.quote(field_value_set, '=')  # omit = sign from quoting
                    request11 = 'https://buffalo-android.ifttt.com/grizzly/me/diy/actions/' + a_module_name + '/validate?fields' + field_value_set_quoted  # GET
                elif text_available:
                    field_value_set_quoted = urllib.parse.quote(field_value_set, '=')  # omit = sign from quoting
                    request11 = 'https://buffalo-android.ifttt.com/grizzly/me/diy/actions/' + a_module_name + '/validate?fields' + field_value_set_quoted  # GET
                else:
                    request11 = 'no fields'
                action_id = a_id
                action_service_id = action_service

    except KeyError:
        print('no action_permission')
    return action_fields,action_id,action_service_id,action_desc,request11,applet_creation_pause_by_action

def completeAppletGeneration(trigger_fields,push_enabled,trigger_id,trigger_service_id,request1,action_fields,action_id,action_service_id,request11):
    request2 = 'https://buffalo-android.ifttt.com/grizzly/me/diy/preview'  # POST
    request2_body = {
        "diy": {"action_fields": action_fields, "action_id": action_id,
                "action_service_id": action_service_id,
                "push_enabled": push_enabled, "trigger_fields": trigger_fields, "trigger_id": trigger_id,
                "trigger_service_id": trigger_service_id}}
    print('trigger URL:')
    print(request1)

    if request1 != 'no fields':
        print('request 1 (trigger)... get request sends with field params')
        r = requests.get(request1, headers=header)
        js_dict = r.json()
        pprint(js_dict)
        print('########### completeAppletGeneration 1')
        print(request1)
        print(js_dict)

    print('action URL:')
    if request11 != 'no fields':
        print(request11)
        print('request 11 (action)... get request sends with field params')
        r = requests.get(request11, headers=header)
        js_dict = r.json()
        print('########### completeAppletGeneration 2')
        print(request11)
        pprint(js_dict)

    else:
        print(request11)
    # ////////////////////////////////////////////////////////////////////////
    print('request 2 ... post data for preview')
    r = requests.post(request2, data=json.dumps(request2_body), headers=post_header)
    js_response = r.json()  # preview description is available in the response
    print('########### completeAppletGeneration 3')
    print(request2)
    print(json.dumps(request2_body))
    pprint(js_response)

    if 'channel' in js_response:
        if js_response['channel'] == ['channel not active for user']:
            print('Channel not active for user.....')

    description = js_response['preview']  # required for request3

    # ////////////////////////////////////////////////////////////////////////
    print('request 3 ... post data with push enabled true')
    request3 = 'https://buffalo-android.ifttt.com/grizzly/me/diy'  # POST
    request3_body = {
        "diy": {"action_fields": action_fields, "action_id": action_id,
                "action_service_id": action_service_id,
                "description": description, "push_enabled": True, "trigger_fields": trigger_fields,
                "trigger_id": trigger_id, "trigger_service_id": trigger_service_id}}

    r = requests.post(request3, data=json.dumps(request3_body), headers=post_header)
    print('########### completeAppletGeneration 4')
    print(request3)
    print(json.dumps(request3_body))
    print(r.text)

    js_response = r.json()  # include applet details required for next request
    applet = js_response['applet']
    applet_id = applet['id']
    applet_title = applet['name']
    applet_desc = applet['description']
    applet_creation_response = applet['speed']
    f = open("../Phase1AppletGeneration/output_applets/response-" + str(applet_id) + ".txt", "w")
    f.write(r.text)
    f.close()
    ###############################################################################################################
    print('request 4 ... get the details of the applet created')
    request4 = 'https://buffalo-android.ifttt.com/grizzly/me/services/diy/applets/' + applet_id  # GET
    r = requests.get(request4, headers=header)
    js_dict = r.json()
    print('########### completeAppletGeneration 5')
    print(request4)
    pprint(js_dict)
    ############################################# Disable applet ###################################################
    print('request 5... disable the applet')
    URL_for_post_status = 'https://ifttt.com/api/v3/graph'
    enablebody = {
        "query": 'mutation {\n          normalizedAppletDisable(input:{\n            applet_id: \"' + str(
            applet_id) + '\",\n            name: \"\",\n            push_enabled: false,\n            dynamic_applet_configuration: false,\n            stored_fields: \"{}\",\n            metadata: \"{}\"\n          }) {\n            normalized_applet {\n                      id\nname\ndescription\nbrand_color\nmonochrome_icon_url\nauthor\nstatus\ninstalls_count\npush_enabled\ntype\ncreated_at\nlast_run\nrun_count\nspeed\nconfig_type\nby_service_owner\nbackground_images {\n    background_image_url_1x\n    background_image_url_2x\n}\nconfigurations {\n    title\n    icon_url\n}\napplet_feedback_by_user\ncan_push_enable\n        service_name\n        channels {\n            id\nmodule_name\nshort_name\nname\ndescription_html\nbrand_color\nmonochrome_image_url\nlrg_monochrome_image_url\nis_hidden\nconnected\nrequires_user_authentication\ncall_to_action {\n    text\n    link\n}\norganization {\n    tier\n}\n        }\n              underlying_applet {\n                live_applet {\n                    live_applet_triggers {\n                        statement_id\n                    }\n                }\n              }\n            }\n            user_token\n            errors {\n              attribute\n              message\n            }\n          }\n        }'}
    r2 = requests.post(URL_for_post_status, headers=post_header, json=enablebody)



    return applet_id,applet_desc,applet_title

def appletGeneration(trigger, trigger_service,action, action_service):
    try:
        trigger_fields, push_enabled, trigger_id, trigger_service_id, trigger_desc, request1, applet_creation_pause_by_trigger,return_trigger_module_name = triggerConfiguration(
            trigger, trigger_service)
        action_fields, action_id, action_service_id, action_desc, request11, applet_creation_pause_by_action = actionConfiguration(
            action, action_service,return_trigger_module_name)

        if applet_creation_pause_by_trigger or applet_creation_pause_by_action:
            print('applet creation paused due to required info not available')
        elif not action_id or not trigger_id:
            print('Problem in trigger or action selection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111')
        else:
            applet_id, applet_desc, applet_title = completeAppletGeneration(trigger_fields, push_enabled, trigger_id,
                                                                            trigger_service_id,
                                                                            request1, action_fields, action_id,
                                                                            action_service_id, request11)
            applet_title = applet_title.replace("'", "''")
            updateDBOrDeleteDuplication(appletcollection, applet_title, applet_id, applet_desc, trigger_service,
                                        trigger, trigger_desc, trigger_fields, action_service, action, action_desc,
                                        action_fields)
    except KeyError:
        print('no trigger_permission')
    except JSONDecodeError:
        print('json error')
        appletGeneration(trigger, trigger_service, action, action_service)
############################################################################################################################
############################################################################################################################
x = 0
#'pinterest' 36: appletcollection10
#foursquare 36: appletcollection11 'Any new check-in'
print('start here')
s1 = timeit.default_timer()
threads = []
attempt = 1
current_action_services =  ['tumblr','instagram','onedrive','strava', 'narro', 'diigo', 'google_docs',  'pocket', 'google_calendar',  'google_sheets', 'google_drive', 'google_contacts', 'particle','github', 'fitbit','spotify', 'flickr', 'beeminder', 'toodledo', 'reddit', 'todoist','dropbox','pocket','office_365_mail','office_365_contacts','deezer','twitter','evernote','blogger','amazonclouddrive','musixmatch','cisco_spark','email','office_365_calendar','ios_photos','sms','android_device','telegram','stockimo','ios_calendar']
#current_action_services = ['office_365_calendar','ios_photos','sms','android_device','telegram','stockimo','ios_calendar']
#current_action_services = ['dropbox'] #withings
current_trigger_service = 'office_365_mail'
current_trigger = 'Any new email'
trigger_services_count = {}# for counting
for item in itertools.product(trigger_results, action_results):
    trigger_service = item[0][0]
    action_service= item[1][0]
    trigger = item[0][1]
    action = item[1][1]

    if trigger_service == action_service:
        continue
    ############################################################################
    ############################################################################
    if trigger_service.strip() != current_trigger_service.strip() or trigger.strip() != current_trigger:
        continue
    if action_service not in current_action_services:
        continue
    else:
        current_action_services.remove(action_service)
    print(current_trigger_service)
    print(current_action_services)
    ############################################################################
    ############################################################################
    print('################################')
    print('trigger_service: ' + str(trigger_service))
    print('action_service: ' + str(action_service))
    # //////// COMMENT LINE 563 TO TEST PINTEREST
    #if trigger_service in all_auth_details_list and action_service in all_auth_details_list:
    if action_service in all_auth_details_list:
        print('trigger: ' + str(trigger))
        print('trigger: ' + str(action))

        queryresultFound = appletcollection.find({'trigger': trigger, 'action_service': action_service, 'action': action})
        queryresult = []
        for found in queryresultFound:
            queryresult.append(found)
        if len(queryresult) != 0:
            print('already in')
            continue
        try:

            if trigger_service in trigger_services_count:
                trigger_services_count[trigger_service].append(trigger)
            else:
                trigger_services_count[trigger_service] = [trigger]
            # if the trigger count for a trigger service equal the attempt only contine
            if len(list(set(trigger_services_count[trigger_service]))) == attempt:
                ############################################################
                ## with the thread
                # x = x + 1
                # if x % 1 == 0:
                #     time.sleep(30)
                ##################
                if appletcollection.find({}).count() >= 1000:
                    print('thousand applets !!!')
                    e1 = timeit.default_timer()
                    print('Time for applet generation function= ' + str(e1 - s1))
                    break
                ############################################################
                appletGeneration(trigger, trigger_service, action, action_service)
                ## with the thread
                # process = Thread(target=appletGeneration,
                #                  args=[trigger, trigger_service, action, action_service])
                # process.start()
                # threads.append(process)
                #################

        except KeyError:
            print('no trigger_permission')
        except JSONDecodeError:
            print('json error')
            continue

## with the thread
# for process in threads:
#     process.join()
##################





