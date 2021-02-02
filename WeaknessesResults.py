import requests
import re
from pprint import pprint
import itertools
from urllib.parse import urlparse
import json
import urllib.parse
from pymongo import MongoClient
from  simplejson.errors import JSONDecodeError
import timeit
from threading import Thread
import time
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
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import re
############
options = Options()
options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
serv = Service(r'/root/Tools/Firefox/geckodriver')
browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
browser.set_window_size(1000, 1000)
browser.get('https://ifttt.com/login?wp_=1')
##################
###########################################################################
#token = '0dfb5edac5e2201a9ece7b3908dcfd04d57522b6' #  #1b004674987164ecf6ed87c30146aa90b4c21024 #0dfb5edac5e2201a9ece7b3908dcfd04d57522b6 #c2436a9ef37d65910c1c05f6d137dbb7d79260d4
#remember_token=b9c969f8fc4d28c3207ef1b3838c75233e8246c3
token = 'b9c969f8fc4d28c3207ef1b3838c75233e8246c3'
header = {'Authorization': 'Token token="' + token + '"'}
post_header = {'Authorization': 'Token token="' + token + '"', 'Content-Type':'application/json; charset=utf-8'}
###################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
pcollection = db.get_collection('defaultprivacy')
authcollection =  db.get_collection('authdetailsfortesting')

###################################################################################################################################
current_services = ['bitly','facebook','google_contacts','instapaper','slack', 'date_and_time','maker_webhooks','twitter','youtube','wordpress','withings','weebly',
               'toodledo','todoist','tesco','strava','medium','musixmatch','pocket','reddit','google_docs','google_drive',
               'google_sheets','instagram','fitbit','flickr','gmail', 'email','google_calendar','blogger','dropbox','diigo','evernote',
                'ios_health', 'if_notifications','android_device', 'location','do_button', 'android_phone','android_messages', 'voip_calls','line', 'do_camera',
                'ios_photos', 'ios_reading_list','foursquare', 'android_battery','android_photos', 'qualitytime','ios_reminders', 'ios_contacts','do_note']

action_services36 = {"bitly","google_contacts","instapaper","slack","maker_webhooks","twitter","wordpress","weebly","toodledo","todoist","tesco","strava","musixmatch","pocket",
 "reddit","google_docs","google_drive","google_sheets","fitbit","flickr","gmail","email","google_calendar","blogger","dropbox","diigo","evernote","ios_health",
 "if_notifications","android_device","android_messages","voip_calls","line","ios_photos","ios_reading_list","ios_reminders"}
# not used triggers: date_and_time, maker_webhooks  facebook instagram android_photos
#  bitly  google_contacts instapaper twitter wordpress toodledo todoist strava pocket reddit  google_docs google_drive google_sheets flickr fitbit
# failed applet gen: weebly, gmail, email
#failes applet execu: tesco musixmatch ios_photos ios_reminders ios_reading_list ios_health todoist
servicetesting = 'todoist'
resDB1= client.get_database('applets_'+'facebook' + '_1')
finalresultcollectionupdate1 = resDB1.get_collection('finalresults')
#finalresultcollectionupdate1.remove({'service_idnetifier': servicetesting})
finalresultcollectionupdate1.update({'service_idnetifier': servicetesting}, {'$set': {'actual_text_pry': 'private','actual_url_pry': 'private'}},upsert=True)

resDB2= client.get_database('applets_'+'instagram' + '_1')
finalresultcollectionupdate2 = resDB2.get_collection('finalresults')
#finalresultcollectionupdate2.remove({'service_idnetifier': servicetesting})
finalresultcollectionupdate2.update({'service_idnetifier': servicetesting}, {'$set': {'actual_text_pry': 'private','actual_url_pry': 'private'}},upsert=True)

resDB3= client.get_database('applets_'+'android_photos' + '_1')
finalresultcollectionupdate3 = resDB3.get_collection('finalresults')
finalresultcollectionupdate3.update({'service_idnetifier': servicetesting}, {'$set': {'actual_text_pry': 'private','actual_url_pry': 'public'}},upsert=True)
#finalresultcollectionupdate3.remove({'service_idnetifier': servicetesting})

resDB4= client.get_database('applets_'+'twitter' + '_1')
finalresultcollectionupdate4 = resDB4.get_collection('finalresults')
#finalresultcollectionupdate4.remove({'service_idnetifier': servicetesting})
finalresultcollectionupdate4.update({'service_idnetifier': servicetesting}, {'$set': {'actual_text_pry': 'private','actual_url_pry': 'private'}},upsert=True)
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
#keywords = ['lgn', 'login', 'signin', 'log in', 'sign in', 'sign up', 'signup', 'register', 'error', 'not found', 'notfound']
keywords = ['error loading', 'not found', 'notfound', 'couldnot',"couldn't find" 'could not',"doesn't exist" 'could not load', 'broken', 'removed', 'try drive for your team','protected', 'unable to view'] # load
login_button_names = ['lgn', 'login', 'signin', 'sign_in', 'log_in','authorize']
imagelinkkeywords = ['avatar', 'profile' ,'user', 'thumbnails', 'logo', 'badge', 'icon', 'ads']
imagtypes = ['.jpg', 'png', '.gif']


def urlanalysis(purl, loginurl, service, current_trigger_s, count, recursive_url_list):
    count = count + 1
    print(purl + ': '+str(count))
    is_private_url = False
    is_noise_url = False
    current_trigger_s_strings_to_check = [current_trigger_s]
    services_user_own_urls = ['flickr', 'dropbox', 'google_drive', 'google_docs', 'google_sheets']
    ######################## domain knowledge ########## TODO: ADD SHORTEN URLS GENERATED BY BITLY or IFTTT
    has_definite_public_urls = False
    current_trigger_s_strings_to_check.append('if.tt')
    current_trigger_s_strings_to_check.append('bit.ly')
    if current_trigger_s == 'facebook':
        current_trigger_s_strings_to_check.append('scontent')
    if current_trigger_s == 'android_photos':
        current_trigger_s_strings_to_check.append('locker')
    if current_trigger_s == 'twitter':
        current_trigger_s_strings_to_check.append('t.com')
    if current_trigger_s == 'instagram':
        current_trigger_s_strings_to_check.append('scontent')
        current_trigger_s_strings_to_check.append('instagr.am')
    ######################
    try:
        browser.get(purl)
        time.sleep(5)
        new_page = browser.page_source
        applet_page_content = BeautifulSoup(new_page, "html.parser")
        texts = applet_page_content.findAll(text=True)
        forms = applet_page_content.findAll('form', recursive=True)
        links = applet_page_content.findAll('a', recursive=True)
        imgs = applet_page_content.findAll('img', recursive=True)
        for text in texts:
            if any(ext in text.lower() for ext in keywords):
                is_private_url = True
                #print(text)
                print('is private')
                return is_private_url, is_noise_url
        if not is_private_url:
            # check if purl is the login url of this service
            if not loginurl:
                if loginurl == 'purl':
                    is_private_url = True
                    return is_private_url, is_noise_url

            ## check for login forms
            if not is_private_url:
                for fm in forms:
                    for fk, fv, in fm.attrs.items():
                        if type(fk) is str:
                            if any(ext in fk.lower() for ext in login_button_names):
                                is_private_url = True
                                return is_private_url, is_noise_url
                        if type(fv) is str:
                            if any(ext in fv.lower() for ext in login_button_names):
                                is_private_url = True
                                return is_private_url, is_noise_url
                        if type(fv) is list:
                            for fvi in fv:
                                if any(ext in fvi.lower() for ext in login_button_names):
                                    is_private_url = True
                                    return is_private_url,is_noise_url

            # check if lead to redirection page
            if not is_private_url:
                for text in texts:
                    if 'You are being redirected to an external site' in text:
                        for link in links:
                            try:
                                urlh = link['href']
                                domainh = urlparse(urlh).netloc  # todoist.com
                                if any(ext in domainh.lower() for ext in current_trigger_s_strings_to_check):  # twitter
                                    if urlh not in recursive_url_list:
                                        recursive_url_list.append(urlh)
                                        is_private_url, is_noise_url = urlanalysis(urlh, loginurl, service,
                                                                                   current_trigger_s, count,
                                                                                   recursive_url_list)
                                        if is_private_url:
                                            return is_private_url, is_noise_url
                            except KeyError:
                                pass


            # further check the page contains urls with the current service name in the link
            if not is_private_url:
                domain = urlparse(purl).netloc # todoist.com
                if not any(ext in domain.lower() for ext in current_trigger_s_strings_to_check): # twitter
                    for link in list(set(links)):
                        try:
                            urlh = link['href']
                            if urlh != purl:
                                domainh = urlparse(urlh).netloc  # todoist.com
                                if any(ext in domainh.lower() for ext in current_trigger_s_strings_to_check):  # twitter
                                    if urlh not in recursive_url_list:
                                        recursive_url_list.append(urlh)
                                        is_private_url, is_noise_url = urlanalysis(urlh, loginurl, service,
                                                                                   current_trigger_s,
                                                                                   count, recursive_url_list)
                                        if is_private_url:
                                            return is_private_url, is_noise_url
                                        if not is_private_url:
                                            if current_trigger_s == 'android_photos' and  'locker' in domain:
                                                has_definite_public_urls =True
                                            if current_trigger_s == 'facebook' and  'scontent' in domain:
                                                has_definite_public_urls =True
                                            if current_trigger_s == 'instagram' and  'scontent' in domain:
                                                has_definite_public_urls =True


                        except KeyError:
                            pass
                    if not is_private_url:
                        for img in list(set(imgs)):
                            try:
                                if img['src'] != purl:
                                    urli = img['src']
                                    domaini = urlparse(urli).netloc  # todoist.com
                                    if any(ext in domaini.lower() for ext in current_trigger_s_strings_to_check):  # twitter
                                        if urli not in recursive_url_list:
                                            recursive_url_list.append(urli)
                                            is_private_url, is_noise_url = urlanalysis(urli, loginurl, service,
                                                                                       current_trigger_s,
                                                                                       count, recursive_url_list)
                                            if is_private_url:
                                                return is_private_url, is_noise_url
                                            if not is_private_url:
                                                if current_trigger_s == 'android_photos' and 'locker' in domain:
                                                    has_definite_public_urls = True
                                                if current_trigger_s == 'facebook' and 'scontent' in domain:
                                                    has_definite_public_urls = True
                                                if current_trigger_s == 'instagram' and 'scontent' in domain:
                                                    has_definite_public_urls = True

                            except KeyError:
                                pass


            # extract urls from the text by pattern search
            if not has_definite_public_urls:
                if not is_private_url:
                    domain = urlparse(purl).netloc  # todoist.com
                    if not any(ext in domain.lower() for ext in current_trigger_s_strings_to_check):  # twitter
                        for text in texts:
                            # could be filtered to find
                            newurls = re.findall(r'(https?://[^\s]+)', text)
                            for newurl in newurls:
                                domaini = urlparse(newurl).netloc  # todoist.com
                                if any(ext in domaini.lower() for ext in current_trigger_s_strings_to_check):  # twitter
                                    if newurl not in recursive_url_list:
                                        recursive_url_list.append(newurl)
                                        is_private_url, is_noise_url = urlanalysis(newurl, loginurl, service,
                                                                                   current_trigger_s,
                                                                                   count, recursive_url_list)
                                        if is_private_url:
                                            return is_private_url, is_noise_url


            # find if a noise url

            if not is_private_url and purl not in services_user_own_urls:
                domainx = urlparse(purl).netloc  # todoist.com
                ##################### special case for reddit since reddit include t.com
                if 'reddit' in domainx:
                    try:
                        current_trigger_s_strings_to_check.remove('t.com')
                    except ValueError:
                        pass
                #####################
                if not any(ext in domainx.lower() for ext in current_trigger_s_strings_to_check):  # twitter
                    print('camer here ===================================JACKPOT')
                    is_noise_url =  True



    except WebDriverException:
        pass
    return is_private_url, is_noise_url

def publicurlsanalysis(purls, existing_priv_urls, exnoise_urls,service, resultcolelction, finalresultcollection, stringtype, extrap, current_trigger_s):
    print(len(purls))
    print(purls)
    new_priv_urls = []
    existing_public = purls
    noise_urls = exnoise_urls
    loginurl = None

    for authobject in authcollection.find({'service_idnetifier': service}):
        loginurl = authobject['loginurl']
    ##################
    for priurl in existing_priv_urls:
        if  any(ext in priurl.lower() for ext in imagtypes):
            if any(ext in priurl.lower() for ext in imagelinkkeywords):
                is_noise_url = True
                noise_urls.append(priurl)
                existing_priv_urls.remove(priurl)
    #######################
    for purl in purls :
        print('################')
        print('existing public urls:  ')
        print(existing_public)
        is_noise_url = False
        # #######
        if  any(ext in purl.lower() for ext in imagtypes):
            if any(ext in purl.lower() for ext in imagelinkkeywords):
                is_noise_url = True
                noise_urls.append(purl)
                try:
                    existing_public.remove(purl)
                except ValueError:
                    pass

        # #######
        print('~~~~~~~~~~~~~~~~~~~~~~~~ start analysing the url by its page content~~~~~~~~~~~~~~~~~~~~~~~~~')
        is_private_url, is_noise_url = urlanalysis(purl, loginurl,service, current_trigger_s,0, [])

        if not is_private_url and is_noise_url:
            noise_urls.append(purl)
            try:
                existing_public.remove(purl)
            except ValueError:
                pass
            print('# NOISE Here')
            print(noise_urls)
            print(existing_public)

        # remove incorrectly identified private urls and update public urls
        if not is_private_url and not is_noise_url:
            print('not private and no noise')
            if purl in existing_priv_urls:
                try:
                    existing_priv_urls.remove(purl)
                except ValueError:
                    pass

        if is_private_url:
            new_priv_urls.append(purl)
            existing_public.remove(purl)
            print(existing_public)

    ###############
    new_priv_urls = new_priv_urls + existing_priv_urls
    if stringtype == 'byhtml':
        resultcolelction.update({'service_idnetifier': service},
                                {'$set': {'url_privacy.has_private_url': len(new_priv_urls) > 0,
                                          'url_privacy.private_urls': list(set(new_priv_urls)),
                                          'url_privacy.has_public_url': len(existing_public) > 0,
                                          'url_privacy.public_urls': list(set(existing_public)),
                                          'url_privacy.noise_urls': list(set(noise_urls))}},
                                upsert=True)
    else:
        resultcolelction.update({'service_idnetifier': service},
                                {'$set': {'url_privacy.' + extrap + '.has_private_url': len(new_priv_urls) > 0,
                                          'url_privacy.' + extrap + '.private_url': list(set(new_priv_urls)),
                                          'url_privacy.' + extrap + '.public_url': list(set(existing_public)),
                                          'url_privacy.' + extrap + '.has_public_url': len(existing_public) > 0,
                                          'url_privacy.' + extrap + '.noise_urls': list(set(noise_urls))}}, upsert=True)
    finaltype = 'NA'
    if len(new_priv_urls) > 0:
        finaltype = 'private'
    if len(existing_public) > 0:
        finaltype = 'public'

    finalresultcollection.update({'service_idnetifier': service}, {
        '$set': {'url_privacy_' + stringtype: finaltype, 'has_private_urls': len(new_priv_urls) > 0,
                 'has_public_urls': len(existing_public) > 0}}, upsert=True)

def analyze_action_services_to_infer_privacy_further(testlist, v2check):
    for current_trigger_service in testlist:
        ######################################## SETU UP service ########################################################################
        # current_trigger_service = 'instagram'  # facebook  instagram twitter android_photos
        print(' trigger service :    ==============> ' + current_trigger_service)
        resDB = client.get_database('applets_' + current_trigger_service + '_1')
        if not v2check:
            resultcollectionByText = resDB.get_collection('textdiff')
            resultcollectionByHtml = resDB.get_collection('htmldiff')
            finalresultcollection = resDB.get_collection('finalresults')
        else:
            resultcollectionByText = resDB.get_collection('textdiff')
            resultcollectionByHtml = resDB.get_collection('v2htmldiff')
            finalresultcollection = resDB.get_collection('v2finalresults')


        ###################################################################################################################################

        ########################## text analysis
        for textdet in resultcollectionByText.find({}):
            service = textdet['service_idnetifier']
            # if not service == 'reddit':
            #     continue
            print(service)
            found_privacy_text = False
            found_privacy_url = False
            # remove incorrect fields
            resultcollectionByText.update({'service_idnetifier': service}, {
                '$unset': {'private_urls': "", 'public_urls': "", 'has_public_url': "", 'public_url': "",
                           'url_privacy.public_urls': ""}}, upsert=True)
            ###### start here
            for x, y in textdet['text_privacy'].items():
                has_public_txt = False
                if y['has_private_text'] and not has_public_txt:
                    finalresultcollection.update({'service_idnetifier': service},
                                                 {'$set': {'text_privacy_bytxt': 'private'}}, upsert=True)
                    found_privacy_text = True
                if y['has_public_text']:
                    has_public_txt = True
                    found_privacy_text = True
                    finalresultcollection.update({'service_idnetifier': service},
                                                 {'$set': {'text_privacy_bytxt': 'public'}}, upsert=True)
            for x, y in textdet['url_privacy'].items():
                try:
                    if len(y['private_url']) > 0 and not len(y['public_url']) > 0:
                        finalresultcollection.update({'service_idnetifier': service},
                                                     {'$set': {'url_privacy_bytxt': 'private',
                                                               'has_private_urls': True}},
                                                     upsert=True)
                except KeyError:
                    continue
                purls = list(set(y['public_url']))
                priurls = list(set(y['private_url']))
                noise_urls = []
                try:
                    noise_urls = list(set(y['noise_urls']))
                except KeyError:
                    pass

                if len(purls) > 0 and '...' not in x:  # or len(priurls) > 0:
                    print(x)
                    print('check abve')
                    existing_priv_urls = list(set(y['private_url']))
                    resultcollectionByText.update({'service_idnetifier': service},
                                                  {'$set': {'url_privacy.' + x + '.has_public_url': True,
                                                            'url_privacy.' + x + '.public_url': list(set(purls))}},
                                                  upsert=True)
                    publicurlsanalysis(purls, existing_priv_urls, noise_urls, service, resultcollectionByText,
                                       finalresultcollection, 'bytxt', x, current_trigger_service)
                print('################################## DONE FOR BY TEXT ############################################')

            ############################### html analysis ##############
            for htmldet in resultcollectionByHtml.find({'service_idnetifier': service}):
                textpry = htmldet['text_privacy']
                urlpry = htmldet['url_privacy']
                has_public_txt = False
                has_public_url = False
                # remove incorrect fields
                resultcollectionByHtml.update({'service_idnetifier': service}, {
                    '$unset': {'private_urls': "", 'public_urls': "", 'has_public_url': "", 'public_url': ""}},
                                              upsert=True)
                ###### start here
                if textpry['has_private_text'] and not has_public_txt:
                    found_privacy_text = True
                    finalresultcollection.update({'service_idnetifier': service},
                                                 {'$set': {'text_privacy_byhtml': 'private'}},
                                                 upsert=True)
                if textpry['has_public_text']:
                    has_public_txt = True
                    found_privacy_text = True
                    finalresultcollection.update({'service_idnetifier': service},
                                                 {'$set': {'text_privacy_byhtml': 'public'}},
                                                 upsert=True)
                if urlpry['has_private_url'] and not has_public_url:
                    found_privacy_url = True
                    finalresultcollection.update({'service_idnetifier': service},
                                                 {'$set': {'url_privacy_byhtml': 'private', 'has_private_urls': True}},
                                                 upsert=True)
                purls = list(set(urlpry['public_urls']))
                priurls = list(set(urlpry['private_urls']))
                noise_urls = []
                try:
                    noise_urls = list(set(urlpry['noise_urls']))
                except KeyError:
                    pass

                if len(purls) > 0 or len(priurls) > 0:
                    existing_priv_urls = urlpry['private_urls']
                    resultcollectionByHtml.update({'service_idnetifier': service},
                                                  {'$set': {'url_privacy.has_public_url': True,
                                                            'url_privacy.private_urls': list(set(purls))}},
                                                  upsert=True)
                    publicurlsanalysis(purls, existing_priv_urls, noise_urls, service, resultcollectionByHtml,
                                       finalresultcollection, 'byhtml', '', current_trigger_service)

                # for col in pcollection.find({'service_idnetifier': service}):
                #     def_privacy = col['default_privacy']
                #     finalresultcollection.update({'service_idnetifier': service}, {'$set': {'default_privacy': def_privacy}},
                #                                  upsert=True)
                print(
                    '################################## DONE FOR BY HTML ############################################')

def analyze_TAIPbyAS_to_infer_privacy_further(testlist, v2check):
    for current_trigger_service in testlist:
        ######################################## SETU UP service ########################################################################
        # current_trigger_service = 'instagram'  # facebook  instagram twitter android_photos
        print(' trigger service :    ==============> ' + current_trigger_service)
        resDB = client.get_database('applets_' + current_trigger_service + '_1')
        ### decide result db
        if not v2check:
            finalresultcollection = resDB.get_collection('v1finalresults')
        else:
            finalresultcollection = resDB.get_collection('v2finalresults')
        ###################################################################################################################################
        # get urls from the applet succeed db
        # urls are  - content_url and content_image_url
        ###### first get generated applet ID from the applet collection in evalapplets db
        applet_folder_name = 'applets_' + current_trigger_service + '_1'
        appDB = client.get_database('evalapplets')
        applcollec = appDB.get_collection(applet_folder_name)
        for app in applcollec.find({}):
            appletID = app['applet_id']
            aservice = app['action_service']
            loginurl = None
            for authobject in authcollection.find({'service_idnetifier': aservice}):
                loginurl = authobject['loginurl']
            ###### search for the applet ID to check it was suuceed in succeed collection
            record = resDB.get_collection('succeed').find({'applet_id': appletID})
            if record.count() == 0:
                print('applet scceed not found')
            else:
                for rec in record:
                    content_image_url = None
                    content_url = None
                    ###### if exists there, get URLs of two types
                    try:
                        content_image_url = rec['trigger_data']['content_image_url']
                    except KeyError:
                        pass
                    try:
                        content_url = rec['trigger_data']['content_url']
                    except KeyError:
                        pass
                    ####### check the accessiblity of the URLS
                    is_private_imgurl = ''
                    is_private_url = ''
                    url_privacy = ''
                    if not v2check:                        ### for V1 check use the urlanalysis ()
                        if content_image_url is not None:
                            #print(content_image_url)
                            is_private_imgurl, is_noise_imgurl = urlanalysis(content_image_url, loginurl, aservice, current_trigger_service, 0, [])
                            if is_private_imgurl:
                                url_privacy = 'private'
                            if not is_private_imgurl:
                                url_privacy = 'public'

                        if url_privacy != 'public':
                            if content_url is not None:
                                #is_private_url, is_noise_url = urlanalysis(content_url, loginurl, aservice, current_trigger_service, 0, [])
                                response = requests.get(content_url, timeout=10)
                                print(response.status_code)
                                if response.status_code == 400:
                                    url_privacy = 'private'
                                if response.status_code == 200:
                                    url_privacy = 'public'

                                # if is_private_url:
                                #     url_privacy = 'private'
                                # if not is_private_url:
                                #     url_privacy = 'public'

                        has_content_image_url = False
                        has_content_url = False
                        if content_url  is not None:
                            has_content_url =  True
                        if content_image_url  is not None:
                            has_content_image_url =  True

                        finalresultcollection.update({'service_idnetifier': aservice}, {
                            '$set': {'TAIP_url_privacy' : url_privacy, 'content_image_url': has_content_image_url, 'content_url':has_content_url }}, upsert=True)



        #### for V2 check the accessiblity by requests.get by response code


        # publicurlsanalysis(purls, existing_priv_urls, noise_urls, service, resultcollectionByHtml,
        #                                finalresultcollection, 'byhtml', '', current_trigger_service)


        print('################################## DONE FOR BY TAIP feed ############################################')

###########################################################################################################
###########################################################################################################
########################################### V1 or V2 action service #############################################
testlist = []#['android_photos'] #['instagram']#['facebook', 'twitter','instagram', 'android_photos']

for i in range(3): ## increase the number
    print('ROUND ' + str(i) + ' STARTING ............. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    v2_check = True ######## critical
    analyze_action_services_to_infer_privacy_further(testlist, v2_check)


###########################################################################################################
###########################################################################################################
############################################# V2 TAIP #####################################################
testlist = []#['android_photos']#['facebook', 'twitter','instagram', 'android_photos']
for i in range(3): ## increase the number
    print('ROUND ' + str(i) + ' STARTING for TAIP............. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    v2_check = False ######## critical
    analyze_TAIPbyAS_to_infer_privacy_further(testlist, v2_check)
###########################################################################################################
###########################################################################################################
###########################################################################################################
browser.quit()
action_services36_mobile = {"ios_health", "if_notifications","android_device","android_messages","voip_calls","line","ios_photos","ios_reading_list","ios_reminders"}
# for current_trigger_service in testlist:
#     resDB = client.get_database('applets_' + current_trigger_service + '_1')
#     finalresultcollection = resDB.get_collection('finalresults')
#
#     for assm in action_services36_mobile:
#         finalresultcollection.update({'service_idnetifier': assm}, {
#             '$set': {'url_privacy_byhtml' : 'manual' }}, upsert=True)
#         finalresultcollection.update({'service_idnetifier': assm}, {
#             '$set': {'url_privacy_bytxt' : 'manual' }}, upsert=True)
#         finalresultcollection.update({'service_idnetifier': current_trigger_service}, {
#             '$unset': {'url_privacy_bytext': ""}}, upsert=True)

##########################################################################################################
######################################## Creating Backups #################################################
current_trigger_servicees = []#['android_photos']# ['instagram']#['facebook', 'twitter','android_photos', 'instagram']#instagram
for current_trigger_servicee in current_trigger_servicees:
    print(' trigger service :    ==============> ' + current_trigger_servicee)
    resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
    resultcollectionByText = resDB.get_collection('textdiff')
    resultcollectionByHtml = resDB.get_collection('htmldiff')
    bkpresultcollectionByText = resDB.get_collection('bkptextdiff')
    bkpresultcollectionByHtml = resDB.get_collection('bkphtmldiff')
    v2resultcollectionByText = resDB.get_collection('v2textdiff')
    v2resultcollectionByHtml = resDB.get_collection('v2htmldiff')
    ##  for v2 create new collection
    try:
        for rebhtml in bkpresultcollectionByHtml.find({}):
            v2resultcollectionByHtml.insert_one(rebhtml)
    except Exception:
        pass

    # try:
    #     for rebhtml in resultcollectionByHtml.find({}):
    #         bkpresultcollectionByHtml.insert_one(rebhtml)
    # except Exception:
    #     pass

##############################################################################################################
############################################# check correctness of resutls and V1 ##############################
current_trigger_serviceess =[]# ['facebook', 'twitter','android_photos', 'instagram']#instagram
for current_trigger_servicee in current_trigger_serviceess:
    print(' trigger service :    ==============> ' + current_trigger_servicee)
    resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
    finalresultcollection = resDB.get_collection('finalresults')
    db = client['services']
    pcollection = db.get_collection('defaultprivacy')
    ##################################################
    actual_trigger_text_privacy = 'private'
    actual_trigger_url_privacy = 'private'
    ##################################################
    for fres in finalresultcollection.find({}):
        service = fres['service_idnetifier']
        urlpribyhtml = ''
        txtpribyhtml = ''
        urlpribytxt = ''
        txtpribytxt = ''
        actualurlpry = ''
        actualtextpry = ''
        try:
            urlpribyhtml = fres['url_privacy_byhtml']
        except KeyError:
            pass
        try:
            txtpribyhtml = fres['text_privacy_byhtml']
        except KeyError:
            pass
        try:
            urlpribytxt = fres['url_privacy_bytxt']
        except KeyError:
            pass
        try:
            txtpribytxt = fres['text_privacy_bytxt']
        except KeyError:
            pass
        try:
            actualurlpry = fres['actual_url_pry']
        except KeyError:
            pass
        try:
            actualtextpry = fres['actual_text_pry']
        except KeyError:
            pass

        ### TAIP BY default privacy when cannot find by keywords
        if txtpribyhtml == '':
            ## get the default privacy of the service
            for apry in pcollection.find({'service_idnetifier': service}):
                txtpribyhtml = apry['default_privacy']
        # find weaknesses from the actuals
        violation_bytext = False
        violation_byurl = False
        if actualurlpry != '':
            if actualurlpry != 'NA':
                if actual_trigger_url_privacy != actualurlpry:
                    violation_byurl = True
            else:
                violation_byurl = False
        else:
            violation_byurl = ''
        ####
        if actualtextpry != '':
            if actualtextpry != 'NA':
                if actual_trigger_text_privacy != actualtextpry:
                    violation_bytext = True
            else:
                violation_bytext = False

        else:
            violation_bytext = ''
        finalresultcollection.update({'service_idnetifier': service}, {'$set': {'V3_text' : violation_bytext, 'V3_url' : violation_byurl}}, upsert=True)

        # find accuracy of inferred  privacy
        correct_urlpry_bytxt = False
        correct_urlpry_byhtml = False
        correct_textpry_bytxt = False
        correct_textpry_byhtml = False

        if urlpribyhtml != 'manual' and urlpribyhtml != '':
            if actualurlpry == urlpribyhtml:
                correct_urlpry_byhtml = True
        else:
            correct_urlpry_byhtml = ''
        ######
        if urlpribytxt != 'manual' and urlpribytxt != '':
            if actualurlpry == urlpribytxt:
                correct_urlpry_bytxt = True
        else:
            correct_urlpry_bytxt = ''
        ######
        if txtpribyhtml != 'manual' and txtpribyhtml != '':
            if actualtextpry == txtpribyhtml:
                correct_textpry_byhtml = True
        else:
            correct_textpry_byhtml = ''
        ######
        if txtpribytxt != 'manual' and txtpribytxt != '':
            if actualtextpry == txtpribytxt:
                correct_textpry_bytxt = True
        else:
            correct_textpry_bytxt = ''
        ######
        finalresultcollection.update({'service_idnetifier': service},
                                     {'$set': {'correct_urlpry_bytxt ': correct_urlpry_bytxt,
                                               'correct_urlpry_byhtml': correct_urlpry_byhtml,
                                               'correct_textpry_bytxt ': correct_textpry_bytxt,
                                               'correct_textpry_byhtml': correct_textpry_byhtml }}, upsert=True)

##########################################################################################################
############################################# !!!!!!!! get statistics !!!!!!!!!1###################################
action_services36here = ["bitly","google_contacts","instapaper","slack","maker_webhooks","twitter","wordpress","weebly","toodledo","todoist","tesco","strava","musixmatch","pocket",
 "reddit","google_docs","google_drive","google_sheets","fitbit","flickr","gmail","email","google_calendar","blogger","dropbox","diigo","evernote","ios_health",
 "if_notifications","android_device","android_messages","voip_calls","line","ios_photos","ios_reading_list","ios_reminders"]
current_trigger_servicees = ['android_photos']#['facebook']#['android_photos']#['twitter']#['facebook', 'twitter','android_photos', 'instagram']#
for current_trigger_servicee in current_trigger_servicees:
    print(' trigger service :    ==============> ' + current_trigger_servicee)
    # resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
    # finalresultcollection = resDB.get_collection('v2finalresults') ###### change this accordingly: v1finalresults, finalresults
    #########################
    applet_folder_name = 'applets_' + current_trigger_servicee + '_1'
    appDB = client.get_database('evalapplets')
    applcollec = appDB.get_collection(applet_folder_name)
    ###############
    # db = client['services']
    # finalresultcollection = db.get_collection('defaultprivacy')
    ###############
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    executed_total = 0
    for aservice in action_services36here:
        #print(aservice)
        resultfors = applcollec.find({'action_service':aservice})#action_service ##service_idnetifier
        if resultfors.count() == 0:
            print('-')
            #pass

        for result in resultfors:
            #print(result)
            try:
                v3_result = result['action_fields']#////
                # V1 TAIP = TAIP_url_privacy
                # V1 = 'taifu_V1_text ', taifu_V1_url
                # V3_text, V3_url, correct_urlpry_byhtml. 'correct_urlpry_bytxt ', correct_textpry_byhtml, correct_textpry_bytxt, 'executed ', v4
                if v3_result == '':
                    v3_result = '-'
                ############ #
                # count TP, TN, FP, FN
                if v3_result == 'TP':
                    TP = TP + 1
                if v3_result == 'TN':
                    TN = TN + 1
                if v3_result == 'FP':
                    FP = FP + 1
                if v3_result == 'FN':
                    FN = FN + 1
                ############ #
                if v3_result:
                    executed_total = executed_total +1

                print(v3_result)
            except KeyError:
                print('-')
    print( 'TP =' + str(TP))
    print('TN =' + str(TN))
    print('FP =' + str(FP))
    print('FN =' + str(FN))
    print('executed_total =' + str(executed_total))

#########################################################################################################################
############################################ executed status ############################################################
facebook	=['strava', 'android_device', 'ios_health', 'line', 'diigo', 'ios_photos', 'twitter', 'ios_reading_list', 'if_notifications', 'slack', 'reddit', 'dropbox', 'google_calendar', 'todoist', 'evernote', 'flickr', 'fitbit', 'android_messages', 'google_drive', 'pocket', 'toodledo', 'wordpress', 'google_contacts', 'ios_reminders', 'voip_calls', 'google_docs', 'google_sheets', 'bitly', 'blogger', 'instapaper']
instagram	= ['bitly', 'android_device', 'fitbit', 'evernote', 'if_notifications', 'flickr', 'ios_reading_list', 'android_messages', 'wordpress', 'toodledo', 'google_docs', 'blogger', 'instapaper', 'strava', 'ios_photos', 'ios_health', 'google_calendar', 'google_drive', 'google_sheets', 'todoist', 'ios_reminders', 'diigo', 'voip_calls', 'line', 'pocket', 'slack', 'reddit', 'dropbox']
android_photos = ['slack', 'pocket', 'google_sheets', 'google_calendar', 'instapaper', 'wordpress', 'evernote', 'toodledo', 'flickr', 'line', 'dropbox', 'ios_health', 'todoist', 'blogger', 'twitter', 'fitbit', 'google_drive', 'voip_calls', 'strava', 'android_device', 'if_notifications', 'ios_reading_list', 'reddit', 'android_messages', 'ios_reminders', 'diigo', 'ios_photos', 'bitly', 'google_docs']
twitter = ['blogger', 'wordpress', 'bitly', 'diigo', 'instapaper', 'pocket', 'google_calendar', 'dropbox', 'google_docs', 'google_drive', 'google_sheets', 'line', 'slack', 'fitbit', 'strava', 'android_device', 'ios_health', 'ios_reading_list', 'ios_reminders', 'evernote', 'android_messages', 'if_notifications', 'voip_calls', 'flickr', 'ios_photos', 'reddit', 'todoist', 'toodledo']
current_trigger_servicees = ['facebook', 'twitter','android_photos', 'instagram']#instagram
# for current_trigger_servicee in current_trigger_servicees:
#     print(' trigger service :    ==============> ' + current_trigger_servicee)
#     resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
#     finalresultcollectionr = resDB.get_collection('finalresults')
#     related_service_array = []
#     if current_trigger_servicee == 'facebook':
#         related_service_array = facebook
#     if current_trigger_servicee == 'instagram':
#         related_service_array = instagram
#     if current_trigger_servicee == 'android_photos':
#         related_service_array = android_photos
#     if current_trigger_servicee == 'twitter':
#         related_service_array = twitter
#
#     for rservice in related_service_array:
#         finalresultcollectionr.update({'service_idnetifier': rservice}, {'$set': {'executed ': True }}, upsert=True)
#########################################################################################################################
############################################ V4 #########################################################################
db = client['services']
pcollection = db.get_collection('defaultprivacy')
privatekeywords = ['private', 'personal', 'onlyme', 'only me', 'only you', 'privacy']
publickeywords = ['temporarypublic']# ['public', 'everyone', 'anyone', 'privacy'] #['temporarypublic']#
allprivacykywrds = privatekeywords + publickeywords
#############
current_trigger_serviceess =[]# ['android_photos']#['facebook', 'twitter','android_photos', 'instagram']
for current_trigger_servicee in current_trigger_serviceess:
    applet_folder_name = 'applets_' + current_trigger_servicee + '_1'
    appDB = client.get_database('evalapplets')
    applcollec = appDB.get_collection(applet_folder_name)
    for aservice in action_services36here:
        if applcollec.find({'action_service':aservice}).count() == 0:
            print('-')
        app = applcollec.find_one({'action_service':aservice})
        #for app in applcollec.find({'action_service':aservice}):
        if app is not None:
            triggerfields = app['trigger_fields']
            actionfields = app['action_fields']
            aservicename = app['action_service']
            resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
            v4finalresultcollection = resDB.get_collection('finalresults')
            #######
            actionservicehaspryconfigs = False
            for apry in pcollection.find({'service_idnetifier': aservicename}):
                actionservicehaspryconfigs = apry['has_privacy_configs']
            triggerservicehaspryconfigs = False
            for apry in pcollection.find({'service_idnetifier': current_trigger_servicee}):
                triggerservicehaspryconfigs = apry['has_privacy_configs']
            # privatekeywords, publickeywords
            ##### check privacy at trigger fields
            triggerfieldhasaccesscontrol = False
            actionfieldhasaccesscontrol = False
            for x, y in triggerfields.items():
                if type(x) is list:
                    x = ''.join(x)
                if type(y) is list:
                    y = ''.join(y)
                if any(ext in x.lower() for ext in allprivacykywrds) or any(
                        ext in y.lower() for ext in allprivacykywrds):
                    triggerfieldhasaccesscontrol = True
            for x, y in actionfields.items():
                if type(x) is list:
                    x = ''.join(x)
                if type(y) is list:
                    y = ''.join(y)
                if any(ext in x.lower() for ext in allprivacykywrds) or any(
                        ext in y.lower() for ext in allprivacykywrds):
                    actionfieldhasaccesscontrol = True
            ###### check v4
            # print('#########')
            print(actionfieldhasaccesscontrol) #triggerfieldhasaccesscontrol  actionfieldhasaccesscontrol
            # print(triggerhaspry)
            # print(triggerhasaccesscontrol)#
            # print(actionfields)
            # print(actionhaspry)
            # print(actionhasaccesscontrol)
            # print('###########')
            v4exists = False
            if triggerservicehaspryconfigs and not triggerfieldhasaccesscontrol and actionservicehaspryconfigs and not actionfieldhasaccesscontrol:
                v4exists = True

            if not triggerservicehaspryconfigs and not triggerfieldhasaccesscontrol and actionservicehaspryconfigs and not actionfieldhasaccesscontrol:
                v4exists = True

            if triggerservicehaspryconfigs and not triggerfieldhasaccesscontrol and not actionservicehaspryconfigs and not actionfieldhasaccesscontrol:
                v4exists = True

            v4finalresultcollection.update({'service_idnetifier': aservicename}, {'$set': {'v4': v4exists}},
                                           upsert=True)


#########################################################################################################################
############################################ V5 #########################################################################
current_trigger_serviceessss = ['instagram']#['facebook', 'twitter','android_photos', 'instagram']
for current_trigger_servicee in current_trigger_serviceessss:
    print(' trigger service :    ==============> ' + current_trigger_servicee)
    resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
    succssexecutionscollect = resDB.get_collection('succeed')
    v5finalresultcollection = resDB.get_collection('finalresults')
    ##################
    applet_folder_name = 'applets_' + current_trigger_servicee + '_1'
    appDB = client.get_database('evalapplets')
    applcollec = appDB.get_collection(applet_folder_name)
    truecount = 0
    falsecount = 0

    for aservice in action_services36here:
        if applcollec.find({'action_service':aservice}).count() == 0:
            print('-')
        app = applcollec.find_one({'action_service':aservice})
        #for app in applcollec.find({'action_service':aservice}):
        if app is not None:
            #for app in applcollec.find({}):
            appletid = app['applet_id']
            action_fields = app['action_fields']
            ingridients = ''
            for ak, av in action_fields.items():
                action_fields_string = json.dumps(av)
                p = re.findall(r'(\{\{[^\s^}]+\}\})', action_fields_string)#("\{\{SourceUrl\}\}")
                i = 0
                for p1 in p:
                    if i>0:
                        ingridients = ingridients + ', '

                    ingridients = ingridients + p1
                    #i = i +1

            #print(ingridients)

            aservicename = app['action_service']
            action_fields_string = json.dumps(action_fields)
            # check fields requested
            has_imageurl_infields = False
            has_url_infields = False
            if any(ext in action_fields_string.lower() for ext in ['photourl', 'imageurl', 'imagesource', 'sourceurl']):
                has_imageurl_infields = True
                action_fields_string.replace('photourl', '')
                action_fields_string.replace('imageurl', '')
                action_fields_string.replace('imagesource', '')

            if any(ext in action_fields_string.lower() for ext in ['url','link']):
                has_url_infields = True
            ### check extracted trigger data by TAIP
            has_imageurl_inTAIP = False
            has_url_inTAIP = False
            extracted_data_string = ''
            for sresutl in succssexecutionscollect.find({'applet_id': 'Xg6vqykh'}):#
                extracted_data = sresutl['trigger_data']
                extracted_data_string = json.dumps(extracted_data)
                if 'content_url' in extracted_data_string:
                    has_url_inTAIP = True
                if 'content_image_url' in extracted_data_string:
                    has_imageurl_inTAIP = True
                if not has_url_inTAIP and not has_imageurl_inTAIP:
                    has_url_inTAIP = False
                    has_imageurl_inTAIP = False

                ###### check v4
                #print('#########')
                # print(action_fields_string.lower())  #
                #print(has_imageurl_infields)
                #print(has_url_infields)
                # print(extracted_data_string.lower())
                #print(has_imageurl_inTAIP)
                #print(has_url_inTAIP)
                # if has_imageurl_infields:
                #     truecount = truecount +1
                # else:
                #     falsecount = falsecount + 1

                ######################### check v5
                v5 = False
                if not has_imageurl_infields and has_imageurl_inTAIP:
                    v5 = True
                else:
                    if not has_imageurl_infields and has_url_infields and has_imageurl_inTAIP:
                        v5 = True

                #print('v5:' + str(v5))
                #print(v5)
                if v5:
                    truecount = truecount +1
                else:
                    falsecount = falsecount + 1
                v5finalresultcollection.update({'service_idnetifier': aservicename}, {'$set': {'v5': v5}}, upsert=True)
                #print('###########')
    # print('true '+ str(truecount))
    # print('false ' + str(falsecount))
    print(str(truecount))
    print(str(falsecount))
##############################################################################################################
############################################# V1 FINAL RESULTS ################ ##############################
current_trigger_serviceessq = [] #['facebook', 'twitter','android_photos', 'instagram']#instagram
for current_trigger_servicee in current_trigger_serviceessq:
    print(' trigger service :    ==============> ' + current_trigger_servicee)
    resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
    finalresultcollection = resDB.get_collection('finalresults')
    v1finalresultcollection = resDB.get_collection('v1finalresults')
    for fres in finalresultcollection.find({}):
        service = fres['service_idnetifier']
        ### ground truth for v1
        v1_text_gt = fres['V3_text']
        v1_url_gt = fres['V3_url']
        #### TAIFU results
        correctnss_of_url_pry = fres['correct_urlpry_byhtml']
        correctnss_of_text_pry = fres['correct_textpry_byhtml']
        ######## final results VIOLATEION, TP, FP,
        taifu_V1_text = ''
        taifu_V1_url = ''

        if v1_text_gt != '' and correctnss_of_text_pry != '':
            if v1_text_gt and correctnss_of_text_pry:
                taifu_V1_text = 'TP'
            if not v1_text_gt and not correctnss_of_text_pry:
                taifu_V1_text = 'FP'
            if not v1_text_gt and  correctnss_of_text_pry:
                taifu_V1_text = 'TN'
            if  v1_text_gt and  not correctnss_of_text_pry:
                taifu_V1_text = 'FN'

        if v1_url_gt != '' and correctnss_of_url_pry != '':
            if v1_url_gt and correctnss_of_url_pry:
                taifu_V1_url = 'TP'
            if not v1_url_gt and not correctnss_of_url_pry:
                taifu_V1_url = 'FP'
            if not v1_url_gt and  correctnss_of_url_pry:
                taifu_V1_url = 'TN'
            if  v1_url_gt and  not correctnss_of_url_pry:
                taifu_V1_url = 'FN'

        v1finalresultcollection.update({'service_idnetifier': service}, {'$set': {'taifu_V1_text ': taifu_V1_text, 'taifu_V1_url': taifu_V1_url}}, upsert=True)


#########################################################################################################################
############################################ V1 and V2 at TAIP##################################################################
########### SET Or UNSET sepcific values
current_trigger_servicees =[]#['android_photos']# ['twitter']#['facebook', 'twitter','android_photos', 'instagram']#instagram
for current_trigger_servicee in current_trigger_servicees:
    print(' trigger service :    ==============> ' + current_trigger_servicee)
    resDB = client.get_database('applets_' + current_trigger_servicee + '_1')
    # finalresultcollection = resDB.get_collection('finalresults')
    # finalresultcollection.update({'service_idnetifier': 'google_calendar'}, {'$set': {'actual_url_pry': 'public' }}, upsert=True)
    # finalresultcollection.update({'service_idnetifier': 'google_calendar'}, {
    #     '$unset': {'actual_url_pry ': ""}}, upsert=True)