from builtins import print

import requests
from pprint import pprint
import mysql.connector

#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////

# # ////////////// Check DB for already analysed applet //////////////////
sql = "SELECT * FROM services"
mycursor.execute(sql)
results_values = mycursor.fetchall()
rc = mycursor.rowcount

def permission_process(si, trigger_or_action_permission):
    service_identifier = si
    ingredients = 'NA'
    name_of_trigger_or_action = 'NA'
    desc_of_trigger_or_action = 'NA'
    type_of_trigger_or_action = 'NA'
    field_name = 'NA'
    field_label = 'NA'
    field_required = 'NA'
    field_type = 'NA'
    options = 'NA'
    options_static = 'NA'

    for tp in trigger_or_action_permission:
        t_name = tp['name']
        t_description = tp['description']
        t_fields = tp['fields']
        t_type = tp['type']
        t_module_name = tp['module_name']
        name_of_trigger_or_action = t_name
        desc_of_trigger_or_action = t_description
        type_of_trigger_or_action = t_type

        try:
            t_resolve_ingredients = tp['resolve_ingredients']
            # resolve ingredients
            t_ingredients = None
            if t_resolve_ingredients:
                rq = requests.get('https://buffalo-android.ifttt.com' + str(t_resolve_ingredients), headers=header)
                ingredients_js_dict = rq.json()
                # pprint(ingredients_js_dict)
                t_ingredients = ingredients_js_dict
                for ing in ingredients_js_dict:
                    i_name = ing['name']
                    i_value_type = ing['value_type']
                    i_is_hidden = ing['is_hidden']
                ingredients = str(t_ingredients)
        except KeyError:
            print('action has no resolve ingredients')

        # further analyse configuration info
        fd = 0
        if t_fields:
            for field in t_fields:
                fd += 1
                f = t_fields[field]
                f_field_type = f['field_type']
                f_required = f['required']
                f_name = f['name']
                f_label = f['label']
                f_options_static = f['options_static']

                try:
                    f_resolve_options = f['resolve_options']
                    if f_field_type == 'option':
                        r = requests.get('https://buffalo-android.ifttt.com' + str(f_resolve_options), headers=header)
                        options_js_dict = r.json()
                        # pprint(options_js_dict)
                        options = str(options_js_dict)
                except KeyError:
                    print('no options to resolve')

                options_static = f_options_static
                field_name = f_name
                field_label = f_label
                field_required = f_required
                field_type = f_field_type


                print('service_identifier: ' + service_identifier)
                print('type_of_trigger_or_action: ' + type_of_trigger_or_action)
                print('name_of_trigger_or_action: ' + name_of_trigger_or_action)
                print('desc_of_trigger_or_action: ' + desc_of_trigger_or_action)
                print('ingredients: ' + ingredients)
                print('field_name: ' + field_name)
                print('field_label: ' + field_label)
                print('field_required: ' + str(field_required))
                print('field_type: ' + field_type)
                print('options: ' + options)
                print('options_static: ' + str(options_static))


                # ////////////////Add database record ////////////////////
                sql = "INSERT INTO Service_Configuration (service_identifier,type_of_trigger_or_action, name_of_trigger_or_action,desc_of_trigger_or_action,ingredients,field_name,field_label,field_required,field_type,options,options_static) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
                val = (service_identifier,type_of_trigger_or_action, name_of_trigger_or_action,desc_of_trigger_or_action,ingredients,field_name,field_label,field_required,field_type,options,options_static)
                #mycursor.execute(sql, val)
                #mydb.commit()

                print(mycursor.rowcount, "record inserted.")
                # ////////////////End adding database record /////////////
                ingredients = 'NA'
                field_name = 'NA'
                field_label = 'NA'
                field_required = 'NA'
                field_type = 'NA'
                options = 'NA'
                options_static = 'NA'

        else:
            print('service_identifier: ' + service_identifier)
            print('type_of_trigger_or_action: ' + type_of_trigger_or_action)
            print('name_of_trigger_or_action: ' + name_of_trigger_or_action)
            print('desc_of_trigger_or_action: ' + desc_of_trigger_or_action)
            print('ingredients: ' + ingredients)
            print('field_name: ' + field_name)
            print('field_label: ' + field_label)
            print('field_required: ' + str(field_required))
            print('field_type: ' + field_type)
            print('options: ' + options)
            print('options_static: ' + str(options_static))
            # ////////////////Add database record ////////////////////
            sql = "INSERT INTO b (service_identifier,type_of_trigger_or_action, name_of_trigger_or_action,desc_of_trigger_or_action,ingredients,field_name,field_label,field_required,field_type,options,options_static) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
            val = (service_identifier, type_of_trigger_or_action, name_of_trigger_or_action, desc_of_trigger_or_action,
                   ingredients, field_name, field_label, field_required, field_type, options, options_static)
            #mycursor.execute(sql, val)
            #mydb.commit()

            print(mycursor.rowcount, "record inserted.")
            # ////////////////End adding database record /////////////
            ingredients = 'NA'
            field_name = 'NA'
            field_label = 'NA'
            field_required = 'NA'
            field_type = 'NA'
            options = 'NA'
            options_static = 'NA'


    return;




s = 0
for rv in results_values:
    s += 1
    print(str(s) + '.')
    service_identifier = rv[2]
    # api-endpoint
    URL = "https://buffalo-android.ifttt.com/grizzly/me/diy/services/" + service_identifier

    # sending get request and saving the response as response object
    token = '1b004674987164ecf6ed87c30146aa90b4c21024'
    header = {'Authorization': 'Token token="' + token + '"'}
    r = requests.get(URL, headers=header)
    js_dict = r.json()
    #pprint(js_dict)
    # analyse service details
    try:
        trigger_permission = js_dict['trigger_permissions']
        #pprint(trigger_permission)

        permission_process(service_identifier, trigger_permission)

    except KeyError:
        print('no trigger_permission')


    try:
        action_permissions = js_dict['action_permissions']
        #pprint(action_permissions)
        permission_process(service_identifier, action_permissions)


    except KeyError:
        print('no action_permission')







