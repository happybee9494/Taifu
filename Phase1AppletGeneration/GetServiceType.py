from pymongo import MongoClient

uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
eventDatacollection = db.get_collection('serviceconfigdetails')
all_event_details = eventDatacollection.find({})
################################################################
authDatacollection = db.get_collection('authdetails')
all_auth_details = authDatacollection.find({})

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

print(trigger_results)
for authService in all_auth_details_list:
    print(authService)
    ii = 0
    for item in trigger_results:
        if authService == item[0]:
            ii = ii + 1
            if ii == 1:
                print('is a trigger service !!')
            print(item[1])
    ii2 = 0
    for item2 in action_results:
        if authService == item2[0]:
            ii2 = ii2 + 1
            if ii2 == 1:
                print('is a action service !!')
            print(item2[1])

    print('###########################')
