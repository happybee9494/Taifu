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
token = 'b9c969f8fc4d28c3207ef1b3838c75233e8246c3'
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"', 'Content-Type':'application/json; charset=utf-8'}
###########################################################################

current_trigger_service = 'flickr'
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



############################################################################
############################################################################
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
    try:
        connected = authService['linked']
        if connected:
            all_auth_details_list.append(serviceID)
    except KeyError:
        pass

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
        return '{{PhotoUrl}}'
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
        return  '+*****'
    if cluster_label == 'folder':
        return  'myfolder'
    if cluster_label == 'address':
        return  'e12334'
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
        return  '****@gmail.com'
    if cluster_label == 'command':
        return  'turn on light'
    if cluster_label == 'code or token':
        return  'code123'
    if cluster_label == 'expression':
        return  '([A-Z])\w+/g'
    if cluster_label == 'attachment':
        return  'url to attachment'
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
        return  '****@gmail.com'

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

def triggerConfiguration(event, service):
    print('TRIGGER INPUTS ....')
    # POST fields for preview request
    trigger_fields = {}
    applet_creation_pause_by_trigger = False
    trigger_desc = None
    module_name = None
    trigger_id = None
    try:
        URL_for_trigger_data = "https://buffalo-android.ifttt.com/grizzly/me/diy/services/" + service
        r = requests.get(URL_for_trigger_data, headers=header)
        js_dict = r.json()
        print('########### trigger config 1')
        trigger_id = js_dict['numeric_id']

        graph_url = 'https://ifttt.com/api/v3/graph'
        print('############ get service information:')
        request2_body = {"query": " query {\n  channel(module_name: \""+service+"\") {\n triggers {\n id\nname\ndescription\nfull_module_name\n trigger_fields {\n  name\nlabel\nfield_ui_type\nrequired\nhelper_text\nshareable\nhideable\n                    }\n                }\n            }\n        }"}
        r = requests.post(graph_url, data=json.dumps(request2_body), headers=post_header)
        js_dict = r.json()
        #pprint(js_dict)
        event_name = event.lower().strip().replace(' ', '_')
        print(event_name)
        module_name = service +"."+event_name
        ############################# get fields ###########################
        print('#################### data')
        service_data = js_dict['data']['channel']['triggers']
        #pprint(service_data)
        event_fields_found = False
        event_fields_data = None
        not_shearable_trigger_fields = []
        for data in service_data:
            if data['full_module_name'] == module_name:
                event_fields_data = data
                event_fields_found = True

        if not event_fields_found:
            for data in service_data:
                if data['name'] == event:
                    event_fields_data = data
                    event_fields_found = True

        if event_fields_found:
            fields = event_fields_data['trigger_fields']
            module_name = event_fields_data['full_module_name']
            if fields:
                #pprint(fields)
                # [{'field_ui_type': 'text_field',
                #   'helper_text': '',
                #   'hideable': True,
                #   'label': 'Title',
                #   'name': 'title',
                #   'required': True,
                #   'shareable': True},
                print('no of fields: ' + str(len(fields)))
                for field in fields:
                    is_sherable = field['shareable']
                    if not is_sherable:
                        not_shearable_trigger_fields.append(field['name'])
                    print(is_sherable)
                    field_ui_type = field['field_ui_type'] # type
                    if field_ui_type == 'collection_select':
                        print('##### test statement')
                        request3_body = { "query": "  query {\n  trigger(module_name: \"" + module_name+ "\") {\n  trigger_fields {\n name\noptions {\n label\n value\n  group\n}\n  }\n }\n }"}
                        r = requests.post(graph_url, data=json.dumps(request3_body), headers=post_header)
                        js_dict = r.json()
                        print(r)
                        pprint(js_dict)
                    else:  # text_field  text_area
                        print(field_ui_type)


                    f_helpertext = field['helper_text']
                    f_required = field['required']
                    field_name = field['name']
                    f_label = field['label'].lower()
                    #################################################################################################################
                    # based on field types assign values for the fields
                    if field_ui_type == 'collection_select' or field_ui_type == 'checkbox_multi':
                        print(field_name)

                        try:

                            action_options_body = {
                                "query": "  query {\n  trigger(module_name: \"" + module_name + "\") {\n  trigger_fields {\n name\noptions {\n label\n value\n  group\n}\n  }\n }\n }"}
                            r = requests.post(graph_url, data=json.dumps(action_options_body), headers=post_header)
                            action_options_dict = r.json()
                            print(r)
                            print(action_options_dict)
                            pprint(action_options_dict)
                            options_for_action_fields = action_options_dict['data']['trigger']['trigger_fields']
                            for opt in options_for_action_fields:
                                if opt['name'] == field_name:
                                    if opt['options']:
                                        if field_ui_type == 'checkbox_multi':
                                            trigger_fields[field_name] = [opt['options'][0]['value']]
                                        else:
                                            trigger_fields[field_name] = opt['options'][0]['value']


                        except KeyError:
                            print('no options to resolve')
                    elif field_ui_type == 'double_collection_select':
                        action_options_body = {  "query": "  query {\n  trigger(module_name: \"" + module_name + "\") {\n  trigger_fields {\n name\noptions {\n label\n value\n  group\n}\n  }\n }\n }"}
                        r = requests.post(graph_url, data=json.dumps(action_options_body), headers=post_header)
                        action_options_dict = r.json()
                        print(r)
                        pprint(action_options_dict)
                        options_for_action_fields = action_options_dict['data']['trigger']['trigger_fields']
                        for opt in options_for_action_fields:
                            if opt['name'] == field_name:
                                if opt['options']:
                                    trigger_fields[field_name] = opt['options'][0]['value']
                                    print(opt)
                    elif field_ui_type == 'location':
                        other_field_available = True
                        field_key = field_name
                        value = '1.2966° N, 103.7764° E'  # // nus location
                        trigger_fields[field_key] = value
                    elif field_ui_type == 'location-area':
                        other_field_available = True
                        field_key = field_name
                        value = 'NUS School of Computing, COM1, 13 Computing Drive, 117417'
                        trigger_fields[field_key] = value
                    elif field_ui_type == 'date-and-time':
                        other_field_available = True
                        field_key = field_name
                        value = 'October 23, 2019 at 01:01PM'
                        trigger_fields[field_key] = value
                    elif field_ui_type == 'miniutes-past-hour':
                        other_field_available = True
                        field_key = field_name
                        value = '20'
                        trigger_fields[field_key] = value
                    elif field_ui_type == 'option-multi':
                        other_field_available = True
                    elif field_ui_type == 'text_field' or field_ui_type == 'text_area' :
                        text_type = all_label_details_list[f_label]
                        text_value = getValue(text_type, f_label)
                        print('f_label: ' + str(f_label))
                        other_field_available = True
                        field_key = field_name
                        trigger_fields[field_key] = text_value
                    elif field_ui_type == 'time-of-day':
                        other_field_available = True
                        field_key = field_name
                        value = '01:01PM'
                        trigger_fields[field_key] = value
                #################################################################################################################

        else:
            print('no event fields !')
    except KeyError:
        print('no trigger_permission')
    print(trigger_fields)
    return trigger_fields,event,service,trigger_desc,module_name, applet_creation_pause_by_trigger,trigger_id,not_shearable_trigger_fields

def actionConfiguration(event, service,return_trigger_module_name):
    action_id = None
    action_fields = {}
    action_service_id = None
    request11 = None
    action_desc = None
    applet_creation_pause_by_action = None
    print('ACTION INPUTS...')
    module_name = None
    action_id = None
    try:
        URL_for_trigger_data = "https://buffalo-android.ifttt.com/grizzly/me/diy/services/" + service
        r = requests.get(URL_for_trigger_data, headers=header)
        js_dict = r.json()
        print('########### action')
        action_id = js_dict['numeric_id']
        ########################## init #############################
        graph_url = 'https://ifttt.com/api/v3/graph'
        print('############ get service information:')
        request2_body = {"query": " query {\n  channel(module_name: \""+service+"\") {\n actions {\n id\nname\ndescription\nfull_module_name\n action_fields {\n  name\nlabel\nfield_ui_type\nrequired\nhelper_text\nshareable\nhideable\n                    }\n                }\n            }\n        }"}
        r = requests.post(graph_url, data=json.dumps(request2_body), headers=post_header)
        js_dict = r.json()
        #pprint(js_dict)
        event_name = event.lower().strip().replace(' ', '_')
        print(event_name)
        module_name = service +"."+event_name
        ############################# get fields ###########################
        print('#################### data')
        service_data = js_dict['data']['channel']['actions']
        #pprint(service_data)
        event_fields_found = False
        event_fields_data = None
        not_shearable_action_fields = []
        for data in service_data:
            if data['full_module_name'] == module_name:
                event_fields_data = data
                event_fields_found = True

        if not event_fields_found:
            for data in service_data:
                if data['name'] == event:
                    event_fields_data = data
                    event_fields_found = True

        if event_fields_found:
            fields = event_fields_data['action_fields']
            module_name = event_fields_data['full_module_name']
            print('#### get default field values for action: ######')
            ######## default fields #################
            request5_body = {"query": "  query {\n action(module_name: \""+ module_name +"\") {\n defaults_for_trigger(trigger_module_name: \"" + return_trigger_module_name + "\")"
                              " \n   }\n   \n    \n    \n   trigger(module_name: \"" + return_trigger_module_name + "\") {\n    channel {\n    brand_color\n    name\n    "
                              "lrg_monochrome_image_url\n}\nname\ningredients {\n    id\n    name\n    is_hidden\n  normalized_name\n  value_type\n}\n }\n  }"}
            r2 = requests.post(graph_url, data=json.dumps(request5_body), headers=post_header)
            js_dict2 = r2.json()
            #pprint(js_dict2)
            print(r2)
            defaults_for_trigger = js_dict2['data']['action']['defaults_for_trigger']
            print(defaults_for_trigger)
            action_fields  =  json.loads(defaults_for_trigger)
            #########################################
            #########################################
            have_blank_fields = False
            blank_field_keys = []

            for af, av in action_fields.items():
                if av is '' or av is None:
                    have_blank_fields = True
                    blank_field_keys.append(af)
            print(have_blank_fields)
            print(blank_field_keys)
            #have_blank_fields = False
            if have_blank_fields:
                # pprint(fields)
                # [{'field_ui_type': 'text_field',
                #   'helper_text': '',
                #   'hideable': True,
                #   'label': 'Title',
                #   'name': 'title',
                #   'required': True,
                #   'shareable': True},
                print('no of fields: '+ str(len(fields)))
                for field in fields:
                    print(field)
                    is_sherable = field['shareable']
                    if not is_sherable:
                        not_shearable_action_fields.append(field['name'])
                    print(is_sherable)
                    if field['name'] in blank_field_keys:
                        pass
                    else:
                        continue

                    field_ui_type = field['field_ui_type']
                    field_name = field['name']
                    f_label = field['label'].lower()
                    print(f_label)
                    print(field_ui_type)
                    if field_ui_type == 'collection_select':
                        print(field_name)
                        action_options_body = {  "query": "  query {\n  action(module_name: \"" + module_name + "\") {\n  action_fields {\n name\noptions {\n label\n value\n  group\n}\n  }\n }\n }"}
                        r = requests.post(graph_url, data=json.dumps(action_options_body), headers=post_header)
                        action_options_dict = r.json()
                        print(r)
                        pprint(action_options_dict)
                        options_for_action_fields = action_options_dict['data']['action']['action_fields']
                        for opt in options_for_action_fields:
                            if opt['name'] == field_name:
                                if opt['options']:
                                    if field_ui_type == 'checkbox_multi' or field_ui_type == 'checkbox_multi':
                                        action_fields[field_name] = [opt['options'][0]['value']]
                                    else:
                                        action_fields[field_name] = opt['options'][0]['value']

                    elif field_ui_type == 'double_collection_select':
                        action_options_body = {  "query": "  query {\n  action(module_name: \"" + module_name + "\") {\n  action_fields {\n name\noptions {\n label\n value\n  group\n}\n  }\n }\n }"}
                        r = requests.post(graph_url, data=json.dumps(action_options_body), headers=post_header)
                        action_options_dict = r.json()
                        print(r)
                        pprint(action_options_dict)
                        options_for_action_fields = action_options_dict['data']['action']['action_fields']
                        for opt in options_for_action_fields:
                            if opt['name'] == field_name:
                                if opt['options']:
                                    action_fields[field_name] = opt['options'][0]['value']
                                    print(opt)
                    elif field_ui_type == 'location':
                        other_field_available = True
                        value = '1.2966° N, 103.7764° E'  # // nus location
                        action_fields[field_name] = value
                    elif field_ui_type == 'location-area':
                        other_field_available = True
                        value = 'NUS School of Computing, COM1, 13 Computing Drive, 117417'
                        action_fields[field_name] = value
                    elif field_ui_type == 'date-and-time':
                        other_field_available = True
                        value = 'October 23, 2019 at 01:01PM'
                        action_fields[field_name] = value
                    elif field_ui_type == 'miniutes-past-hour':
                        other_field_available = True
                        value = '20'
                        action_fields[field_name] = value
                    elif field_ui_type == 'option-multi':
                        other_field_available = True
                    elif field_ui_type == 'text_field' or field_ui_type == 'text_area':
                        text_type = all_label_details_list[f_label]
                        text_value = getValue(text_type, f_label)
                        print('f_label: ' + str(f_label))
                        other_field_available = True
                        action_fields[field_name] = text_value
                    elif field_ui_type == 'time-of-day':
                        other_field_available = True
                        value = '01:01PM'
                        action_fields[field_name] = value
                    else: #text_field  text_area
                        print(field_name)


        else:
            print('no event fields !')


    except KeyError:
        print('no action_permission')
    return action_fields,event,service,action_desc,module_name, applet_creation_pause_by_action, action_id,not_shearable_action_fields

def completeAppletGeneration(trigger_fields,trigger,trigger_service, trigger_module_name, trigger_channel, action_fields,action,action_service,action_module_name, action_channel,not_shearable_action_fields,not_shearable_trigger_fields):
    applet_id = None
    applet_desc = None
    applet_title = None
    action_fields_new = {}
    print('########### preview: ')
    #print(json.dumps(trigger_fields))
    #print(json.dumps(action_fields))
    for af, av in action_fields.items():
        action_fields_new[af] = av.replace('\n','')
    print(action_fields_new)
    # print(str(action_fields).replace('\\n',''))
    # print(json.dumps(str(action_fields).replace('\\n','')))
    print('###########')
    #print(json.dumps(trigger_fields).replace('"','\\\\\\"'))
    graph_url = 'https://ifttt.com/api/v3/graph'
    #request6_body =  {"query":"mutation {\n  statementPreview(input:{\n    stored_fields: \"{\\\"trigger\\\":\\\"facebook.your_profile_changes_fb\\\",\\\"action\\\":\\\"android_device.set_device_volume\\\",\\\"trigger_fields\\\":{\\\"field_to_watch\\\":\\\"profile_picture\\\"},\\\"action_fields\\\":{\\\"volume\\\":\\\"{\\\\\\\"volume_level\\\\\\\":0.6,\\\\\\\"name\\\\\\\":\\\\\\\"60%\\\\\\\"}\\\"}}\",\n  }) {\n    normalized_applet {\n      name\n      brand_color\n      service_slug\n      can_push_enable\n    }\n    errors {\n        attribute\n        message\n    }\n  }\n}\n"}
    body = {"trigger":trigger_module_name,"action":action_module_name,"trigger_fields":trigger_fields,"action_fields":action_fields}
    print(json.dumps(body))
    #request6_body =  {"query":"mutation {\n  statementPreview(input:{\n    stored_fields: \"{\\\"trigger\\\":\\\""+trigger_module_name+"\\\",\\\"action\\\":\\\""+action_module_name+" \\\",\\\"trigger_fields\\\":"+json.dumps(trigger_fields).replace('"','\\"')+",\\\"action_fields\\\":{\\\"title\\\":\\\"{{CaptionNoHashtag}}\\\",\\\"labels\\\":\\\"IFTTT, Facebook\\\", \\\"body\\\":\\\"<img src=\\\\\"{{ImageSource}}\\\\\"><br>{{Caption}}<br>Uploaded by {{From}} {{Link}}<br>{{CreatedAt}}\\\"}}\",\n  }) {\n    normalized_applet {\n      name\n      brand_color\n      service_slug\n      can_push_enable\n    }\n    errors {\n        attribute\n        message\n    }\n  }\n}\n"}
    prevw_request_body = { "query": "mutation {\n  statementPreview(input:{\n    stored_fields: \"{\\\"trigger\\\":\\\"" + trigger_module_name + "\\\",\\\"action\\\":\\\"" + action_module_name + " \\\","
                          "\\\"trigger_fields\\\":" + json.dumps(trigger_fields).replace('"', '\\"') + ",\\\"action_fields\\\": " + json.dumps(action_fields_new).replace('"', '\\"') + "}\",\n  }) "
                         "{\n    normalized_applet {\n      name\n      brand_color\n      service_slug\n      can_push_enable\n    }\n    errors {\n        attribute\n        message\n    }\n  }\n}\n"}
    print(prevw_request_body)
    prev_r = requests.post(graph_url, data=json.dumps(prevw_request_body), headers=post_header)
    js_dict_prev = prev_r.json()
    pprint(js_dict_prev)
    print(prev_r)

    preview_error = js_dict_prev['data']['statementPreview']['errors']
    print(preview_error)

    print('##################################################################')
    print('########### Finishing:')
    ####### trigger field preparation ###############################

    if preview_error is None:
        applet_title = js_dict_prev['data']['statementPreview']['normalized_applet']['name']
        print(applet_title)
        trigger_fields_array = ""
        tf_count = 0
        ########### trigger fields ##########
        for tf, tv in trigger_fields.items():
            tf_count = tf_count + 1

            if tf in not_shearable_trigger_fields:
                field = "{hidden: false"
            else:
                field = "{hidden: true"
            field = field + ", name: " + " \"" + tf + "\""
            if type(tv) == list:
                newtv = "\"["
                count_tvv = 0
                for tvv in tv:
                    count_tvv = count_tvv + 1
                    newtv = newtv + "\\\""+  tvv.replace('"', '\\\\\\"') + "\\\""
                    if count_tvv != len(tv):
                        newtv = newtv + ","
                newtv = newtv + "]\""
                field = field + ", value: " + newtv + "}"
            else:
                field = field + ", value: " + " \"\\\"" + tv + "\\\"\"}"
            if tf_count > 1:
                trigger_fields_array = trigger_fields_array + ","
            trigger_fields_array = trigger_fields_array + field
        print(trigger_fields_array)
        # [{name: \"hashtag\",hidden: true, value: \"\\\"ifttt\\\"\"}]
        ####### trigger field preparation ###############################
        action_fields_array = ""
        af_count = 0
        ############## action_Fields ###########
        for af, av in action_fields.items():
            af_count = af_count + 1
            if af in not_shearable_action_fields:
                field = "{hidden: false"
            else:
                field = "{hidden: true"
            field = field + ", name: " + " \"" + af + "\""
            field = field + ", value: " + " \"\\\"" + av.replace('\n', '').replace('"', '\\\\\\"') + "\\\"\"}"
            if af_count > 1:
                action_fields_array = action_fields_array + ","
            action_fields_array = action_fields_array + field
        print('## action fields')
        print(action_fields_array)

        #################################################################

        request7_body = {"query": "  mutation {\n  diyAppletCreate(input:{\n   name: \"" + applet_title + "\","
        "\n   push_enabled: false,\n    channel_id: " + trigger_channel + ",\n  trigger: {\nchannel_id: " + trigger_channel + ",\nstep_identifier: \"" + trigger_module_name + "\","
        "\nfields: [" + trigger_fields_array + "]\n}\n,\n    queries: [], \n  actions: [{\nchannel_id: " + action_channel + ",\nstep_identifier: \"" + action_module_name + "\","
        "\nfields: [" + action_fields_array + "]"
        # "\nfields: [{name: \"title\",hidden: true, value: \"\\\"{{CaptionNoHashtag}}\\\"\"},{name: \"body\",hidden: true, value: \"\\\"IFTTT, Facebook\\\"\"},{name: \"labels\",hidden: true, value:\"\\\"IFTTT, Facebook\\\"\"}]"
        "\n}\n]\n}) "
        "{\n  normalized_applet {\n   id\n  name\n description\n  brand_color\n  monochrome_icon_url\n   author\n   status\n   installs_count\n    push_enabled\n   type\n  "
        " created_at\n  last_run\n  run_count\n   speed\n  config_type\n   by_service_owner\n  background_images {\n  background_image_url_1x\n  background_image_url_2x\n   }"
        "\n   configurations {\n  title\nslug\ndescription\nicon_url\nrequired\nlive_configurations {\n id\n  disabled\n}\n  }\n   applet_feedback_by_user\n   can_push_enable\n "
        "published\n   archived\n  author_tier\n   pro_features\n  service_name\n  channels {\n   id\nmodule_name\nshort_name\nname\ndescription_html\nbrand_color\nmonochrome_image_url"
        "\nlrg_monochrome_image_url\nis_hidden\nconnected\nrequires_user_authentication\ncall_to_action {\n    text\n    link\n}\norganization {\n  tier\n}\n  }"
        "\n  underlying_applet {\n    live_applet {\n    live_applet_triggers {\n    statement_id\n    }\n    }\n   }\n   }\n   errors {\n    attribute\n    message\n  }\n  }\n   }"}
        #pprint(request7_body)
        print('############ call')
        print(request7_body)
        try:

            r = requests.post(graph_url, data=json.dumps(request7_body), headers=post_header)
            js_dict_finsh = r.json()
            pprint(js_dict_finsh)
            print(r)
            finish_error = js_dict_finsh['data']['diyAppletCreate']['errors']
            if finish_error is None:
                applet_id = js_dict_finsh['data']['diyAppletCreate']['normalized_applet']['id']
                applet_title = js_dict_finsh['data']['diyAppletCreate']['normalized_applet']['id']
                appletcollection.update({'applet_id': applet_id},
                                  {'$set': {'applet_title': applet_title, 'finish_response': js_dict_finsh, 'trigger_service': trigger_service,'trigger': trigger,'trigger_fields': trigger_fields,
                                            'action_service': action_service,'action': action, 'action_fields': action_fields}}, upsert=True)
            else:
                errorcollection.update({'action_service': action_service},
                                  {'$set': {'finish_response': js_dict_finsh, 'preview_response': js_dict_prev, 'trigger_service': trigger_service,'trigger': trigger,'trigger_fields': trigger_fields,
                                            'action': action, 'action_fields': action_fields}}, upsert=True)
        except Exception as ex:
            ################### check exception details ####################################################
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            print('exception caught')

    else:
        errorcollection.update({'action_service': action_service},
        {'$set': {'preview_response': js_dict_prev, 'trigger_service': trigger_service,'trigger': trigger,'trigger_fields': trigger_fields,
                                            'action': action, 'action_fields': action_fields}}, upsert=True)



    return applet_id,applet_desc,applet_title

def appletGeneration(trigger, trigger_service, action, action_service):
    push_enabled = None
    request1 = None

    try:
        trigger_fields, trigger_id, trigger_service_id, trigger_desc,  trigger_module_name,applet_creation_pause_by_trigger,trigger_id,not_shearable_trigger_fields = triggerConfiguration(
            trigger, trigger_service)
        action_fields, action_id, action_service_id, action_desc, action_module_name, applet_creation_pause_by_action,action_id,not_shearable_action_fields = actionConfiguration(
            action, action_service, trigger_module_name)


        applet_id, applet_desc, applet_title = completeAppletGeneration(trigger_fields, trigger, trigger_service_id,trigger_module_name, trigger_id, action_fields, action,  action_service_id,action_module_name,action_id,not_shearable_action_fields,not_shearable_trigger_fields)

        #     applet_title = applet_title.replace("'", "''")
        #     updateDBOrDeleteDuplication(appletcollection, applet_title, applet_id, applet_desc, trigger_service,
        #                                 trigger, trigger_desc, trigger_fields, action_service, action, action_desc,
        #                                 action_fields)
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


trigger_services_count = {}# for counting
print(len(current_action_services))
action_services_done = []
for applet in appletcollection.find({}):
    action_services_done.append(applet['action_service'])
print(action_results)
################################################################################################
for item in itertools.product(trigger_results, action_results):
    #continue
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
    if action_service in action_services_done:
        continue
    print(current_trigger_service)
    print(current_action_services)
    ############################################################################
    ############################################################################
    print('################################')
    print('trigger_service: ' + str(trigger_service))
    print('action_service: ' + str(action_service))
    # //////// COMMENT LINE 563 TO TEST PINTEREST
    #if trigger_service in all_auth_details_list and action_service in all_auth_details_list:
    #if action_service in all_auth_details_list:
    if True:
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
                ############### with the thread ###########################
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





