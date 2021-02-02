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
LOGIN_URL = ''
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
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
def initLoginurl(url):
    LOGIN_URL = url


########################################################################################################################
################################################## FORMS ###############################################################
def findElementAndClickIfExist(browser,attribute, element,func_possible_name_list):
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
def allElementDiscoveryAndClickIfExist(browser,elements,func_possible_name_list):
    for element in elements:
        if findElementAndClickIfExist(browser,'id', element,func_possible_name_list) != 'success':
            if findElementAndClickIfExist(browser,'class', element,func_possible_name_list) != 'success':
                if findElementAndClickIfExist(browser,'name', element,func_possible_name_list) != 'success':
                    if findElementAndClickIfExist(browser,'value', element,func_possible_name_list) != 'success':
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
def allElementDiscoveryByElementTextAndClickIfExist(browser,elements,string,func_possible_name_list):
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
        if findElementAndClickIfExist(browser,'id', element,func_possible_name_list) != 'success':
            if findElementAndClickIfExist(browser,'class', element,func_possible_name_list) != 'success':
                if findElementAndClickIfExist(browser,'name', element,func_possible_name_list) != 'success':
                    print('no id class or name in button')
                else:
                    return 'authorized'
            else:
                return 'authorized'
        else:
            return 'authorized'
    return ""
#######################################################################################################################
# to satisfy case of deezer and office 365
def fillPasswordOnly(browser,datalist,text_input,email_input,loginurl):
    print('fillPasswordOnly')

    usernameFilled = ''
    if not bool(usernameFilled):
        for ei in email_input:
            print('Find username 00')
            usernameFilled = formfindElementByIDorNAMEandSendKeys(browser, ei, datalist[0], 'username')
            return usernameFilled
            if not bool(usernameFilled):
                print('email name not exists !')
                usernameFilled = formfindElementByXPATHandSendKeys(browser, "//input[@type='email']", datalist[0],
                                                                   'username')
                return usernameFilled

    for ti in text_input:
        print('Find username 4')
        try:
            name = ti['name'].lower().replace(' ', '')
            # #################### (1) check for username related KEYWORDS by name##################################
            if not bool(usernameFilled):
                if any(ext in name for ext in possible_usernames):
                    usernameFilled = formfindElementByIDorNAMEandSendKeys(browser, ti, datalist[0], 'username')
                    return usernameFilled
            # #################### (1) check for password related KEYWORDS #########################################
        except KeyError:
            print('name not exists !!')
        # #################### (1) check for username related KEYWORDS by placeholder ##########################
        if not bool(usernameFilled):
            try:
                placeholder = ti['placeholder'].lower().replace(' ', '')
                if any(ext in placeholder for ext in possible_usernames):
                    xpathtext = "//input[@placeholder='" + ti['placeholder'] + "']"
                    usernameFilled = formfindElementByXPATHandSendKeys(browser, xpathtext, datalist[0], 'username')
                    return usernameFilled
            except KeyError:
                print('place holder not exist in text input')

        # #################### (1) check for username related KEYWORDS by id ##########################
        if not bool(usernameFilled):
            try:
                id = ti['id'].lower().replace(' ', '')
                if any(ext in id for ext in possible_usernames):
                    usernameFilled = formfindElementByIDorNAMEandSendKeys(browser, ti, datalist[0], 'username')
                    return usernameFilled
            except KeyError:
                print('key error')
def formfindElementByIDorNAMEandSendKeys(browser,element, data, string):
    success = ""
    foundElement = None
    try:
        try:
            foundElement = browser.find_element_by_id(element['id'])

            if foundElement.get_attribute("value").strip() == '':
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
                ## by class name and type
                try:
                    try:
                        type = element['type']
                        real_class_name = ''
                        if len(element['class']) > 1:
                            for cn in element['class']:
                                real_class_name = real_class_name + '.' + cn
                        else:
                            real_class_name = element['class'][0]
                        #####
                        print(real_class_name)
                        foundElement = browser.find_element_by_css_selector('input' + real_class_name)
                        if element['type'] == foundElement.get_attribute('type'):
                            time.sleep(1)
                            foundElement.send_keys(data)
                            print(string + 'by class name filled')
                            success = "True"
                        else:
                            real_class_name = ''
                            if len(element['class']) > 1:
                                for cn in element['class']:
                                    real_class_name = real_class_name + cn+ ' '
                            else:
                                real_class_name = element['class'][0]
                            #######
                            print(real_class_name)
                            foundElement = browser.find_element_by_xpath(
                                "//input[@type = '"+element['type']+"'][@class='"+real_class_name.strip()+"']");
                            foundElement.send_keys(data)
                            print(string + 'by xpath filled')
                            success = "True"
                    except KeyError:
                        print(string + ' by class name not exists !')
                except ElementNotVisibleException:
                    print('element not visible')
    except ElementNotVisibleException:
        print('element not visible')
        try:
            try:
                foundElement = browser.find_element_by_name(element['name'])
                foundElement.send_keys(data)
                print(string + 'by class name filled')
                success = "True"
            except KeyError:
                print(string + ' by class name not exists !')
        except ElementNotVisibleException:
            print('element not visible')
    return success,foundElement
def formfindElementByIDorNAMEandSendKeysANDsubmit(browser,element, data, string,loginurl,text_input,email_input,datalist):
    print('formfindElementByIDorNAMEandSendKeysANDsubmit')
    success = ""
    submitSuccess = ""

    found,foundElement = formfindElementByIDorNAMEandSendKeys(browser,element, data, string)
    if bool(found):
        screenshot = browser.save_screenshot('my_screenshot.png')
        foundElement.submit()
        time.sleep(30)
        #time.sleep(50)
        # amazonclouddrive
        if ('signin' not in browser.current_url) and ('login' not in browser.current_url):
            success = "True"
        else:
            print('password not filled')
            if bool(found) :
                print('password filled submit failed')
                # only fille the password, if both resets cannot
                print(text_input)
                print(datalist)
                usernameFilled = fillPasswordOnly(browser,datalist,text_input,email_input,loginurl)
                if bool(usernameFilled):
                    print('here comes')
                    found2, foundElement2 = formfindElementByIDorNAMEandSendKeys(browser, element, data, string)
                    if bool(found2):
                        success = "True"
                        return submitSuccess, success
        print(browser.current_url)
        if success:
            if browser.current_url != loginurl:
                print('submitted !!')
                submitSuccess = "True"
            else:
                print('not submitted')

    return submitSuccess,success
def formfindElementByXPATHandSendKeys(browser,xpathText, data, string):
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
def formfindElementByXPATHandSendKeysANDsubmit(browser,xpathText, data, string,loginurl):
    print('formfindElementByXPATHandSendKeysANDsubmit')
    success = ""
    submitSuccess = ""
    found, foundElement = formfindElementByXPATHandSendKeys(browser,xpathText, data, string)
    if bool(found):
        foundElement.submit()
        success = "True"

        if browser.current_url != loginurl:
            print('submitted !!')
            submitSuccess = "True"
        else:
            print('Not submitted')

    return submitSuccess,success
def submitInputButtonByTypeAndSubmit(browser,i,login_button_names):
    print(i)
    #if i['type'] == 'button' or i['type'] == 'sumbit' or i['type'] == 'Sumbit':
    if i['type'] == 'submit':
        try:
            try:
                if any(ext in i['value'].lower().replace(' ', '') for ext in login_button_names):
                    try:
                        browser.find_element_by_xpath("//input[@id='" + i['id'] + "']").click()
                        # time.sleep(15)
                         # deezer wait long for captrcha
                        print('Form submitted')
                        return "True"

                    except KeyError:
                        print('button id not exists !')
            except KeyError:
                print('value key not exists')
        except KeyError:
            print('button by type not exists !')
def formfindElementByIDorNAMEandSubmit(browser,element, string):
    print('formfindElementByIDorNAMEandSubmit')
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
        time.sleep(25)
        # print(browser.page_source)
    else:
        success = ""
    return success
def func_form_process(browser,forms, list,inputs, buttons, applet_page_content, isusernameset,loginurl):
    login_type = 'Form submitted'
    usernameFilled = isusernameset
    passwordFilled = ""
    submitSuccess = ""
    m = 0
    print('Form processing .....')
    for f in forms:
        print('//////////////////////////////////////////////////')
        m += 1
        print('form: ' + str(m))
        sign_up_form = False
        for attrf in f.attrs:
            if any(ext in f[attrf] for ext in ['sign-up','register','signup','search']):
                print('Not a sign in form !!!!!')
                sign_up_form = True
                break

        if sign_up_form:
            continue
        ###########################################################
        try:
            if f['type'] == 'hidden':
                print('hidden form !')
                continue
        except KeyError:
            print('no type key in form')
        print(f)
        print('//////////////////////////////////////////////////')
        all_input = f.findChildren("input", recursive=True)
        text_input = f.findChildren("input", attrs={"type": "text"}, recursive=True)
        email_input = f.findChildren("input", attrs={"type": "email"}, recursive=True)
        password_input = f.findChildren("input", attrs={"type": "password"}, recursive=True)
        hidden_input = f.findChildren("input", attrs={"type": "hidden"}, recursive=True)
        submit_input = f.findChildren("input", attrs={"type": "submit"}, recursive=True)
        submit_input2 = f.findChildren("input", attrs={"type": "Submit"}, recursive=True)
        buttonsInForm = f.findChildren("button", recursive=True)
        remain_input = f.findChildren("input", recursive=True)
        time.sleep(5)
        print(password_input)
        print(text_input)
        print(email_input)
        # print(password_input)
        # print(hidden_input)
        # print(submit_input)
        # print(remain_input)
        if not text_input and not email_input and not password_input:
            login_type =  func_div_input_process(browser,forms,inputs, buttons, applet_page_content, list)
            return
        ########################################################### added after musixmatch#############################

        sign_in_input = False
        have_forbidden_keyword = False
        for ai in all_input:
            for attrf in ai.attrs:
                print(ai[attrf])
                if any(ext in ai[attrf] for ext in ['remember']):# to avoid remember account in flicker, to avoid break by next condition
                    continue
                if any(ext in ai[attrf] for ext in ['account']):
                    have_forbidden_keyword = True
                    break
                if any(ext in ai[attrf] for ext in possible_usernames) or any(
                        ext in ai[attrf] for ext in ['password']) or any(
                        ext in ai[attrf] for ext in login_button_names) or any(
                        ext in ai[attrf] for ext in button_class_name):
                    print('Sing in related input !!!!!')
                    sign_in_input = True

        print(have_forbidden_keyword)
        if have_forbidden_keyword:
            continue
        if not sign_in_input:
            continue
        ############################################################


        # ########################## If IFTTT connected by one button click ############################################
        if len(text_input) == 0 and len(email_input) == 0 and len(password_input) == 0 and len(text_input) == 0:
            for sb in submit_input:
                if sb['name'] == 'commit':
                    print('simply connect')
                    browser.find_element_by_name(sb['name']).submit()
                    print('Form submitted')
                    time.sleep(10)
                    login_type = 'simply connect'
                    return login_type, browser


        # ##################################### If type of input is email ##############################################
        if not bool(usernameFilled):
            for ei in email_input:
                if not bool(usernameFilled):
                    print(ei)
                    print('Find username 0')
                    usernameFilled, foundElement = formfindElementByIDorNAMEandSendKeys(browser, ei, list[0],
                                                                                        'username')
                    print(usernameFilled)
                    if not bool(usernameFilled):
                        print('email name not exists !')
                        usernameFilled, foundElement = formfindElementByXPATHandSendKeys(browser,
                                                                                         "//input[@type='email']",
                                                                                         list[0], 'username')


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
                                    usernameFilled = formfindElementByIDorNAMEandSendKeys(browser,ri, list[0], 'username')
                            except KeyError:
                                print('name not exists !')
                                id = ri['id'].lower().replace(' ', '')
                                if any(ext in id for ext in possible_usernames):
                                    usernameFilled = formfindElementByIDorNAMEandSendKeys(browser,ri, list[0], 'username')
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
                                                usernameFilled,foundElement = formfindElementByXPATHandSendKeys(browser,xpathtext, list[0], 'username')
                                        except KeyError:
                                            print('placeholder not exists !')
        # ################### If text input type has other attrinbutes with username/password KEYWORDS #################
        text_inputx = text_input
        print(text_input)
        for ti in text_inputx:
            print('Find username 4')
            try:
                name = ti['name'].lower().replace(' ', '')
                # #################### (1) check for username related KEYWORDS by name##################################
                if not bool(usernameFilled):
                    if any(ext in name for ext in possible_usernames):
                        usernameFilled,foundElement = formfindElementByIDorNAMEandSendKeys(browser,ti, list[0], 'username')
                # #################### (1) check for password related KEYWORDS #########################################
                if bool(usernameFilled):
                    if 'password' in name:
                        try:
                            # pswrd = browser.find_element_by_name(ti['name'])
                            # pswrd.send_keys(list[1])
                            # browser.find_element_by_name(ti['name']).submit()
                            submitSuccess,passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(browser, ti, list[1], 'password',loginurl,text_input,email_input,list)
                            print('password by name filled')
                            #print('Form submitted')
                            if bool(submitSuccess):
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
                        usernameFilled,foundElement = formfindElementByXPATHandSendKeys(browser,xpathtext, list[0], 'username')
                except KeyError:
                    print('place holder not exist in text input')

            # #################### (1) check for username related KEYWORDS by id ##########################
            if not bool(usernameFilled):
                try:
                    id = ti['id'].lower().replace(' ', '')
                    if any(ext in id for ext in possible_usernames):
                        usernameFilled,foundElement = formfindElementByIDorNAMEandSendKeys(browser,ti, list[0], 'username')
                except KeyError:
                    print('key error')
        # #################################### FILL  PASSWORDS #########################################################
        if bool(usernameFilled) and not bool(passwordFilled):
            try:
                print('Find Password 2')
                if 'evernote' in loginurl:
                    time.sleep(5) # to press continue
                for pi in password_input:
                    print(pi)
                    submitSuccess,passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(browser,pi, list[1], 'password',loginurl,text_input,email_input,list)
                    print(passwordFilled)
                    if bool(submitSuccess):
                        return login_type
                    if not bool(passwordFilled):
                        xpathtextt = "//input[@type='password']"
                        submitSuccess,passwordFilled = formfindElementByXPATHandSendKeysANDsubmit(browser,xpathtextt, list[1], 'password',loginurl,text_input,email_input,list)
                        if bool(submitSuccess):
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
                                    submitSuccess,passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(browser,p, list[1], 'passcode',loginurl,text_input,email_input,list)
                                    if bool(submitSuccess):
                                        return login_type
                        except KeyError:
                            print('no passcode by name')

                    if not bool(passwordFilled):
                        try:
                            pid = p['id'].lower().replace(' ', '')
                            # #################### (2) check for passcode by id ########################################
                            if not bool(usernameFilled):
                                if 'passcode' in pid:
                                    submitSuccess,passwordFilled = formfindElementByIDorNAMEandSendKeysANDsubmit(browser,p, list[1], 'passcode',loginurl,text_input,email_input,list)
                                    if bool(submitSuccess):
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
                navigate = allElementDiscoveryAndClickIfExist(browser,inputs, two_step_form_navigation_button_name)
            if not bool(navigate):
                navigate = allElementDiscoveryByElementTextAndClickIfExist(browser,buttons, "button", two_step_form_navigation_button_name)
            ############### Find password in form inputs ###############################################################
            if bool(navigate):
                time.sleep(20)
                applet_page_response = browser.page_source
                applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
                forms = applet_page_content.findAll('form', recursive=True)
                inputs = applet_page_content.findAll('input', recursive=True)
                buttons = applet_page_content.findAll('button', recursive=True)
                return func_form_process(browser,forms, list, inputs, buttons, applet_page_content, "True",loginurl)
         # ######################################### END ###############################################################
        if not bool(submitSuccess):
            print('not submitted')
            ################################ Input buttons#### #########################################################
            for sb in submit_input:
                print('submit input')
                submitSuccess = submitInputButtonByTypeAndSubmit(browser, sb, login_button_names)
            if bool(submitSuccess):
                return "form log in"
            else:
                for sb2 in submit_input2:
                    print('submit input2')
                    submitSuccess = submitInputButtonByTypeAndSubmit(browser, sb2, login_button_names)
                if bool(submitSuccess):
                    return "form log in"
             ###########################################################################################################
            if not bool(submitSuccess):
                print(buttonsInForm)
                for bb in buttonsInForm:
                    if bb.text:
                        print(bb.text)
                        if not any(ext in bb.text.lower().replace(' ', '') for ext in list_of_not_values):
                            if any(ext in bb.text.lower().replace(' ', '') for ext in login_button_names):

                                try:
                                    browser.find_element_by_xpath("//button[@id='" + bb['id'] + "']").click()
                                    print('Form submitted x')
                                    time.sleep(80)#deezer time.sleep(80)
                                    return login_type
                                except KeyError:
                                    print('button id not exists !')
                                    try:
                                        #browser.execute_script("document.body.style.transform='scale(0.9)';")
                                        classID=''
                                        if len(bb['class'])>1:
                                            for x in bb['class']:
                                                classID = classID + '.'+x

                                        source_element = browser.find_element_by_css_selector('button'+classID)
                                        actions = ActionChains(browser)
                                        actions.move_to_element(source_element)
                                        time.sleep(1)
                                        actions.click()#.perform()
                                        print('Form submitted by class name')
                                        #time.sleep(25)
                                        print(browser.current_url)
                                        return login_type
                                    except KeyError:
                                        print('button class not exists !')
                                    try:
                                        print('came here name')
                                        browser.find_element_by_xpath(
                                            "//button[@name='" + bb['name'] + "']").click()
                                        print('Form submitted')
                                        #time.sleep(25)
                                        return login_type
                                    except KeyError:
                                        print('button name not exists !')
                                        try:
                                            strg = bb['class']
                                            if any(ext in strg[0].lower() for ext in button_class_name):
                                                try:
                                                    print("//button[contains(text(), '" + bb.text + "')]")
                                                    button_lst = browser.find_elements_by_xpath(
                                                        "//*[contains(text(), '" + bb.text + "') and  not(contains(text(), 'google')) and  not(contains(text(), 'Google')) and  not(contains(text(), 'facebook')) and  not(contains(text(), 'Facebook'))]")
                                                    print(button_lst)

                                                    for bl in button_lst:
                                                        bl.click()
                                                        #time.sleep(25)
                                                        print('Form submitted')
                                                        return login_type
                                                except KeyError:
                                                    print('button by text not exists !')
                                                    browser.find_element_by_class_name(strg[0]).click()
                                                    #time.sleep(25)
                                                    print('Form submitted')
                                                    return login_type
                                        # ##################################################################################
                                        except KeyError:
                                            print('button class not exists !')
                                            try:
                                                print("//button[contains(text(), '" + bb.text + "')]")
                                                button_lst = browser.find_elements_by_xpath(
                                                    "//*[contains(text(), '" + bb.text + "')]")
                                                for bl in button_lst:
                                                    time.sleep(25)
                                                    bl.click()
                                                    print('Form submitted')
                                                    return login_type
                                            except KeyError:
                                                print('button by text not exists !')

    return 'NOT success login by form'
########################################################################################################################
################################################ DIV FORMS #############################################################
def divFormfindElementByIDorNAMEandSendKeys(browser,element, data, string):
    print('divFormfindElementByIDorNAMEandSendKeys')
    print(element)
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
                actions = ActionChains(browser)
                foundElement = browser.find_element_by_name(element['name'])
                actions.move_to_element(foundElement)
                time.sleep(1)
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
def divFormfindElementByXPATHandSendKeys(browser,xpathText, data, string):
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

def divPrpcessomg(browser,inputs, buttons, page,list ):
    login_type = "True"
    button_submitted = False
    for i in inputs:
        print(i)
        try:
            if i['type'] == 'search':
                continue
        except KeyError:
            print('no hidden type')
        ##########################
        print('camer here 0')
        sign_in_input = False
        have_forbidden_keyword = False
        print(i)
        for attrf in i.attrs:
            print(i[attrf])
            if any(ext in i[attrf] for ext in ['account']):
                have_forbidden_keyword = True
                break
            if any(ext in i[attrf] for ext in possible_usernames) or any(ext in i[attrf] for ext in ['password']) or any(ext in i[attrf] for ext in login_button_names) or any(ext in i[attrf] for ext in button_class_name) :
                print('Sing in related input !!!!!')
                sign_in_input = True

        print(have_forbidden_keyword)
        if have_forbidden_keyword:
            continue
        if not sign_in_input:
            continue
        print(i)
        try:
            if i['type'] == 'hidden':
                continue
        except KeyError:
            print('no hidden type')
        ########################################## USERNAME ############################################################
        ################################ If type is text ###############################################################
        try:
            try:
                if i['type'] == 'text' or i['type'] == 'email':
                    # ############################# If type of DIV is text search by name ##############################
                    try:
                        print('here 0')
                        name = i['name'].lower().replace(' ', '')
                        if any(ext in name for ext in possible_usernames):
                            username_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(browser, i, list[0],
                                                                                                  'username')
                        #for attrff in i.attrs:
                            # if any(ext in i[attrff] for ext in possible_usernames):
                            #     print(i)
                            #     username_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(browser,i, list[0],
                            #                                                                           'username')

                    except KeyError:
                        print('no key')
                    # ############################# If type of DIV is text search by placeholder########################

                    if not username_done:
                        try:
                            print('here 1')
                            if i['placeholder']:
                                placeholder = i['placeholder'].lower().replace(' ', '')
                                if any(ext in placeholder for ext in possible_usernames):
                                    xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
                                    username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext,
                                                                                                       list[0],
                                                                                                       'username')
                        except KeyError:
                            print('placeholder key not exists !')
                    # ##################################  SUMBIT password ###############################################
                    if username_done:
                        if 'password' in i['name']:
                            print('password enter')
                            password_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(browser,i, list[1],
                                                                                                  'password')
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
                                    username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext,
                                                                                                       list[0],
                                                                                                       'username')

                        else:
                            if any(ext in i[attr] for ext in possible_usernames) and not username_done:
                                xpathtext = "//input[@" + attr + "= '" + i[attr] + "']"
                                username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[0],
                                                                                                   'username')
        except NoSuchElementException:
            print('no such element')
        ################################ If type is email ##############################################################
        # if not username_done:
        #     try:
        #         try:
        #             if i['type'] == 'email':
        #                 # ############################# If type of DIV is text search by name ##########################
        #                 try:
        #                     name = i['name'].lower().replace(' ', '')
        #                     if any(ext in name for ext in possible_usernames):
        #                         username_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[0],
        #                                                                                               'username')
        #                 except KeyError:
        #                     print('no key')
        #                 # ############################# If type of DIV is text search by placeholder####################
        #                 if not username_done:
        #                     try:
        #                         if i['placeholder']:
        #                             placeholder = i['placeholder'].lower().replace(' ', '')
        #                             if any(ext in placeholder for ext in possible_usernames):
        #                                 xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
        #                                 username_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext,
        #                                                                                                    list[0],
        #                                                                                                    'username')
        #                     except KeyError:
        #                         print('placeholder key not exists !')
        #                 # ##################################  SUMBIT password ##########################################
        #                 if username_done:
        #                     if 'password' in i['name']:
        #                         password_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(i, list[1],
        #                                                                                               'password')
        #                         if password_done:
        #                             return login_type
        #         except KeyError:
        #             print('no key')
        #     except NoSuchElementException:
        #         print('no such element')

        ##############################################PASSWORD #########################################################
        ################################ If type is pasword ############################################################
        if username_done:
            try:
                try:
                    print(i)
                    if i['type'] == 'password':
                        # ############################# If type is password find by id or name #########################
                        password_done, foundElement = divFormfindElementByIDorNAMEandSendKeys(browser,i, list[1], 'password')
                        # ############################# If type is password find by placeholder#########################
                        if not password_done:
                            try:
                                if i['placeholder']:
                                    placeholder = i['placeholder'].lower().replace(' ', '')
                                    if 'password' in placeholder:
                                        xpathtext = "//input[@placeholder='" + i['placeholder'] + "']"
                                        password_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext,
                                                                                                           list[1],
                                                                                                           'password')
                                        if password_done:
                                            return login_type
                            except KeyError:
                                print('placeholder key not exists !')
                        # ############################# If type is password find by xpath###############################
                        if not password_done:
                            xpathtext = "//input[@type='password']"
                            password_done, foundElement = divFormfindElementByXPATHandSendKeys(xpathtext, list[1],
                                                                                               'password')
                            if password_done:
                                return login_type
                    else:
                        continue

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
                    if type(button[attr]) is list:
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
                                time.sleep(25)
                                button_submitted = True
                                return login_type
                            except KeyError:
                                print('button id not exists !')
                                try:
                                    print('came here name')
                                    browser.find_element_by_xpath(
                                        "//button[@name='" + button['name'] + "']").click()
                                    print('Form submitted')
                                    time.sleep(25)
                                    button_submitted = True
                                    return login_type
                                except KeyError:
                                    print('button name not exists !')
                                    try:
                                        strg = button['class']
                                        if any(ext in strg[0].lower() for ext in button_class_name):
                                            try:
                                                print("//button[contains(text(), '" + button.text + "')]")
                                                button_lst = browser.find_elements_by_xpath(
                                                    "//*[contains(text(), '" + button.text + "') and  not(contains(text(), 'google')) and  not(contains(text(), 'Google')) and  not(contains(text(), 'facebook')) and  not(contains(text(), 'Facebook'))]")
                                                print(button_lst)

                                                for bl in button_lst:
                                                    time.sleep(25)
                                                    bl.click()
                                                    print('Form submitted')
                                                    return login_type
                                                button_submitted = True
                                            except KeyError:
                                                print('button by text not exists !')
                                                browser.find_element_by_class_name(strg[0]).click()
                                                time.sleep(25)
                                                print('Form submitted')
                                                button_submitted = True
                                                return login_type
                                    # ##################################################################################
                                    except KeyError:
                                        print('button class not exists !')
                                        try:
                                            print("//button[contains(text(), '" + button.text + "')]")
                                            button_lst = browser.find_elements_by_xpath(
                                                "//*[contains(text(), '" + button.text + "')]")
                                            for bl in button_lst:
                                                time.sleep(25)
                                                bl.click()
                                                print('Form submitted')
                                                button_submitted = True
                                                return login_type
                                        except KeyError:
                                            print('button by text not exists !')
            ####################################If NO BUTTONS exists####################################################
            if not button_submitted:
                divs = page.findAll('div', recursive=True)
                for div in divs:
                    print('came here div')
                    try:
                        class_name = div['class']
                        if class_name:
                            real_class_name = ''
                            if len(class_name) >1:
                                for cn in class_name:
                                    real_class_name = real_class_name+'.'+cn
                            else:
                                real_class_name = class_name[0]


                            for attrff in div.attrs:
                                if any(ext in div[attrff] for ext in button_class_name):
                                    print(div)
                                    time.sleep(5)# required for twitter
                                    source_element = browser.find_element_by_css_selector('div' + real_class_name)
                                    actions = ActionChains(browser)
                                    actions.move_to_element(source_element)
                                    time.sleep(1)
                                    actions.click()  # .perform()
                                    time.sleep(25)
                                    print('Form submitted div')
                                    return login_type
                            class_name = class_name[0].lower().replace(' ', '')
                            if any(ext in class_name for ext in button_class_name):
                                if not any(ext in class_name for ext in list_of_not_values):
                                    print('has button')
                                    browser.find_element_by_class_name(class_name).click()
                                    time.sleep(25)
                                    return login_type
                            #class_name = class_name[0].lower().replace(' ', '')

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
                                    time.sleep(25)
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
                                    time.sleep(25)
                                    print('Form submitted')
                                    return login_type
                    except KeyError:
                        print('no such key')

        # ######################################### END ###############################################################
def func_div_input_process(browser,forms,inputs, buttons, page,list ):
    print('Div input processing ....')
    password_done = False
    username_done = False
    login_type = 'div form submitted'
    print(inputs)
    for f in forms:
        sign_in_form = False
        for attrf in f.attrs:
            if any(ext in f[attrf] for ext in ['login','signin']):
                print('Sing up form !!!!!')
                sign_in_form = True
                break

        if not sign_in_form:
            continue


        ############################################################
        print(f)
        inputs2 = f.findAll('input', recursive=True)
        buttons2 = f.findAll('button', recursive=True)
        result = divPrpcessomg(browser, inputs2, buttons2, f, list)
        if bool(result):
            return login_type

    result2 = divPrpcessomg(browser, inputs, buttons, page, list)
    if bool(result2):
        return login_type

    return 'NOT success login by div form'
########################################################################################################################
################################################ GOOGLE FORMS ##########################################################
def func_process_google_login(browser,div_input, button, list):

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
                    time.sleep(25)
                    return  login_type

        except WebDriverException:
            print('WebDriverException at Form submitted')
    time.sleep(25)
    return login_type
def func_process_google_all_login(browser,div_input, button,inputs,forms, list):
    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    divs = applet_page_content.findAll('div', recursive=True)
    print(applet_page_response)
    email_filled = False
    password_filled = False
    email_submitted = False
    password_submitted = False
    login_type = None
    has_email_field = False
    for input in inputs:
        if input['type'] == 'email':
            has_email_field = True

    for d in divs:
        try:
            if d['id'] == 'identifier-shown':
                print(d)
        except KeyError:
            print('no key')


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
    try:
        if not email_filled:
            #browser.find_element_by_id("Email").send_keys(list[0])
            WebDriverWait(browser, 50).until(EC.visibility_of_element_located((By.ID, 'Email'))).send_keys(list[0])
            print('email find by id filled')
            email_filled = True
    except WebDriverException:
        print('WebDriverException at email filled')
    try:
        if email_filled:
                WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'next'))).send_keys(Keys.RETURN)
                print('next by id ')
                email_submitted = True
    except WebDriverException:
        print('WebDriverException at email submit')
    try:
        if email_submitted:
                WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'Passwd'))).send_keys(
                    list[1])
                print('password find by id filled')
                password_filled = True
    except WebDriverException:
        print('WebDriverException at password filled')
    try:
        if password_filled and not password_submitted:
            WebDriverWait(browser, 10).until(
                        EC.visibility_of_element_located((By.NAME, 'signIn'))).send_keys(Keys.RETURN)
            print('password submitted')
            password_submitted = True
            login_type = 'form_submitted_count'
            if email_submitted and password_submitted:
                time.sleep(25)
                return login_type
    except WebDriverException:
        print('WebDriverException at Form submitted')
    # ###################################################################################################################
    time.sleep(25)
    return login_type
########################################################################################################################
############################################### AUTHENTICATION #########################################################
def authentication(browser,data_list,loginurl):
    print('start authentication...')
    print(browser)
    print(data_list)
    print(loginurl)
    login_type = None
    time.sleep(10) ##############################################//////////////////////////////////////////////////////
    applet_page_response = browser.page_source
    #print(browser.page_source)
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    forms = applet_page_content.findAll('form', recursive=True)
    inputs = applet_page_content.findAll('input', recursive=True)
    buttons = applet_page_content.findAll('button', recursive=True)
    a_links = applet_page_content.findAll('a', recursive=True)
    google_text = False
    google_all_text = False
    google_all = 'One account. All of Google'
    print(inputs)
    print(buttons)
    #############################################
    # handle special case of google services - when already logged in to account
    # check for the link with aria-label="Google Account: Anonymous Bee (anonymousbee94@gmail.com)"
    # try:
    #     print(a_links)
    #     element = browser.find_element(By.XPATH, "//a[@aria-label='" + "Google Account: Anonymous Bee (anonymousbee94@gmail.com)" + "']")
    #     print(element)
    #     return "already logged in", browser
    # except KeyError:
    #     print('not logged into google accoutn')
    #############################################
    #  One account. All of Google.

    # if ((google_all in applet_page_content) or (google_all in applet_page_response)) :#applet_page_response
    #     google_all_text = True
    #     print('Google ALL Sign In')

    #############################################
    #////////////// find button_click to form/sso
    # if not forms:
    input_size = len(inputs)
    c = 0
    for input in inputs:
        if input['type'] == 'hidden':
            c += 1
    print('pass 0')
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
    if (('To continue' in applet_page_content) or ('Continue to'in applet_page_content) or ('Continue to'in applet_page_response) or ('To continue' in applet_page_response)) and (('Not your computer? Use a Private Window to sign in'  in applet_page_content) or ('Not your computer? Use a Private Window to sign in'  in applet_page_response)):#applet_page_response
        google_text = True
        print('Google Sign In')
        if google_all_text:
            google_text = False


    print('pass 1')
    # ##################################################################################################################
    if not google_text and not google_all_text:
        if forms and inputs:
            try:
                try:
                    try:
                        try:
                            try:
                                print('no google text')
                                login_type =  func_form_process(browser,forms, data_list,inputs, buttons, applet_page_content,"",loginurl)
                                time.sleep(20)
                                return login_type, browser
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
    print('pass 2')
    # ########################################### GOOGLE ALL ###########################################################
    # This one works on Firfox browser
    if google_all_text:
        print('Sign in with Google All...')
        div_input = applet_page_content.findAll('input', recursive=True)
        div_button = applet_page_content.findAll('div', {'role': 'button'}, recursive=True)
        form_submitted_count = func_process_google_all_login(browser,div_input, div_button, inputs,forms,data_list)
        login_type = 'sign_with_google_all_count'
        time.sleep(25)
        return login_type, browser
    google_all_text = False
    print('pass 40')
    # ##################################################################################################################
    # ##################################################################################################################
    if not forms:
        if inputs:
            try:
                try:
                    try:
                        try:
                            try:
                                login_type = func_div_input_process(browser,forms,inputs, buttons, applet_page_content, data_list)
                                time.sleep(20)
                                return login_type, browser
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
    print('pass 3')
    # ##################################################################################################################
    # This one works on Firfox browser
    if google_text:
        print('Sign in with Google...')
        div_input = applet_page_content.findAll('input', recursive=True)
        div_button = applet_page_content.findAll('div', {'role': 'button'}, recursive=True)
        form_submitted_count = func_process_google_login(browser,div_input, div_button,data_list)
        login_type = 'sign_with_google_count'
        time.sleep(25)
        return login_type, browser
    google_text = False
    print('pass 4')
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
                                    login_type = func_form_process(browser,forms, data_list, inputs, buttons, applet_page_content,"",loginurl)
                                    #time.sleep(20)
                                    return login_type, browser
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
    print('pass end')
    return login_type,browser
#####################################################  END ##############################################################