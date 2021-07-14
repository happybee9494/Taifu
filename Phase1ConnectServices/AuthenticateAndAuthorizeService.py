from builtins import  KeyError, property
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import WebDriverException
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
from selenium.webdriver.common.action_chains import ActionChains
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client.get_database('services')
collection = db.get_collection('authdetails')
all_auth_details = collection.find({})
all_credentials_in_db = {}
for x in all_auth_details:
    credentials = []
    credentials.append(x['username'])
    credentials.append(x['password'])
    all_credentials_in_db[x['service_idnetifier']] = credentials
########################################################################################################################
############################################## CONSTANTS ###############################################################
possible_usernames = ['channel','lgn', 'usr', 'usrname', 'user', 'email', 'username', 'phone', 'login', 'loginname', 'user[login]', 'hwid',
                 'identifier',
                 'auth-username', 'mobile/email/login', 'username/email',
                 'user_login',
                 'single_access_token']

two_step_form_navigation_button_name = ['next', 'ok']

login_button_names = ['lgn', 'login', 'signin', 'authorize']

authorize_names = ['authorize', 'allow','approve','agree','okay','yes', 'ok','accept']#done

button_class_name = ['button', 'btn', 'submit']

list_of_not_values = ['social', 'facebook', 'google']

list_of_not_link_texts = ['terms','privacy','back', 'here', 'signup', 'register', 'password','forgotten', 'legal notice', 'data','policy', 'cookie','policy', 'help',
                 'create', 'new' ,'account',
                 'help', 'not', 'now', 'about', 'learn',
                 'developers',
                 'careers','adchoices','settings','services','site','about', 'inc.','home','page','skip','agreement','contact']
########################################################################################################################
################################################## FORMS ###############################################################
def formfindElementByIDorNAMEandSendKeys(element, data, string):
    success = ""
    foundElement = None
    try:
        try:
            foundElement = browser.find_element_by_id(element['id'])
            #foundElement = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.ID, element['id'])))
            foundElement.send_keys(data)
            print(string + ' by id filled')
            success = "True"
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(data)
                print(string + 'by name filled')
                success = "True"
            except KeyError:
                print(string + ' by name not exists !')
    except ElementNotVisibleException:
        print('element not visible')
        try:
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(data)
                print(string + 'by name filled')
                success = "True"
            except KeyError:
                print(string + ' by name not exists !')
        except ElementNotVisibleException:
            print('element not visible')
    return success,foundElement
def formfindElementByIDorNAMEandSendKeysANDsubmit(element, data, string):
    success = ""
    found,foundElement = formfindElementByIDorNAMEandSendKeys(element, data, string)

    if bool(found):
        foundElement.submit()
        print('Form submitted')
        success = "True"
        time.sleep(2)
    return success
def formfindElementByXPATHandSendKeys(xpathText, data, string):
    success = ""
    foundElement = None
    try:
        foundElement = browser.find_element(By.XPATH, xpathText)
        foundElement.send_keys(data)
        print(string +' by xpath filled')
        success = "True"
    except KeyError:
        print(string +' filed by xpath not exists !')
    return success,foundElement
def formfindElementByXPATHandSendKeysANDsubmit(xpathText, data, string):
    success = ""
    found, foundElement = formfindElementByXPATHandSendKeys(xpathText, data, string)
    if bool(found):
        foundElement.submit()
        print('Form submitted')
        success = "True"
        time.sleep(2)
    return success
def formfindElementByIDorNAMEandSubmit(element, string):
    success = ""
    foundElement = None
    try:
        try:
            foundElement = browser.find_element_by_id(element['id'])
            success = "True"
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                success = "True"
            except KeyError:
                print(string + ' by name not exists !')
    except ElementNotVisibleException:
        print('element not visible')
        try:
            try:
                foundElement = browser.find_element_by_name(element['name'])
                success = "True"
            except KeyError:
                print(string + ' by name not exists !')
        except ElementNotVisibleException:
            print('element not visible')
    if bool(success):
        foundElement.submit()
        print('Navigate submitted')
        success = "True"
        time.sleep(2)
    else:
        success = ""
    return success
def func_form_process(forms, list,inputs, buttons, applet_page_content, isusernameset):
    login_type = 'Form submitted'
    usernameFilled = isusernameset
    passwordFilled = ""
    m = 0
    print('Form processing .....')
    for f in forms:
        print('//////////////////////////////////////////////////')
        m += 1
        print('form: ' + str(m))
        try:
            if f['type'] == 'hidden':
                print('hidden form !')
                continue
        except KeyError:
            print('no type key in form')
        print('//////////////////////////////////////////////////')
        text_input = f.findChildren("input", attrs={"type": "text"}, recursive=True)
        email_input = f.findChildren("input", attrs={"type": "email"}, recursive=True)
        password_input = f.findChildren("input", attrs={"type": "password"}, recursive=True)
        hidden_input = f.findChildren("input", attrs={"type": "hidden"}, recursive=True)
        submit_input = f.findChildren("input", attrs={"type": "submit"}, recursive=True)
        submit_input2 = f.findChildren("input", attrs={"type": "Submit"}, recursive=True)
        remain_input = f.findChildren("input", recursive=True)
        time.sleep(5)
        # print(text_input)
        # print(email_input)
        # print(password_input)
        # print(hidden_input)
        # print(submit_input)
        # print(remain_input)
        if not text_input and not email_input and not password_input:
            return func_div_input_process(inputs, buttons, applet_page_content, list)

        # ########################## If IFTTT connected by one button click ############################################
        if len(text_input) == 0 and len(email_input) == 0 and len(password_input) == 0 and len(text_input) == 0:
            for sb in submit_input:
                if sb['name'] == 'commit':
                    print('simply connect')
                    browser.find_element_by_name(sb['name']).submit()
                    print('Form submitted')
                    time.sleep(10)
                    login_type = 'simply connect'
                    return login_type


        # ##################################### If type of input is email ##############################################
        if not bool(usernameFilled):
            for ei in email_input:
                print('Find username 0')
                usernameFilled = formfindElementByIDorNAMEandSendKeys(ei, list[0], 'username')
                if not bool(usernameFilled):
                    print('email name not exists !')
                    usernameFilled = formfindElementByXPATHandSendKeys("//input[@type='email']", list[0], 'username')

        # ##########################  If type of input is username related KEYWORD ######################################
        if not bool(usernameFilled):
            try:
                print('Find username 1')
                for ri in remain_input:
                    if ri not in email_input:
                        type_value = ri['type'].lower().replace(' ', '')
                        if any(ext in type_value for ext in possible_usernames):
                            print('different type found with a keyword')
                            try:
                                name = ri['name'].lower().replace(' ', '')
                                if any(ext in name for ext in possible_usernames):
                                    usernameFilled = formfindElementByIDorNAMEandSendKeys(ri, list[0], 'username')
                            except KeyError:
                                print('name not exists !')
                                id = ri['id'].lower().replace(' ', '')
                                if any(ext in id for ext in possible_usernames):
                                    usernameFilled = formfindElementByIDorNAMEandSendKeys(ri, list[0], 'username')
            except KeyError:
                print('no type key')


        # ################################## If placehodler exists   ###################################################
        if not bool(usernameFilled):
            for ri in remain_input:
                print('Find username 3')
                if ri not in hidden_input:
                    if ri not in password_input:
                        if ri not in email_input:
                            if ri not in text_input:
                                if ri not in submit_input:
                                    if ri not in submit_input2:
                                        print('remain input')
                                        print(ri)
                                        try:
                                            placeholder = ri['placeholder'].lower().replace(' ', '')
                                            if any(ext in placeholder for ext in possible_usernames):
                                                xpathtext = "//input[@placeholder='" + ri['placeholder'] + "']"
                                                usernameFilled = formfindElementByXPATHandSendKeys(xpathtext, list[0], 'username')
                                        except KeyError:
                                            print('placeholder not exists !')
        # ################### If text input type has other attrinbutes with username/password KEYWORDS #################
        for ti in text_input:
            print('Find username 4')
            try:
                name = ti['name'].lower().replace(' ', '')
                # #################### (1) check for username related KEYWORDS by name##################################
                if not bool(usernameFilled):
                    if any(ext in name for ext in possible_usernames):
                        usernameFilled = formfindElementByIDorNAMEandSendKeys(ti, list[0], 'username')
                # #################### (1) check for password related KEYWORDS #########################################
                if bool(usernameFilled):
                    if 'password' in name:
                        try:
                            pswrd = browser.find_element_by_name(ti['name'])
                            pswrd.send_keys(list[1])
                            browser.find_element_by_name(ti['name']).submit()
                            print('password by name filled')
                            print('Form submitted')
                            passwordFilled = "True"
                            return login_type
                        except KeyError:
                            print('password name not exists !!')
            except KeyError:
                print('name not exists !!')
            # #################### (1) check for username related KEYWORDS by placeholder ##########################
            if not bool(usernameFilled):
                try:
                    placeholder = ti['placeholder'].lower().replace(' ', '')
                    if any(ext in placeholder for ext in possible_usernames):
                        xpathtext = "//input[@placeholder='" + ti['placeholder'] + "']"
                        usernameFilled = formfindElementByXPATHandSendKeys(xpathtext, list[0], 'username')
                except KeyError:
                    print('place holder not exist in text input')

            # #################### (1) check for username related KEYWORDS by id ##########################
            if not bool(usernameFilled):
                try:
                    id = ti['id'].lower().replace(' ', '')
                    if any(ext in id for ext in possible_usernames):
                        usernameFilled = formfindElementByIDorNAMEandSendKeys(ti, list[0], 'username')
                except KeyError:
                    print('key error')


        # #################################### FILL  PASSWORDS #########################################################
        if bool(usernameFilled) and not bool(passwordFilled):
            try:
                print('Find Password 2')
                for pi in password_input:
                    passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(pi, list[1], 'password')

                    if bool(passwordFilled):
                        return login_type
                    else:
                        xpathtext = "//input[@type='password']"
                        passwordFilled = formfindElementByXPATHandSendKeysANDsubmit(xpathtext, list[1], 'password')
                        if bool(passwordFilled):
                            return login_type
            except ElementNotVisibleException:
                print('ElementNotVisible exception ...')
        # ################################### check passcode exists ####################################################
        if bool(usernameFilled) and not bool(passwordFilled):
            try:
                print('Find Pasword 3')
                for p in text_input:
                    if not bool(passwordFilled):
                        try:
                            pname = p['name'].lower().replace(' ', '')
                            # #################### (1) check for passcode by name ######################################
                            if not bool(usernameFilled):
                                if 'passcode' in pname:
                                    passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(p, list[1], 'passcode')
                                    if bool(passwordFilled):
                                        return login_type
                        except KeyError:
                            print('no passcode by name')

                    if not bool(passwordFilled):
                        try:
                            pid = p['id'].lower().replace(' ', '')
                            # #################### (2) check for passcode by id ########################################
                            if not bool(usernameFilled):
                                if 'passcode' in pid:
                                    passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(p, list[1], 'passcode')
                                    if bool(passwordFilled):
                                        return login_type
                        except KeyError:
                            print('no passcode by id')
            except ElementNotVisibleException:
                print('ElementNotVisible exception ...')
        # ################################### No PASSWORD means TWO STEP FORM #########################################
        ###############################################################################################################

        if not bool(passwordFilled):
            navigate = ""
            ######## Press Next or Navaigation buttion #################################################################
            if not bool(navigate):
                navigate = allElementDiscoveryAndClickIfExist(inputs, two_step_form_navigation_button_name)
            if not bool(navigate):
                navigate = allElementDiscoveryByElementTextAndClickIfExist(buttons, "button", two_step_form_navigation_button_name)
            ############### Find password in form inputs ###############################################################
            if bool(navigate):
                time.sleep(20)
                applet_page_response = browser.page_source
                applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
                forms = applet_page_content.findAll('form', recursive=True)
                inputs = applet_page_content.findAll('input', recursive=True)
                buttons = applet_page_content.findAll('button', recursive=True)
                return func_form_process(forms, data_list, inputs, buttons, applet_page_content, "True")
         # ######################################### END ###############################################################
    return 'NOT success login by form'
########################################################################################################################
################################################ DIV FORMS #############################################################
def divFormfindElementByIDorNAMEandSendKeys(element, data, string):
    success = False
    foundElement = None
    try:
        try:
            foundElement = browser.find_element_by_id(element['id'])
            foundElement.send_keys(Keys.CONTROL + "a")
            foundElement.send_keys(Keys.DELETE)
            foundElement.send_keys(data)
            print(string + ' by id filled')
            success = True
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(Keys.CONTROL + "a")
                foundElement.send_keys(Keys.DELETE)
                foundElement.send_keys(data)
                print(string + 'by name filled')
                success = True
            except KeyError:
                print(string + ' by name not exists !')
    except ElementNotVisibleException:
        print('element not visible')
        try:
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(Keys.CONTROL + "a")
                foundElement.send_keys(Keys.DELETE)
                foundElement.send_keys(data)
                print(string + 'by name filled')
                success = True
            except KeyError:
                print(string + ' by name not exists !')

        except ElementNotVisibleException:
            print('element not visible')
    return success,foundElement
def divFormfindElementByXPATHandSendKeys(xpathText, data, string):
    success = False
    foundElement = None
    try:
        foundElement = browser.find_element(By.XPATH, xpathText)
        foundElement.send_keys(Keys.CONTROL + "a")
        foundElement.send_keys(Keys.DELETE)
        foundElement.send_keys(data)
        print(string +' by xpath filled')
        success = True
    except KeyError:
        print(string +' filed by xpath not exists !')
    return (success,foundElement)
def func_div_input_process(inputs, buttons, page,list ):
    print('Div input processing ....')
    password_done = False
    username_done = False
    login_type = 'div form submitted'
    for i in inputs:
        try:
            if i['type'] == 'hidden':
                continue
        except KeyError:
            print('no hidden type')
        ########################################## USERNAME ############################################################
        ################################ If type is text ###############################################################
        try:
            try:
                if i['type'] == 'text':
                    # ############################# If type of DIV is text search by name ##############################
                    try:
                        name = i['name'].lower().replace(' ', '')
                        if any(ext in name for ext in possible_usernames):
                            username_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[0], 'username')
                    except KeyError:
                        print('no key')
                    # ############################# If type of DIV is text search by placeholder########################
                    if not username_done:
                        try:
                            if i['placeholder']:
                                placeholder = i['placeholder'].lower().replace(' ', '')
                                if any(ext in placeholder for ext in possible_usernames):
                                    xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
                                    username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[0],'username')
                        except KeyError:
                            print('placeholder key not exists !')
                    # ##################################  SUMBIT password ###############################################
                    if username_done:
                        if 'password' in i['name']:
                            password_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[1],'password')
                            if password_done:
                                return login_type
            except KeyError:
                print('name not exists !')
                ################################ If attribute with KEYWORD #############################################
                if not username_done:
                    for attr in i.attrs:
                        if type(i[attr]) == list:
                            for at in i[attr]:
                                if any(ext in at for ext in possible_usernames):
                                    xpathtext = "//input[@" + attr + "= '" + i[attr] + "']"
                                    username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[0],'username')

                        else:
                            if any(ext in i[attr] for ext in possible_usernames) and not username_done:
                                xpathtext = "//input[@" + attr + "= '" + i[attr] + "']"
                                username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[0],'username')
        except NoSuchElementException:
            print('no such element')
        ################################ If type is email ##############################################################
        if not username_done:
            try:
                try:
                    if i['type'] == 'email':
                        # ############################# If type of DIV is text search by name ##########################
                        try:
                            name = i['name'].lower().replace(' ', '')
                            if any(ext in name for ext in possible_usernames):
                                username_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[0],'username')
                        except KeyError:
                            print('no key')
                        # ############################# If type of DIV is text search by placeholder####################
                        if not username_done:
                            try:
                                if i['placeholder']:
                                    placeholder = i['placeholder'].lower().replace(' ', '')
                                    if any(ext in placeholder for ext in possible_usernames):
                                        xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
                                        username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[0],'username')
                            except KeyError:
                                print('placeholder key not exists !')
                        # ##################################  SUMBIT password ##########################################
                        if username_done:
                            if 'password' in i['name']:
                                password_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[1],'password')
                                if password_done:
                                    return login_type
                except KeyError:
                    print('no key')
            except NoSuchElementException:
                print('no such element')

        ##############################################PASSWORD #########################################################
        ################################ If type is pasword ############################################################
        if username_done:
            try:
                try:
                    if i['type'] == 'password':
                        # ############################# If type is password find by id or name #########################
                        password_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[1], 'password')
                        # ############################# If type is password find by placeholder#########################
                        if not password_done:
                            try:
                                if i['placeholder']:
                                    placeholder = i['placeholder'].lower().replace(' ', '')
                                    if 'password' in placeholder:
                                        xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
                                        password_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext,list[1],'password')
                                        if password_done:
                                            return login_type
                            except KeyError:
                                print('placeholder key not exists !')
                        # ############################# If type is password find by xpath###############################
                        if not password_done:
                            xpathtext = "//input[@type='password']"
                            password_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[1],'password')
                            if password_done:
                                return login_type
                except KeyError:
                    print('no key')
            except NoSuchElementException:
                print('no such element')

    ####################################################################################################################
    ####################################################################################################################
    ########################### SUMBIT div form ########################################################################
        if password_done:
            ################################ If div type is button #####################################################
            if i['type'] == 'button':
                try:
                    try:
                        print(i['value'])
                        if any(ext in i['value'].lower().replace(' ', '') for ext in login_button_names):
                            try:
                                browser.find_element_by_xpath("//input[@id='" + i['id'] + "']").click()
                                print('Form submitted')
                                return login_type
                            except KeyError:
                                print('button id not exists !')
                    except KeyError:
                        print('value key not exists')
                except KeyError:
                    print('button by type not exists !')

            ################################ If BUTTONS exists #########################################################
            for button in buttons:
                print('button exists')
                social_button = False
                for attr in button.attrs:
                    if type(button[attr]) == list:
                        for at in button[attr]:
                            print(at)
                            if any(ext in at for ext in list_of_not_values):
                                print('social button found !!!!!')
                                social_button = True
                    else:
                        if any(ext in button[attr] for ext in list_of_not_values):
                            print('social button found !!!!!')
                            social_button = True
                # ######################################################################################################
                if social_button:
                    continue
                # ######################################################################################################
                if button.text:
                    print(button.text)
                    if not any(ext in button.text.lower().replace(' ', '') for ext in list_of_not_values):
                        if any(ext in button.text.lower().replace(' ', '') for ext in login_button_names):
                            try:
                                print(button)
                                browser.find_element_by_xpath("//button[@id='" + button['id'] + "']").click()
                                print('Form submitted')
                                return login_type
                            except KeyError:
                                print('button id not exists !')
                                try:
                                    print('came here name')
                                    browser.find_element_by_xpath(
                                        "//button[@name='" + button['name'] + "']").click()
                                    print('Form submitted')
                                    return login_type
                                except KeyError:
                                    print('button name not exists !')
                                    try:
                                        strg = button['class']
                                        if any(ext in strg[0].lower() for ext in button_class_name):
                                            try:
                                                print("//button[contains(text(), '" + button.text + "')]")
                                                button_lst = browser.find_elements_by_xpath("//*[contains(text(), '" + button.text + "') and  not(contains(text(), 'google')) and  not(contains(text(), 'Google')) and  not(contains(text(), 'facebook')) and  not(contains(text(), 'Facebook'))]")
                                                print(button_lst)

                                                for bl in button_lst:
                                                    bl.click()
                                                    print('Form submitted')
                                                    return login_type
                                            except KeyError:
                                                print('button by text not exists !')
                                                browser.find_element_by_class_name(strg[0]).click()
                                                print('Form submitted')
                                                return login_type
                                    # ##################################################################################
                                    except KeyError:
                                        print('button class not exists !')
                                        try:
                                            print("//button[contains(text(), '" + button.text + "')]")
                                            button_lst = browser.find_elements_by_xpath(
                                                "//*[contains(text(), '" + button.text + "')]")
                                            for bl in button_lst:
                                                bl.click()
                                                print('Form submitted')
                                                return login_type
                                        except KeyError:
                                            print('button by text not exists !')
            ####################################If NO BUTTONS exists####################################################
            if not buttons:
                divs = page.findAll('div', recursive=True)
                for div in divs:
                    print('came here div')
                    try:
                        class_name = div['class']
                        if class_name:
                            class_name = class_name[0].lower().replace(' ', '')
                        if any(ext in class_name for ext in button_class_name):
                            if not any(ext in class_name for ext in list_of_not_values):
                                print('has button')
                                browser.find_element_by_class_name(class_name).click()
                                return login_type
                    except KeyError:
                        print('no such key')
                        try:
                            id_name = div['id']
                            if id_name:
                                id_name = id_name.lower().replace(' ', '')
                            print(id_name)
                            if any(ext in id_name for ext in button_class_name):
                                if not any(ext in id_name for ext in list_of_not_values):
                                    print('has button')
                                    browser.find_element_by_id(div['id']).click()
                                    print('Form submitted')
                                    return login_type
                        except KeyError:
                            print('no such key')

                ####################################If LINK BUTTONS exists #############################################
                button_links = page.findAll('a', recursive=True)
                for link in button_links:
                    try:
                        class_name = link['class']
                        if class_name:
                            class_name = class_name[0].lower().replace(' ', '')
                        if any(ext in class_name for ext in button_class_name):
                            if not any(ext in class_name for ext in list_of_not_values):
                                print('has link button')
                                if any(ext in link.text.lower().replace(' ', '') for ext in login_button_names):
                                    browser.find_element_by_link_text(link.text).click()
                                    print('Form submitted')
                                    return login_type
                    except KeyError:
                        print('no such key')

        # ######################################### END ###############################################################
    return 'NOT success login by div form'
########################################################################################################################
################################################ GOOGLE FORMS ##########################################################
def func_process_google_login(div_input, button, list):

    email_filled = False
    password_filled = False
    email_submitted = False
    password_submitted = False
    login_type = None
    has_email_field = False
    for div in div_input:
        if div['type'] == 'email':
            has_email_field = True

    # ##################################################################################################################
    # Once a google service is authenticated, have to select 'use another account', Otherwise the form implementation affects
    if not has_email_field:
        try:
            browser.find_element_by_xpath("//div[contains(text(), '" + 'Use another account' + "')]").click()
            print('use another account clicked')
            time.sleep(5)
            applet_page_response = browser.page_source
            applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
            div_input = applet_page_content.findAll('input', recursive=True)

        except WebDriverException:
            print('WebDriverException at ')
    # ###################################################################################################################

    # ###################################################################################################################
    # ###################################################################################################################
    # Process rest of the input fields in order
    for i in div_input:
        # ############################ First Username ###################################################################
        if i['type'] == 'email':
            try:
                WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, i['id']))).send_keys(list[0])
                print('email find by id filled')
                email_filled = True
            except KeyError:
                print('email id not exists !')
                try:
                    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.NAME, i['name']))).send_keys(list[0])
                    print('email find by name filled')
                    email_filled = True
                except KeyError:
                    print('email name not exists !')
        try:
            if email_filled and not email_submitted:
                print(i)
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='" + 'identifierNext' + "']"))).send_keys(Keys.RETURN)
                print('email submitted')
                email_submitted = True
        except WebDriverException:
            print('WebDriverException at email submitted')

        # ############################ Second Password ###################################################################
        try:
            if email_submitted:
                WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='" + 'password' + "']"))).send_keys(list[1])
                print('password filled')
                password_filled = True
        except WebDriverException:
            print('WebDriverException at password filled')
        try:
            if password_filled and not password_submitted:
                x = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='" + 'passwordNext' + "']")))
                x.send_keys(Keys.RETURN)
                print('password submitted')
                password_submitted = True
                login_type = 'form_submitted_count'
                if email_submitted and password_submitted:
                    return  login_type

        except WebDriverException:
            print('WebDriverException at Form submitted')

    return login_type
########################################################################################################################
############################################### AUTHENTICATION #########################################################
def authentication(browser,data_list):
    print('start authentication...')
    #print(browser.page_source)
    login_type = None

    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    forms = applet_page_content.findAll('form', recursive=True)
    inputs = applet_page_content.findAll('input', recursive=True)
    buttons = applet_page_content.findAll('button', recursive=True)
    google_text_divs = applet_page_content.findAll('div', recursive=True)
    a_links = applet_page_content.findAll('a', recursive=True)
    google_text = False

    #////////////// find button_click to form/sso
    # if not forms:
    input_size = len(inputs)
    c = 0
    for input in inputs:
        if input['type'] == 'hidden':
            c += 1

    #if not forms and c == input_size: #all inputs are hidden
    if c == input_size: #all inputs are hidden
        if buttons:
            print('no forms, no inputs but has buttons')
            print(buttons)
            for button in buttons:
                if any(ext in button.text for ext in login_button_names):
                    print('has only button on first page')
        else:
            if a_links:
                print('no forms, no inputs, no buttons but has links')
                related_links = []
                for link in a_links:
                    print(link['href'])
                    if any(ext in link['href'] for ext in ['login','auth']):
                        if not any(ext in link['href'] for ext in ['language']):
                            related_links.append(link)
                if related_links:
                    print('has related links')
                    print(related_links[0])
                    browser.find_element(By.XPATH, "//a[@href='" + related_links[0]['href'] + "']").click()
                    time.sleep(20)
                    new_page = browser.page_source
                    applet_page_content = BeautifulSoup(new_page, "html.parser")
                    forms = applet_page_content.findAll('form', recursive=True)
                    inputs = applet_page_content.findAll('input', recursive=True)
                    buttons = applet_page_content.findAll('button', recursive=True)
                    google_text_divs = applet_page_content.findAll('div', recursive=True)
                    print('after button click analysis')

    print(google_text)
    #////////// find google sso
    if 'To continue' in applet_page_response or 'Continue to'in applet_page_response:
        google_text = True
        print('Google Sign In')



    # ##################################################################################################################
    if not google_text:
        if forms and inputs:
            try:
                try:
                    try:
                        try:
                            try:
                                return func_form_process(forms, data_list,inputs, buttons, applet_page_content,"")
                            except KeyError:
                                print(' no key!')
                        except ElementNotVisibleException:
                            print('element not visible')

                    except NoSuchElementException:
                        print('no such element')

                except MoveTargetOutOfBoundsException:
                    print('MoveTargetOutOfBoundsException')
                    login_type = 'possible_button_click_to_form'

            except WebDriverException:
                print('MoveTargetOutOfBoundsException')
                login_type = 'permission_denied_count'

    # ##################################################################################################################
    if not forms:
        if inputs:
            try:
                try:
                    try:
                        try:
                            try:
                                return func_div_input_process(inputs, buttons, applet_page_content, data_list)
                            except KeyError:
                                print('no key!')
                        except ElementNotVisibleException:
                            print('element not visible')

                    except NoSuchElementException:
                        print('no such element')

                except MoveTargetOutOfBoundsException:
                    print('MoveTargetOutOfBoundsException')
                    login_type = 'possible_button_click_to_form'

            except WebDriverException:
                print('MoveTargetOutOfBoundsException')
                login_type = 'permission_denied_count'

    # ##################################################################################################################
    # This one works on Firfox browser
    if google_text:
        print('Sign in with Google...')
        div_input = applet_page_content.findAll('input', recursive=True)
        div_button = applet_page_content.findAll('div', {'role': 'button'}, recursive=True)
        form_submitted_count = func_process_google_login(div_input, div_button,data_list)
        login_type = 'sign_with_google_count'
        return login_type
    google_text = False
    # ##################################################################################################################
    done_page = applet_page_content.findAll('div',attrs={"class":"center_text"}, recursive=True)
    for dp in done_page:
        links = dp.findChildren("a",attrs={"class":"btn-primary"},  recursive=True)
        for al in links:
            print('auto connected')
            login_type = 'auto_connect_count'

    if not done_page:
        if not forms:
            if not inputs:
                print('No forms no inputs available ')
                try:
                    try:
                        try:
                            try:
                                try:
                                    browser.find_element(By.XPATH, "//a[@href='" + related_links[0]['href'] + "']").click()
                                    time.sleep(20)
                                    form_page_response = browser.page_source
                                    form_page_content = BeautifulSoup(form_page_response, "html.parser")
                                    forms = form_page_content.findAll('form', recursive=True)
                                    return func_form_process(forms, data_list, inputs, buttons, applet_page_content,"")
                                except KeyError:
                                    print('no key!')
                            except ElementNotVisibleException:
                                print('element not visible')

                        except NoSuchElementException:
                            print('no such element')

                    except MoveTargetOutOfBoundsException:
                        print('MoveTargetOutOfBoundsException')
                        login_type = 'possible_button_click_to_form'

                except WebDriverException:
                    print('MoveTargetOutOfBoundsException')
                    login_type = 'permission_denied_count'
    return login_type
########################################################################################################################
################################################ AUTHROIZATION #########################################################
def findElementAndClickIfExist(attribute, element,func_possible_name_list):
    try:
        if type(element[attribute]) is str:
            att = element[attribute].lower().replace(' ', '')
            if any(ext in att for ext in func_possible_name_list):
                try:
                    try:
                        if attribute == 'id':
                            WebDriverWait(browser, 40).until(
                                EC.element_to_be_clickable((By.ID, element['id']))).send_keys(
                                Keys.RETURN)
                            return 'success'
                        if attribute == 'class':
                            WebDriverWait(browser, 40).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, element['class']))).send_keys(Keys.RETURN)
                            return 'success'
                        if attribute == 'name':
                            WebDriverWait(browser, 40).until(
                                EC.element_to_be_clickable((By.NAME, element['name']))).send_keys(Keys.RETURN)
                            return 'success'
                    except TimeoutException:
                        return 'timeout'
                except KeyError:
                    return 'no key'
        else:
            return 'attr not str'

    except KeyError:
        print('key error')
        return 'no key'
def allElementDiscoveryAndClickIfExist(elements,func_possible_name_list):
    for element in elements:
        if findElementAndClickIfExist('id', element,func_possible_name_list) != 'success':
            if findElementAndClickIfExist('class', element,func_possible_name_list) != 'success':
                if findElementAndClickIfExist('name', element,func_possible_name_list) != 'success':
                    if findElementAndClickIfExist('value', element,func_possible_name_list) != 'success':
                        print('no id class or name in input')
                    else:
                        return 'authorized'
                else:
                    return 'authorized'
            else:
                return 'authorized'
        else:
            return 'authorized'
    return ""
def allElementDiscoveryByElementTextAndClickIfExist(elements,string,func_possible_name_list):
    for element in elements:
        if element.text:
            print(element.text)
            if any(ext in element.text.lower().replace(' ', '') for ext in func_possible_name_list):
                try:
                    xpathtext = "//"+string+"[.='"+element.text+"']"
                    WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.XPATH, xpathtext))).send_keys(Keys.RETURN)
                    return 'authorized'
                except TimeoutException:
                    print('no button text')
        if findElementAndClickIfExist('id', element,func_possible_name_list) != 'success':
            if findElementAndClickIfExist('class', element,func_possible_name_list) != 'success':
                if findElementAndClickIfExist('name', element,func_possible_name_list) != 'success':
                    print('no id class or name in button')
                else:
                    return 'authorized'
            else:
                return 'authorized'
        else:
            return 'authorized'
    return ""
def authorize():
    print('start authorizing...')
    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    inputs = applet_page_content.findAll('input', recursive=True)
    buttons = applet_page_content.findAll('button', recursive=True)
    divs = applet_page_content.findAll('div', recursive=True)
    a_links = applet_page_content.findAll('a', recursive=True)
    print(inputs)
    print(buttons)
    # print(divs)
    print(a_links)
    authorized = ""

    # check if any element has name, id, text, or class as in authorize_names then click on it to authorize IFTTT

    if not bool(authorized):
        authorized = allElementDiscoveryAndClickIfExist(inputs,authorize_names)
    if not bool(authorized):
        authorized = allElementDiscoveryAndClickIfExist(divs,authorize_names)
    if not bool(authorized):
        authorized = allElementDiscoveryByElementTextAndClickIfExist(buttons,"button",authorize_names)
    if not bool(authorized):
        return allElementDiscoveryByElementTextAndClickIfExist(a_links,"a",authorize_names)
########################################################################################################################
########################################################################################################################
############################################ START ANALYSIS ############################################################
########################################################################################################################
def getActivationList():
    href_list = []
    browser.get('https://ifttt.com/channels/activation_list?is_web_view=1')
    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    list_div = applet_page_content.find('div', {'id': 'channel_activation_list'})
    a_list = list_div.findChildren("a", recursive=True)
    for a in a_list:
        href_list.append(a['href'])

    return href_list
########################################################################################################################
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


username.send_keys("****@gmail.com")
password.send_keys("*****")

browser.find_element_by_name("commit").click()
href_list = getActivationList()
########################################################################################################################
################################################ ANALYZING'''' #########################################################

for k, v in all_credentials_in_db.items():
    # if k != 'chatwork':
    #     continue
    # if k == 'tumblr' or k== 'weebly' or k=='wordpress' or k=='inoreader'  or k=='pinboard'or k=='buffer'or k=='airpatrol'or k=='chatwork':
    #     continue
    serviceID = k
    activation_line = '/channels/'+ serviceID+'/activate?is_web_view=1'
    print(activation_line)

    if activation_line in href_list:
        continue
        data_list = all_credentials_in_db[k]
        browser.get('https://ifttt.com/' + activation_line)
        time.sleep(20)  # mandatory wait for the page load
        ################################################################################################################
        ######################################### AUTHENTICATION #######################################################
        login_type = authentication(browser, data_list).strip(' ')
        print('login type = '+login_type)
        #print(browser.page_source)
        ################################################################################################################
        ######################################### AUTHORIZATION# #######################################################
        if login_type == 'sign_with_google_count':
            WebDriverWait(browser, 100).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='" + 'submit_approve_access' + "']"))).send_keys(Keys.RETURN)
            # Warning: if continue to sing in with google then may get TimeOutExcption
            print('Clicked allowed')
            time.sleep(5) # Wait for the allow to be clicked and loading the new page
        # if 'connected' in browser.page_source:
        #     collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}},
        #                                    upsert=True)
        #     print('db updated as connected')
        if  (login_type != 'simply connect') and(login_type != 'permission_denied_count') and (login_type != 'NOT success login by form') and (login_type != 'NOT success login by div form') and (login_type != 'sign_with_google_count'):
            time.sleep(7)
            authorize()
            time.sleep(5)
            if 'connected' in browser.page_source:
                collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}},
                                               upsert=True)
                print('db updated as connected')
        ############################################ confirm ###########################################################
        updated_href_list = getActivationList()
        new_activation_line = '/channels/' + k + '/reactivate?is_web_view=1'
        if new_activation_line in updated_href_list:
            collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}},
                                           upsert=True)
            print('db confirm and updated as connected')
        else:
            collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": False}},
                                           upsert=True)
            print('db confirm and rollback changes')


    else:
        print('already connected')
        for service in collection.find({'service_idnetifier': serviceID}):
            collection.update({'_id': service['_id']}, {'$set': {'connected': True}})
            #collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}}, upsert=True)
        print('db confirm and updated as connected')
#########################################################################################################################
#####################################################  END ##############################################################
