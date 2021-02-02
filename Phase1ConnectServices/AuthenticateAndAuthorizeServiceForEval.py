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
#import java.util.concurrent.TimeUnit;

from selenium.webdriver.common.action_chains import ActionChains
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
#client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client.get_database('services')
collection = db.get_collection('authdetails')
evalcollection = db.get_collection('evalauth')
catcollection = db.get_collection('categories')
all_auth_details = collection.find({})
all_credentials_in_db = {}
currentServiceID = ''
globalformcounter = 1 #important field for form_function
for x in all_auth_details:
    credentials = []
    try:
        if x['username'] != '':
            credentials.append(x['username'])
    except KeyError:
        pass
    try:
        if x['password'] != '':
            credentials.append(x['password'])
            all_credentials_in_db[x['service_idnetifier']] = credentials
    except KeyError:
        pass

########################################################################################################################
############################################## CONSTANTS ###############################################################
possible_usernames = ['channel','lgn', 'usr', 'usrname', 'user', 'email', 'username', 'phone', 'login', 'loginname', 'user[login]', 'hwid',
                 'identifier',
                 'auth-username', 'mobile/email/login', 'username/email',
                 'user_login',
                 'single_access_token']

two_step_form_navigation_button_name = ['next', 'ok', 'continue']

login_button_names = ['lgn', 'login', 'signin', 'authorize', 'next']

authorize_names = ['authorize', 'confirm','allow','approve','agree','okay','yes', 'ok','accept', 'continue']#done

button_class_name = ['button', 'btn', 'submit','next']

list_of_not_values = ['social', 'facebook', 'google']

list_of_not_link_texts = ['terms','privacy','back', 'here', 'signup', 'register', 'password','forgotten', 'legal notice', 'data','policy', 'cookie','policy', 'help',
                 'create', 'new' ,'account',
                 'help', 'not', 'now', 'about', 'learn',
                 'developers',
                 'careers','adchoices','settings','services','site','about', 'inc.','home','page','skip','agreement','contact']

def updateEvalAuth(values):
    evalcollection.find_one_and_update({'service_idnetifier': currentServiceID}, {"$set": values},upsert=True) # upsert true will create a new document if not exist
    print('evalauth db updated')
########################################################################################################################
################################################## FORMS ###############################################################
def updateEvalAuth3Args(s, tag, attr):
    if s == 'username':
        updateEvalAuth({"usernametag": str(tag), "usernametagattr": attr})
    elif s == 'password':
        updateEvalAuth({"passwdtag": str(tag), "passwdtagattr": attr})
    elif s == 'passcode':
        updateEvalAuth({"passwdtag": str(tag), "passwdtagattr": attr})
    elif s == 'button':
        updateEvalAuth({"loginbtntag": str(tag), "loginbtntagattr": attr})

def formfindElementByIDorNAMEandSendKeys(element, data, string):
    success = ""
    foundElement = None
#
    try:
        try:
            #foundElement = browser.find_element_by_id(element['id'])
            foundElement = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.ID, element['id'])))
            foundElement.send_keys(data)
            updateEvalAuth3Args(string, foundElement.tag_name, 'id')
            print(string + ' by id filled')
            success = "True"
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(data)
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
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
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
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
        updateEvalAuth({"logintype": "credentials"})

    return success
def formfindElementByIDorNAMEandSendKeysANDsubmitByReturnKey(element, data, string):
    success = ""
    found,foundElement = formfindElementByIDorNAMEandSendKeys(element, data, string)

    if bool(found):
        foundElement.send_keys(Keys.RETURN)
        print('Form submitted by RETURN key')
        success = "True"
        time.sleep(2)
        updateEvalAuth({"logintype": "credentials"})

    return success
def formfindElementByXPATHandSendKeys(xpathText, data, string):
    success = ""
    foundElement = None
    try:
        foundElement = browser.find_element(By.XPATH, xpathText)
        foundElement.send_keys(data)
        #"//input[@placeholder='"
        patternAttr = "@(.*?)="
        attr = re.search(patternAttr,xpathText)
        updateEvalAuth3Args(string, foundElement.tag_name, attr[0].split('@')[1].split('=')[0])
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
        updateEvalAuth({"logintype": "credentials"})
    return success
def formfindElementByIDorNAMEandSubmit(element, string):
    success = ""
    foundElement = None
    try:
        try:
            foundElement = browser.find_element_by_id(element['id'])
            success = "True"
            updateEvalAuth3Args(string, foundElement.tag_name, 'id')
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                success = "True"
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
            except KeyError:
                print(string + ' by name not exists !')
    except ElementNotVisibleException:
        print('element not visible')
        try:
            try:
                foundElement = browser.find_element_by_name(element['name'])
                success = "True"
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
            except KeyError:
                print(string + ' by name not exists !')
        except ElementNotVisibleException:
            print('element not visible')
    if bool(success):
        foundElement.submit()
        print('Navigate submitted')
        success = "True"
        time.sleep(2)
        updateEvalAuth({"logintype": "credentials"})

    else:
        success = ""
    return success
def formfindElementByIDorNAMEandClick(element, string):# sumbit inputs (next or other naviagation)
    success = ""
    foundElement = None
    try:
        try:
            foundElement = browser.find_element_by_id(element['id'])
            success = "True"
            updateEvalAuth3Args(string, foundElement.tag_name, 'id')
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                success = "True"
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
            except KeyError:
                print(string + ' by name not exists !')
    except ElementNotVisibleException:
        print('element not visible')
        try:
            try:
                foundElement = browser.find_element_by_name(element['name'])
                success = "True"
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
            except KeyError:
                print(string + ' by name not exists !')
        except ElementNotVisibleException:
            print('element not visible')
    if bool(success):
        foundElement.click()
        print('Navigate submitted')
        success = "True"
        time.sleep(2)

    else:
        success = ""
    return success
def func_form_process(forms, list,inputs, buttons, applet_page_content, isusernameset, attempt,restartformcount):
    global globalformcounter
    updateEvalAuth({"formtype": "formForm"})
    if bool(isusernameset):
        updateEvalAuth({"formtype": "divFormTwoStep"})
    login_type = 'Form submitted'
    usernameFilled = isusernameset
    passwordFilled = ""
    m = 0
    print('Form processing .....')
    formcount = 0
    formContinue = False
    for f in forms:
        # ######################### supports restart when moveoutofboundexception at a form ###########################
        formcount = formcount + 1
        globalformcounter = globalformcounter + 1
        if restartformcount != 1:
            if restartformcount == formcount:
                formContinue = True
            if not formContinue:
                continue
        ###############################################################################################################

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
        print(f)
        text_input = f.findChildren("input", attrs={"type": "text"}, recursive=True)
        email_input = f.findChildren("input", attrs={"type": "email"}, recursive=True)
        password_input = f.findChildren("input", attrs={"type": "password"}, recursive=True)
        hidden_input = f.findChildren("input", attrs={"type": "hidden"}, recursive=True)
        submit_input = f.findChildren("input", attrs={"type": "submit"}, recursive=True)
        submit_input2 = f.findChildren("input", attrs={"type": "Submit"}, recursive=True)
        remain_input = f.findChildren("input", recursive=True)
        time.sleep(5)
        print(text_input)
        print(email_input)
        print(password_input)
        # print(hidden_input)
        print(submit_input)
        # print(remain_input)
        # ########################### remove possible hidden elements from the obtained lists ##########################
        # specially reqire for the password feild: therefore we do it for the password inputs ##########################
        for passinput in password_input.copy():
            hiddenitem = False
            for passattr, value in passinput.attrs.items():
                if 'hidden' in passattr:
                    hiddenitem = True
                if 'hidden' in value:
                    hiddenitem = True
            if hiddenitem:
                password_input.remove(passinput)
        print('UPDATED' + str(password_input))
        ################################################################################################################
        # ########################## If IFTTT connected by one button click ############################################
        if len(text_input) == 0 and len(email_input) == 0 and len(password_input) == 0:# and len(text_input) == 0:
            for sb in submit_input:
                if sb['name'] == 'commit':
                    print('simply connect')
                    browser.find_element_by_name(sb['name']).submit()
                    print('Form submitted')
                    time.sleep(10)
                    updateEvalAuth({"logintype": "simple_connect", "loginbtntag": "input", "loginbtntagattr": 'name'})
                    login_type = 'simply connect'
                    return login_type
        # ########################## call DIV FORM ANALYSIS#############################################################
        if not text_input and not email_input and not password_input:
            return func_div_input_process(inputs, buttons, applet_page_content, list, False)
        # ##################################### If type of input is email ##############################################
        if not bool(usernameFilled):
            for ei in email_input:
                if len(data_list) == 0:
                    return 'no credentials'
                ##########################################
                print('Find username 0')
                usernameFilled = formfindElementByIDorNAMEandSendKeys(ei, list[0], 'username')
                if not bool(usernameFilled):
                    print('email name not exists !')
                    usernameFilled = formfindElementByXPATHandSendKeys("//input[@type='email']", list[0], 'username')
        # ##########################  If type of input is username related KEYWORD #####################################
        if not bool(usernameFilled):
            try:
                print('Find username 1')
                for ri in remain_input:
                    if len(data_list) == 0:
                        return 'no credentials'
                    ##########################################
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
                                        if len(data_list) == 0:
                                            return 'no credentials'
                                        ##########################################
                                        try:
                                            type_value = ri['name'].lower().replace(' ', '')
                                            if any(ext in type_value for ext in possible_usernames):
                                                print('different type found with a keyword')
                                                try:
                                                    name = ri['name'].lower().replace(' ', '')
                                                    if any(ext in name for ext in possible_usernames):
                                                        usernameFilled = formfindElementByIDorNAMEandSendKeys(ri,
                                                                                                              list[0],
                                                                                                              'username')
                                                except KeyError:
                                                    print('name not exists !')
                                                    id = ri['id'].lower().replace(' ', '')
                                                    if any(ext in id for ext in possible_usernames):
                                                        usernameFilled = formfindElementByIDorNAMEandSendKeys(ri,
                                                                                                              list[0],
                                                                                                              'username')
                                        except KeyError:
                                            print('name not exist !')
                                        #############################################
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
            if len(data_list) == 0:
                return 'no credentials'
            ##########################################
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
                    if attempt == 2:
                        passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmitByReturnKey(pi, list[1], 'password')
                    else:
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
                                    if attempt == 2:
                                        passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmitByReturnKey(pi,list[1],'password')
                                    else:
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
                                    if attempt == 2:
                                        passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmitByReturnKey(pi, list[ 1],'password')
                                    else:
                                        passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(p, list[1], 'passcode')
                                    if bool(passwordFilled):
                                        return login_type
                        except KeyError:
                            print('no passcode by id')
            except ElementNotVisibleException:
                print('ElementNotVisible exception ...')
        # ################################### No PASSWORD means TWO STEP FORM #########################################
        ###############################################################################################################
        if bool(usernameFilled) and not bool(passwordFilled):
            print('Arrived at the navigation point ==============>')
            navigate = ""
            #################################### navigate by input type ATTEMPT TYPE 1 #################################
            for sbin in submit_input:
                navigate = formfindElementByIDorNAMEandClick(sbin, 'navigate')
            if not bool(navigate):
                for sbin in submit_input2:
                    navigate = formfindElementByIDorNAMEandClick(sbin, 'navigate')
            if not bool(navigate):
                for sbin in buttons:
                    navigate = formfindElementByIDorNAMEandClick(sbin, 'navigate')
            ############################################################################################################

            ######## navigate by input type ATTEMPT TYPE 2##############################################################
            if not bool(navigate):
                navigate = allElementDiscoveryAndClickIfExist(submit_input, two_step_form_navigation_button_name)
            if not bool(navigate):
                navigate = allElementDiscoveryAndClickIfExist(submit_input2, two_step_form_navigation_button_name)
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
                inputs = set(inputs)
                buttons = set(buttons)
                return func_form_process(forms, data_list, inputs, buttons, applet_page_content, "True", attempt,restartformcount)
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
            updateEvalAuth3Args(string, foundElement.tag_name, 'id')
            print(string + ' by id filled')
            success = True
        except KeyError:
            print(string + ' by id not exists !')
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(Keys.CONTROL + "a")
                foundElement.send_keys(Keys.DELETE)
                foundElement.send_keys(data)
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
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
                updateEvalAuth3Args(string, foundElement.tag_name, 'name')
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
        patternAttr = "@(.*?)="
        attr = re.search(patternAttr, xpathText)
        updateEvalAuth3Args(string, foundElement.tag_name, attr[0].split('@')[1].split('=')[0])
        print(string +' by xpath filled')
        success = True
    except KeyError:
        print(string +' filed by xpath not exists !')
    return (success,foundElement)
def func_div_input_process(inputs, buttons, page,list,isusernameset ):
    if len(data_list) == 0:
        return 'no credentials'
    ##########################################
    updateEvalAuth({"formtype": "divForm"})
    if isusernameset:
        updateEvalAuth({"formtype": "divFormTwoStep"})
    print('Div input processing ....')
    password_done = False
    username_done = isusernameset
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
                            # if password_done: # may require for some service check if fails
                            #     return login_type
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
                                # if password_done: # may require or some service check if fails
                                #     return login_type
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
                except KeyError:
                    print('no key type password')
                        # ############################# If type is password find by placeholder#########################
                try:
                    if not password_done:
                        try:
                            if i['placeholder']:
                                placeholder = i['placeholder'].lower().replace(' ', '')
                                if 'password' in placeholder:
                                    xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
                                    password_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[1], 'password')
                                    # if password_done: # may require or some service check if fails
                                    #     return login_type
                        except KeyError:
                            print('placeholder key not exists !')
                except KeyError:
                    pass

                try:
                    # ############################# If type is password find by xpath###############################
                    if not password_done:
                        xpathtext = "//input[@type='password']"
                        password_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[1],
                                                                                           'password')
                        # if password_done: # may require or some service check if fails
                        #     return login_type
                except KeyError:
                    pass

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

     # ################################### No PASSWORD means TWO STEP FORM #########################################
     ###############################################################################################################

        if username_done and not password_done:
            navigate = ""
            ######## Press Next or Navaigation buttion #################################################################
            if not bool(navigate):
                navigate = allElementDiscoveryAndClickIfExist(inputs, two_step_form_navigation_button_name)
            if not bool(navigate):
                navigate = allElementDiscoveryByElementTextAndClickIfExist(buttons, "button",
                                                                           two_step_form_navigation_button_name)
            ############### Find password in form inputs ###############################################################
            if bool(navigate):
                time.sleep(20)
                applet_page_response = browser.page_source
                applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
                forms = applet_page_content.findAll('form', recursive=True)
                inputs = applet_page_content.findAll('input', recursive=True)
                buttons = applet_page_content.findAll('button', recursive=True)
                inputs = set(inputs)
                buttons = set(buttons)
                return func_div_input_process(inputs, buttons, applet_page_content, data_list,True)
        # ######################################### END ###############################################################

        # ######################################### END ###############################################################

    updateEvalAuth({"error": "noInputFields", "attempted": True})
    return 'NOT success login by div form'
########################################################################################################################
################################################ GOOGLE FORMS ##########################################################
def func_process_google_login(div_input, button, list):
    list = ['happybee9494@gmail.com', 'happyBEE@94qwer']
    ##########################################
    updateEvalAuth({"formtype": "googleForm"})
    email_filled = False
    password_filled = False
    email_submitted = False
    password_submitted = False
    login_type = None
    has_email_field = False

    for div in div_input:
        try:
            if div['type'] == 'email':
                has_email_field = True
        except KeyError:
            pass

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
            div_input = set(div_input)
        except WebDriverException:
            print('WebDriverException at ')
    # ###################################################################################################################

    # ###################################################################################################################
    # ###################################################################################################################
    # Process rest of the input fields in order

    for i in div_input:
        # ############################ First Username ###################################################################
        try:
            if i['type'] == 'email':
                try:
                    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, i['id']))).send_keys(
                        list[0])
                    usernametagattr = 'id'
                    print('email find by id filled')
                    email_filled = True
                except KeyError:
                    print('email id not exists !')
                    try:
                        WebDriverWait(browser, 10).until(
                            EC.visibility_of_element_located((By.NAME, i['name']))).send_keys(list[0])
                        usernametagattr = 'name'
                        print('email find by name filled')
                        email_filled = True
                    except KeyError:
                        print('email name not exists !')
        except KeyError:
            pass


        if email_filled and not email_submitted:
            try:
                print(i)
                #WebDriverWait(browser, 50).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='" + 'identifierNext' + "']"))).send_keys(Keys.RETURN)
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@jsname='" + 'LgbsSe' + "']"))).send_keys(Keys.RETURN)
                print('email submitted')
                email_submitted = True
            except WebDriverException:
                print('WebDriverException at email submitted')
                break


        # ############################ Second Password ##################################################################
        if email_submitted:
            try:
                WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='" + 'password' + "']"))).send_keys(list[1])
                passwdtagattr = 'name'
                print('password filled')
                password_filled = True
            except WebDriverException:
                print('WebDriverException at password filled')

        if password_filled and not password_submitted:
            try:
                # x = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='" + 'passwordNext' + "']")))
                # x.send_keys(Keys.RETURN)
                time.sleep(7)
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@jsname='" + 'LgbsSe' + "']"))).send_keys(
                    Keys.RETURN)
                print('password submitted')
                loginbtntagattr = 'jsname'
                password_submitted = True
                login_type = 'form_submitted_count'
                if email_submitted and password_submitted:
                    updateEvalAuth(
                        {"logintype": "credentials", "usernametag": "input", "usernametagattr": usernametagattr,
                         "passwdtag": "input","passwdtagattr": passwdtagattr, "loginbtntag": "button", "loginbtntagattr": loginbtntagattr})
                    return  login_type
            except WebDriverException:
                print('WebDriverException at Form submitted')
                break


    return login_type
########################################################################################################################
############################################### AUTHENTICATION #########################################################
def authentication(browser,data_list, service,attempt):
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

    forms = set(forms)
    inputs = set(inputs)
    buttons = set(buttons)
    google_text_divs = set(google_text_divs)
    a_links = set(a_links)
    google_text = False
    #////////////// find button_click to form/sso
    # if not forms:
    input_size = len(inputs)
    c = 0
    for input in inputs:
        try:
            if input['type'] == 'hidden':
                c += 1
        except KeyError:
            pass

    related_links = []
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
                #related_links = []
                for link in a_links:
                    try:
                        print(link['href'])
                        if any(ext in link['href'] for ext in ['login', 'auth']):
                            if not any(ext in link['href'] for ext in ['language']):
                                related_links.append(link)
                    except KeyError:
                        pass

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
    # if 'To continue' in applet_page_response or 'Continue to'in applet_page_response:
    #     google_text = True
    #     print('Google Sign In')
    try:
        googlediv = browser.find_element_by_class_name('kHn9Lb')
        if googlediv.text == 'Sign in with Google':
            google_text = True
            #list = ['happybee9494@gmail.com', 'happyBEE@94qwer']
            collection.update({'service_idnetifier': service},
                              {'$set': {'username': 'happybee9494@gmail.com', 'password': 'happyBEE@94qwer'}})
    except NoSuchElementException:
        pass



    # ##################################################################################################################
    if not google_text:
        if forms and inputs:
            try:
                try:
                    try:
                        try:
                            try:
                                return func_form_process(forms, data_list,inputs, buttons, applet_page_content,"", attempt,globalformcounter)
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

    # could be useful if div processing not helpfull when form processing not successful
    # to be used with the global globalformcounter variable
    # if login_type =='permission_denied_count':
    #     return func_form_process(forms, data_list, inputs, buttons, applet_page_content, "", attempt,
    #                                      globalformcounter)

    # ##################################################################################################################
    if not forms:
        if inputs:
            try:
                try:
                    try:
                        try:
                            try:
                                return func_div_input_process(inputs, buttons, applet_page_content, data_list, False)
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
            updateEvalAuth({"formtype": "noForm","logintype": "auto"})
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
                                    if len(related_links) > 0:
                                        browser.find_element(By.XPATH,
                                                             "//a[@href='" + related_links[0]['href'] + "']").click()
                                        time.sleep(20)
                                        form_page_response = browser.page_source
                                        form_page_content = BeautifulSoup(form_page_response, "html.parser")
                                        forms = form_page_content.findAll('form', recursive=True)
                                        return func_form_process(forms, data_list, inputs, buttons, applet_page_content,
                                                                 "",attempt, globalformcounter)

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

    updateEvalAuth({"formtype": "noForm", "logintype": "failed"})
    return login_type, browser
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
                            foundElement = WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.ID, element['id'])))
                            foundElement.send_keys(Keys.RETURN)
                            updateEvalAuth({"authbtntag": foundElement.tag_name,"authbtntagattr": 'id', 'linked':True})
                            return 'success'

                        if attribute == 'class':
                            foundElement = WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.CLASS_NAME, element['class'])))
                            foundElement.send_keys(Keys.RETURN)
                            updateEvalAuth({"authbtntag": foundElement.tag_name, "authbtntagattr": 'class', 'linked':True})
                            return 'success'
                        if attribute == 'name':
                            foundElement = WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.NAME, element['name'])))
                            foundElement.send_keys(Keys.RETURN)
                            updateEvalAuth({"authbtntag": foundElement.tag_name, "authbtntagattr": 'name', 'linked':True})
                            return 'success'
                        if attribute == 'value':
                            foundElement = WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.NAME, element['value'])))
                            foundElement.send_keys(Keys.RETURN)
                            updateEvalAuth({"authbtntag": foundElement.tag_name, "authbtntagattr": 'value', 'linked':True})
                            return 'success'

                    except TimeoutException:
                        return 'timeout'
                    except ElementNotInteractableException:
                        return 'element not interactable'
                except KeyError:
                    return 'no key haa'
        else:
            return 'attr not str'

    except KeyError:
        print('key error hehe')
        return 'no key'
def allElementDiscoveryAndClickIfExist(elements,func_possible_name_list):
    for element in elements:
        if findElementAndClickIfExist('id', element,func_possible_name_list) != 'success':
            if findElementAndClickIfExist('class', element,func_possible_name_list) != 'success':
                if findElementAndClickIfExist('name', element,func_possible_name_list) != 'success':
                    if findElementAndClickIfExist('value', element,func_possible_name_list) != 'success':
                        print('no id class or name in input check this one')
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
            if any(ext in element.text.lower().replace(' ', '') for ext in func_possible_name_list):
                print('############### detected ###################' + element.text)
                successfull = False
                #################################################################
                try:
                    xpathtext = "//" + string + "[.='" + element.text + "']"
                    WebDriverWait(browser, 40).until(EC.element_to_be_clickable((By.XPATH, xpathtext))).send_keys(
                        Keys.RETURN)
                    updateEvalAuth({"authbtntag": string, "authbtntagattr": 'text', 'linked': True})
                    successfull = True
                    return 'authorized'
                except TimeoutException:
                    print('no button text: time out exception')
                except ElementNotInteractableException:
                    print('element not reachable')
                    return ""

                ####################################################################
                if not successfull:
                    for ea, ev in element.attrs.items():
                        if type(ev) is list:
                            x = " ".join(ev)
                            ev = x.strip()
                        if ea == 'class':
                            try:
                                browser.find_element_by_class_name(ev).click()
                                time.sleep(10)
                                return 'authorized'
                            except Exception:
                                successfull = False

                        if ea == 'id':
                            try:
                                fe = browser.find_element_by_id(ev)
                                fe.send_keys(Keys.RETURN)
                                time.sleep(10)
                                return 'authorized'
                            except Exception:
                                successfull = False
                        if ea == 'name':
                            try:
                                ffe = browser.find_element_by_name(ev)
                                fe.send_keys(Keys.RETURN)
                                time.sleep(10)
                                return 'authorized'
                            except Exception:
                                successfull = False
                ##################################################################
        if findElementAndClickIfExist('id', element,func_possible_name_list) != 'success':
            if findElementAndClickIfExist('class', element,func_possible_name_list) != 'success':
                if findElementAndClickIfExist('name', element,func_possible_name_list) != 'success':
                    if findElementAndClickIfExist('value', element, func_possible_name_list) != 'success':
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
def authorize():
    print('start authorizing...')
    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    inputs = applet_page_content.findAll('input', recursive=True)
    buttons = applet_page_content.findAll('button', recursive=True)
    divs = applet_page_content.findAll('div', recursive=True)
    a_links = applet_page_content.findAll('a', recursive=True)
    hidden_input = applet_page_content.findAll("input", attrs={"type": "hidden"}, recursive=True)
    inputs = set(inputs)
    divs =  set(divs)
    a_links = set(a_links)
    buttons = set(buttons)
    print(inputs)
    print(buttons)
    # print(divs)
    print(a_links)
    authorized = ""
    ############################################## remove hiddrns #######################################################
    print(len(inputs))
    for inp in inputs.copy():
        hiddenitem = False
        for passattr, value in inp.attrs.items():
            if 'hidden' in passattr:
                hiddenitem = True
            if 'hidden' in value:
                hiddenitem = True
        if hiddenitem:
            inputs.remove(inp)
    print('UPDATED inputs' + str(inputs))
    ####################################################################################################################
    print('###############first pass here####################')
    # check if any element has name, id, text, or class as in authorize_names then click on it to authorize IFTTT

    if not bool(authorized) and inputs:
        authorized = allElementDiscoveryAndClickIfExist(inputs,authorize_names)
    if not bool(authorized) and buttons:
        print('hereeeeeeeeeeeeeeeeeeeeeeeeee')
        authorized = allElementDiscoveryByElementTextAndClickIfExist(buttons,"button",authorize_names)
    if not bool(authorized) and a_links:
        return allElementDiscoveryByElementTextAndClickIfExist(a_links,"a",authorize_names)
    if not bool(authorized) and divs:
        authorized = allElementDiscoveryAndClickIfExist(divs,authorize_names)
def assesLoginResultAndAuthorize(serviceID,login_type):
    e1 = timeit.default_timer()
    if login_type == 'sign_with_google_count':
        # WebDriverWait(browser, 100).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='" + 'submit_approve_access' + "']"))).send_keys(Keys.RETURN)
        time.sleep(7)  # wait since the same button id is used here
        try:
            WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@jsname='" + 'LgbsSe' + "']"))).send_keys(Keys.RETURN)
            updateEvalAuth(
                {"authbtntag": 'button', "authbtntagattr": 'jsname', 'linked': True, "authtype": "googleAuth"})
            # Warning: if continue to sing in with google then may get TimeOutExcption
            print('Clicked allowed')
            e1 = timeit.default_timer()
            time.sleep(5)  # Wait for the allow to be clicked and loading the new page
        except TimeoutException:
            print('time out exception')
            authorize()

    if login_type == 'simply connect':
        updateEvalAuth({"authtype": "simple_connect"})
        e1 = timeit.default_timer()
    if login_type == 'auto_connect_count':
        updateEvalAuth({"logintype": 'auto'})
        e1 = timeit.default_timer()
    if (login_type != 'simply connect') and (login_type != 'permission_denied_count') and (
            login_type != 'NOT success login by form') and (login_type != 'NOT success login by div form') and (
            login_type != 'sign_with_google_count'):
        time.sleep(7)
        authorize()
        e1 = timeit.default_timer()
        time.sleep(5)
        if 'connected' in browser.page_source:
            if login_type == 'auto_connect_count':
                updateEvalAuth({"authtype": "auto"})
            else:
                updateEvalAuth({"authtype": "loginandauth"})
            # collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}},upsert=True)
            print('db updated as connected')

    ############################################ confirm ###########################################################
    try:
        os.mkdir('/home/kulani/results')
    except OSError:
        print("")
    browser.save_screenshot('/home/kulani/results/' + serviceID + '.png')
    time.sleep(1)

    return e1

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
    list_div = set(list_div)
    a_list = set(a_list)
    for aa in a_list:
        href_list.append(aa['href'])
        ## temporary ######################### start
        # divimg  = aa.findChildren("div", {'class':'channel_image'},recursive=True)
        # for imgg in divimg:
        #     imaggg = imgg.findChildren("img", recursive=True)
        #     serviceidd = aa['href'].split('/')[2]
        #     servicename = imaggg[0]['alt']
        #     print(serviceidd)
        #     print(servicename)
        #     collection.find_one_and_update({'service_idnetifier': serviceidd}, {"$set": {"service_name": servicename}},  upsert=True)
        ## temporary ######################### end
    return href_list
########################################################################################################################
############################################# LOGIN TO IFTTT # #########################################################
options = Options()
options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
serv = Service(r'/root/Tools/Firefox/geckodriver')
browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
browser.set_window_size(1000, 1000)
browser.get('https://ifttt.com/login?wp_=1')

username = browser.find_element_by_id("user_username")
password = browser.find_element_by_id("user_password")

# username.send_keys("wijitha.mahadewa@gmail.com")
# password.send_keys("wdwmahadewa")
# username.send_keys("happybee9494@gmail.com")
# password.send_keys("happyBEE@94")
username.send_keys("happybee0999@gmail.com")
password.send_keys("happyBEE@99")

browser.find_element_by_name("commit").click()
href_list = getActivationList()
# TO ADD NEWLY INTRODUCED SERVICES TO THE DATABASE #####################################################################
# allservicenames = []
# for x in href_list:
#     substring = re.search('/channels/(.*?)/',x)
#     if substring is not None:
#         allservicenames.append(substring[0].split('/')[2])
# print(len(allservicenames))
# for se in allservicenames:
#     if se not in all_credentials_in_db.keys():
#         collection.insert_one({'service_idnetifier': se,'connected': False})
#######################################################################################################################
## GET THE CATEGORY OF THE SERVICE PROVIDED BY THE IFTTT ##############################################################
# browser.get('https://ifttt.com/services#connected1')
# applet_page_response = browser.page_source
# applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
# cate_div = applet_page_content.find('div', {'class': 'all-categories'})
# section_list = cate_div.findChildren("section", recursive=True)
#
# for section in section_list:
#     h3 = section.findChildren("h3", recursive=False)
#     category = h3[0].text.replace(' ', '_').lower()
#     service_list = []
#     a_list = section.findChildren("a", recursive=True)
#     for a in a_list:
#         service_list.append(a['href'].split('/')[1])
#     print(category)
#     #catcollection.find_one_and_update({'category': category}, {"$set": {"services": service_list}}, upsert=True)
#     print(service_list)
#     catcollection.insert_one({'category': category,'services': service_list})
#######################################################################################################################
##### ADD CATEGORITY TO THE EVAL TABLE ################################################################################
# for catd in catcollection.find({}):
#     catname = catd['category']
#     servicelist = catd['services']
#     print(catname)
#     print(len(servicelist))
#     islinkedServiceList = []
#     for s in evalcollection.find({}):
#         evalse = s['service_idnetifier']
#         print(evalse)
#         if evalse in servicelist:
#             try:
#                 if s['linked']:
#                     islinkedServiceList.append(evalse)
#             except KeyError:
#                 #evalcollection.update({'service_idnetifier': evalse}, {"$set": {"linked": False}}, upsert=True)
#                 pass
#
#             #evalcollection.update({'service_idnetifier': evalse}, {"$set": {"category": catname}},upsert=True)
#     catcollection.update({'category': catname}, {"$set": {"linkedsize": len(islinkedServiceList), 'linked_service':islinkedServiceList}}, upsert=True)
    #catcollection.update({'category': catname}, {"$set": {"size": len(servicelist)}},upsert=True)
######################################################################################################################

########################################################################################################################
################################################ ANALYZING'''' #########################################################
#for k, v in all_credentials_in_db.items():
check2 = False
#for recored in evalcollection.find({'removed_service':False, 'linked':False, 'error':'no_credentials'}):
for recored in collection.find({'service_idnetifier':'flickr'}):
    # check = True
    # if check:
    #     continue
    try:
        k = recored['service_idnetifier']
        # r = recored['register']
        # if r != 'can' and r!= 'maycan':
        #     continue
    except KeyError:
        continue
    if k in ['cortana', 'yardian', 'notifymyecho', 'soma', 'atmoph', 'pebblebee', 'automateshades', 'tomtom_satnav', 'daskeyboardq', 'netro']:
        continue
    # if 'medium' in k:
    #     collection.update({'service_idnetifier': k}, {'$set': {'username': 'happybee0999@gmail.com','password': 'happyBEE@99qwer'}})
    #     #collection.update({'service_idnetifier': k}, {'$set': {'username': 'kulanitharaka@gmail.com', 'password': '3me3@UTOWn'}})
    # if k in ['deezer', 'inoreader', 'jotform', 'pinterest']:
    #     continue
    # if k == 'tumblr' or k== 'weebly' or k=='wordpress' or k=='inoreader'  or k=='pinboard'or k=='buffer'or k=='airpatrol'or k=='chatwork':
    #     continue
    serviceID = k
    activation_line = '/channels/'+ serviceID+'/activate?is_web_view=1'
    print(activation_line)
    currentServiceID = serviceID
    ########## FILTER 1 ########################
    # try:
    #     result = evalcollection.find({'service_idnetifier': k})
    #     attempted = False
    #     for r in result:
    #         if r['attempted']:#attempted
    #             attempted = True
    #             continue
    #     if  not attempted:
    #         print('not attempted')
    #         continue
    # except KeyError:
    #     print('no attempted key')
    ########## FILTER 2########################
    # try:
    #     result = evalcollection.find({'service_idnetifier': k})
    #     logintypenocredentials = False
    #     for r in result:
    #         print(r['error'])
    #         if r['error'] == 'no_credentials':#attempted 'error': 'no_credentials'
    #             logintypenocredentials = True
    #     if  logintypenocredentials and recored['register'] != 'can':
    #         continue
    # except KeyError:
    #     print('no error identified')
    #############################################
    #print(href_list)
    if activation_line in href_list:#/channels/google_docs/activate?is_web_view=1
        s1 = timeit.default_timer()
        try:
            data_list = all_credentials_in_db[k]
            # data_list = ['happybee9494@gmail.com','happyBEE@94qwer' ]
            print(data_list)
        except KeyError:
            data_list = []
            pass

        try:
            browser.get('https://ifttt.com/' + activation_line)
        except WebDriverException:
            updateEvalAuth({"error": 'error_loading'})
            continue
        time.sleep(20)  # mandatory wait for the page load
        ################################################################################################################
        ######################################### AUTHENTICATION #######################################################
        try:
            login_type, browser = authentication(browser, data_list,k,1)
        except UnexpectedAlertPresentException:
            updateEvalAuth({'attempted': True, 'linked': False, 'error': 'UnexpectedAlertPresentException'})
            continue


        if login_type is not None:
            login_type = login_type.strip(' ')
            print('login type = '+login_type)
        #print(browser.page_source)

        ################################################################################################################
        ######################################### AUTHORIZATION# #######################################################
        if login_type == 'no credentials':
            updateEvalAuth({'attempted': True, 'linked':False, 'error': 'no_credentials'})
            try:
                os.mkdir('/home/kulani/results2')
            except OSError:
                print("")
            browser.save_screenshot('/home/kulani/results2/' + serviceID + '.png')
            time.sleep(1)
            continue
        time.sleep(10)
        e1 = assesLoginResultAndAuthorize(serviceID,login_type)


        updated_href_list = getActivationList()
        new_activation_line = '/channels/' + k + '/reactivate?is_web_view=1'
        if new_activation_line in updated_href_list:
            updateEvalAuth({"linked": True})
            #collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}},upsert=True)
            print('db confirm and updated as connected')
            updateEvalAuth({"time": str(e1 - s1)})
        else:
            updateEvalAuth({"linked": False})
            updateEvalAuth({"attempted": True})
            #collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": False}},upsert=True)
            ################################################################################################################
            ######################################### ATTEMPT 2: Couldn't login############################# ###############
            erorresult = evalcollection.find({"service_idnetifier": k, "logintype": "credentials", "linked": False})
            for er in erorresult:
                try:
                    browser.get('https://ifttt.com/' + activation_line)
                except WebDriverException:
                    updateEvalAuth({"error": 'error_loading'})
                    continue
                time.sleep(20)  # mandatory wait for the page load
                login_type = authentication(browser, data_list, k, 2)
                e1 = assesLoginResultAndAuthorize(serviceID, login_type)
                updated_href_list = getActivationList()
                new_activation_line = '/channels/' + k + '/reactivate?is_web_view=1'
                if new_activation_line in updated_href_list:
                    updateEvalAuth({"linked": True})
                    # collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}},upsert=True)
                    print('db confirm and updated as connected')
                    updateEvalAuth({"time": str(e1 - s1)})
                else:
                    updateEvalAuth({"linked": False})
                    updateEvalAuth({"attempted": True})
            ################################################################################################################
            print('db confirm and rollback changes')

    else:
        print('already connected')
        for service in collection.find({'service_idnetifier': serviceID}):
            print('already connected')
            updateEvalAuth({"linked": True})
            updateEvalAuth({"attempted": True})
            #collection.update({'_id': service['_id']}, {'$set': {'connected': True}})
            #collection.find_one_and_update({'service_idnetifier': serviceID}, {"$set": {"connected": True}}, upsert=True)
        print('db confirm and updated as connected')

browser.quit()
#########################################################################################################################
#####################################################  END ##############################################################