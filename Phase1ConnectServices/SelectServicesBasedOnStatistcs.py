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

uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client.get_database('services')
collection = db.get_collection('authdetails')
evalcollection = db.get_collection('evalauth')
catcollection = db.get_collection('categories')
newexappletstats = db.get_collection('userstats')
all_auth_details = collection.find({})

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
############################################# Loop throught the services list ##########################################
for recored in collection.find({}):
    category = ''
    serviceid =''
    appletorconnection = ''
    try:
        serviceid = recored['service_idnetifier']

        # if 'wirelesstag' not in serviceid:
        #     continue
        print(serviceid)
    except KeyError:
        continue

    try:
        browser.get('https://ifttt.com/' + serviceid)
        time.sleep(2)# time to load the page
    except WebDriverException:
        continue
    ####################################### get service cateogry
    # for catd in catcollection.find({}):
    #     catname = catd['category']
    #     servicelist = catd['services']
    #     if serviceid in servicelist:
    #         category = catname
    #######################################

    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    allli = applet_page_content.findAll('li', {'class': 'my-web-applet-card web-applet-card'})#, recursive=True)

    for lie in allli:# get all the applet list
        appletid = ''
        title = ''
        author = ''
        installations = 0
        triggerservice = 0
        actionservice = 0
        oththerservices = []

        links = lie.findChildren("a")
        for link in links:
            if 'connect' not in link['href']: # to filter connect card
                appletid = link['href'].split('/')[2]
                appletorconnection = link['href'].split('/')[1]
        appletalreadyin = False
        for r in newexappletstats.find({'appletid': appletid}):
            appletalreadyin = True
        if appletalreadyin:
            break

        ####################### CONTENT: title and author ##############################################################
        divcontent = lie.findChildren("div", attrs={"class": "content"})#, recursive=True) # get title and author
        for content in divcontent:
            spantitle = content.findChildren("span", attrs={"class": "title"}, recursive=True)  # get title
            for titl in spantitle:
                title = titl.text
            spanauthor = content.findChildren("span", attrs={"class": "author"}, recursive=True) # get author
            for authr in spanauthor:
                author = authr.text
        ####################### META DATA: user stats ##################################################################
        divmeta = lie.findChildren("div", attrs={"class": "meta"})#, recursive=True)
        #print(divmeta)
        for meta in divmeta:
            divstat = meta.findChildren("div", attrs={"class": "installs"}, recursive=True)
            for ustat in divstat:
                installations = ustat.text
                if 'k' in installations:
                    withoutkvalue = installations.split('k')[0]
                    withoutkvalue = float(withoutkvalue)
                    actualvalue = withoutkvalue*1000
                    installations = int(actualvalue)


        ####################### SERVICES: TRIGGER AND ACTION ###########################################################
        divwork = lie.findChildren("div", attrs={"class": "works-with"})#, recursive=True)
        #print(divwork)
        for work in divwork:
            servicelist = work.findChildren("li",  recursive=True)
            counter = 0
            for service in servicelist:
                imglink = service.findChildren("img", recursive=True)
                for imgl in imglink:
                    if counter == 0:
                        triggerservice = imgl['title']
                        counter = counter + 1
                    if counter == 1:
                        actionservice = imgl['title']
                    else:
                        oththerservices.append(imglink['title'])

            # get the identities of these services
            tsrecord = collection.find({'service_name': triggerservice})
            for x in tsrecord:
                triggerservice = x['service_idnetifier']
            asrecord = collection.find({'service_name': actionservice})
            for y in asrecord:
                actionservice = y['service_idnetifier']

            if appletid != '':
                print(appletid)
                print(title)
                print(author)
                print(installations)
                print(triggerservice)
                print(actionservice)
                newexappletstats.find_one_and_update({'applet_id': appletid}, {
                    "$set": {'title': title, 'author': author, 'installations': installations,
                             'trigger_service': triggerservice, 'action_service': actionservice, 'other': oththerservices, 'type':appletorconnection}}, upsert=True)
                print('###################################################################################################')
browser.quit()
        ################################################################################################################
