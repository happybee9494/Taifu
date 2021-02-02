import scrapy
from bson import ObjectId
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import hashlib
import os
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from multiprocessing import Process, Queue
from scrapy_selenium import SeleniumRequest
from scrapy.http.cookies import CookieJar
from Taifu.BehaviorMonitoring_NoiseTemplates.tatester.tatester.spiders.AuthenticateAndAuthorizeServiceForEval import authentication
#from Taifu.Phase1ConnectServices.AuthenticateAndAuthorizeServiceForEval import authentication

import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy_splash import SplashRequest, SplashFormRequest,SlotPolicy
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from pymongo import MongoClient
import timeit
from threading import Thread
from multiprocessing.pool import ThreadPool
import time
# Scrapy:  https://github.com/scrapy/scrapy # https://blog.scrapinghub.com/2016/03/23/scrapy-tips-from-the-pros-march-2016-edition
# Splash: http://scrapingauthority.com/scrapy-javascript # Docs:https://splash.readthedocs.io/en/stable/api.html
# http://devdoc.net/python/scrapy-splash.html
# https://stackoverflow.com/questions/45886068/scrapy-crawlspider-splash-how-to-follow-links-through-linkextractor
# Selenium: http://mroseman.com/scraping-dynamic-pages/#integration
script_started = timeit.default_timer()
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
#ollection = db.get_collection('monitorauthdetails')
#collection = db.get_collection('evalauthdetails')# use a new collection for evaluation of 105 services
collection =  db.get_collection('authdetailsfortesting')
all_auth_details = collection.find({})
################################################
current_trigger_service = 'twitter'
applet_folder_name = 'applets_'+current_trigger_service+'_1'
################################################
################ create new collection from old
# for oll in ollection.find({}):
#     collection.insert_one(oll)
#######################
############# reset scarped details ##########
# for x in collection.find({}):#({'service_idnetifier': 'gmail'}):
#     try:
#         collection.find_one_and_update({'service_idnetifier': x['service_idnetifier']}, {
#             "$set": {'scraped_hash': {'0': [], '1': [], '2': []},
#                      'scraped_urls': [],
#                      'scraped_urls_dic': {'0': [], '1': [], '2': []},
#                      'scraped_hash_url_map': {},
#                      'login_result': ''
#                      }
#         }, upsert=True)  # upsert true will create a new document if not exist
#     except KeyError:
#         collection.delete_one(x)
########################################################################################################################
########################################################################################################################
options = Options()
#options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
#serv = Service(r'/root/Tools/Firefox/geckodriver')
#browser = webdriver.Firefox(capabilities=cap, service=serv, options=options)
########################################################################################################################
########################################################################################################################
# chrome_options = ChromeOptions()
# chrome_options.add_argument('--headless')
# #chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
#browser = webdriver.Firefox(capabilities=cap, service=serv, options=options)
########################################################################################################################
########################################################################################################################
pageHashdict = {}
urlencounter = {}

def getClusterDetails(htmlfiles):
    # find if each URL has crawled 5 times
    clusterbynamedict = {}
    crawledTotalForEachCount = {}# stores crawled no as key
    for htmlf in htmlfiles:
        basename = htmlf.split('_')[0]
        if basename in clusterbynamedict.keys():
            clusterbynamedict[basename].append(htmlf)
        else:
            clusterbynamedict[basename] = [htmlf]
        ###############capture the total of each count number####################
        crawlNo = htmlf.split('_')[1].replace('.html', '')
        crawlN = int(crawlNo)
        if crawlN in crawledTotalForEachCount:
            crawledTotalForEachCount[crawlN] = crawledTotalForEachCount[crawlN] + 1
        else:
            crawledTotalForEachCount[crawlN] = 1 ## so we can assure 4 th run occured successfuly
    return clusterbynamedict, crawledTotalForEachCount
def authentication_failed(response):
    pass

class LoginSpider(CrawlSpider):

    def __init__(self, *args, **kwargs):
        print('init')
        print(kwargs.get('round'))
        self.round = kwargs.get('round')
        self.statusstring = kwargs.get('statusstring')
        self.sfoldername = kwargs.get('sfoldername')
        self.needmoretime = kwargs.get('needmoretime')
        self.browser = webdriver.Firefox(capabilities=cap, service=Service(r'/root/Tools/Firefox/geckodriver'),options=options)
        self.browser.set_window_size(1000, 2000)
        self.authObj = kwargs.get('aobj')
        self.service_name = self.authObj['service_idnetifier']
        self.domain = self.authObj['domains']
        self.loginurl = self.authObj['loginurl']
        self.afterloginurl = self.authObj['afterloginurl']
        self.authcookies = self.authObj['cookies']
        credentials = []
        credentials.append(self.authObj['username'])
        credentials.append(self.authObj['password'])
        self.data_list = credentials
        print(self.domain)
        print(self.loginurl)
        print(self.service_name)
        print(self.data_list)
        self.scraped_urls =[]
        self.loginTimes = []
        self.strip_domain_list = [item.strip() for item in self.domain.split(',')]
        print(self.strip_domain_list)
        self.name = self.service_name
        self.start_urls = [self.loginurl]
        self.rules = (
            Rule(LinkExtractor(allow_domains=self.strip_domain_list)), Rule(callback='parse_item')
        )
        self.lua_script = """function main(splash)   
            splash:go(splash.args.url)
            splash.wait(3)
            return {html=splash:html()}        
        end"""
        # this should be the last line #################################################################################
        super(LoginSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        print('parse')
        #self.browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
        ### if no_login, then scrape without login #####################################################################
        if self.authObj['username'] == 'no_login':
            print('No Need to login...')
            self.browser.get(self.loginurl)
            print(self.browser.current_url)
            self.writeToFile(self.browser.loginurl, self.browser.page_source)
            yield SplashRequest(url=self.loginurl, callback=self.after_no_login, endpoint='render.html')
        # elif self.authcookies != '':
        #     ### check if cookies set at authdetails ####################################################################
        #     print(self.authcookies)
        #     print('have cookies...')
        #     # for cookie in self.authcookies:
        #     #     print(cookie)
        #     #     self.browser.add_cookie({k: cookie[k] for k in ('name','value','domain','path','expiry')})
        #     #.browser.get(self.afterloginurl)
        #     # self.writeToFile(self.afterloginurl, self.browser.page_source)
        #     yield SplashRequest(url=self.afterloginurl, callback=self.after_login_with_cookies, endpoint='render.html',cookies=self.authcookies,args={'lua_source':self.lua_script,'wai':3})#,args={'wait:0.1'} endpoint='render.html'
        else:
            print('Need to login...')
            has_credentials = True
            for data in self.data_list:
                if not data.strip():
                    has_credentials = False
            if has_credentials:
                startLoging = timeit.default_timer()

                ####################### open login page ##
                # load the login page
                self.browser.get(self.loginurl)
                time.sleep(20) # WAIT UNTIL THE PAGE IS LOADED
                # call authentication method
                login_type, self.browser = authentication(self.browser, self.data_list, self.loginurl,1)
                if self.needmoretime:
                    time.sleep(160)  # for service with CAPTCHA
                else:
                    time.sleep(20)  # for services with NO CAPTCHA

                print(login_type)
                # save login cookies and logged in url to authdetails collection #######################################
                if self.browser.current_url != self.loginurl:
                    self.writeToFile(self.browser.current_url, self.browser.page_source)
                    endLogin = timeit.default_timer()
                    loginTime = endLogin - startLoging
                    self.loginTimes.append(loginTime)
                    collection.update({'_id': self.authObj['_id']}, {
                        '$set': {'cookies': self.browser.get_cookies(), 'afterloginurl': self.browser.current_url,
                                 'login_time': loginTime}})
                    # #################################
                    # yield SplashRequest(url=self.browser.current_url, callback=self.after_login,
                    #                     endpoint='render.html',
                    #                     cookies=self.browser.get_cookies())
                else:
                    print('problem in login')
                    print(self.loginurl)
                    collection.update({'_id': self.authObj['_id']}, {
                        '$set': {'login_result': 'problem'}})
                    self.browser.quit()
            else:
                print('no credentials')
        ### update cookies at authdetails collection ###################################################################

    def writeToFile(self,url,htmltext):
        print('writeToFile()')
        self.scraped_urls.append(url)
        #print(htmltext)
        # check and update url encounter
        if url in urlencounter.keys():
            for k, v in urlencounter.items():
                if k is url:
                    urlencounter[k]=urlencounter[k] + 1
        else:
            urlencounter[url] = 1

        foldername = 'evalscraped_'+self.name
        # encode url
        encodedurl = url.encode('utf-8')
        hashurl = hashlib.md5(encodedurl)
        pageHashdict[hashurl] = url
        if urlencounter[url] == 1:
            for record in collection.find({'service_idnetifier': self.service_name}):
                scrapedhash = record['scraped_hash']
                scraped_urls_dic = record['scraped_urls_dic']

                scrapedhash[str(self.round)].append(hashurl.hexdigest())
                scrapedhash[str(self.round)] = list(set(scrapedhash[str(self.round)]))
                scraped_urls_dic[str(self.round)].append(url)
                scraped_urls_dic[str(self.round)] = list(set(scraped_urls_dic[str(self.round)]))

                try:
                    collection.update({'service_idnetifier': self.service_name}, {"$set": {'scraped_hash': scrapedhash, 'scraped_urls_dic': scraped_urls_dic}}, upsert=True)  # upsert true will create a new document if not exist
                    # for record2 in collection.find({'service_idnetifier': self.service_name}):
                    #     print('test 1 ')
                    #     scrapedhash = record2['scraped_hash']
                    #     scraped_urls_dic = record2['scraped_urls_dic']
                    #     print(scrapedhash)
                    #     print(scraped_urls_dic)
                except Exception as ex:
                    print('exception at update db')
                    ################### check exception details ####################################################
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)
                    print('exception caught')
        ##############################################
        # create folder
        if not os.path.exists(str(self.sfoldername)):
            os.makedirs(str(self.sfoldername))
            print(str(self.sfoldername))
        # create folder
        if not os.path.exists(str(self.sfoldername)+"/"+foldername):
            os.makedirs(str(self.sfoldername)+"/"+foldername)
        # create folder
        if not os.path.exists(str(self.sfoldername)+"/metadata"):
            os.makedirs(str(self.sfoldername)+"/metadata")
        # create folder
        if not os.path.exists(str(self.sfoldername)+"/screens"):
            os.makedirs(str(self.sfoldername)+"/screens")
        # create folder
        if not os.path.exists(str(self.sfoldername)+"/screens/"+foldername):
            os.makedirs(str(self.sfoldername)+"/screens/"+foldername)
        ##############################################
        # create file and page content
        basefilename = str(self.sfoldername)+"/"+foldername+"/"+str(hashurl.hexdigest()) +"_" + str(self.round)
        print(basefilename)
        if urlencounter[url] == 1:
            try:
                f = open(basefilename+ ".html")
                f.close()
            except IOError:
                f = open(basefilename+ ".html", "w+")
                f.write(htmltext)
                f.close()
        ############################################### save a screen shot ##############
        screenbasefilename = str(self.sfoldername)+"/screens/" + foldername + "/" + str(hashurl.hexdigest()) + "_" + str(self.round)
        if urlencounter[url] == 1:
            ################################# to save the current url #######
            self.browser.get(url)
            time.sleep(5)
            #################################################################
            self.browser.save_screenshot(screenbasefilename+ '.png')
            time.sleep(2)
        ###############################################
        # create and write meta data
        matabasefilename = str(self.sfoldername)+"/metadata"+"/"+str(self.name)
        if urlencounter[url] == 1:
            try:
                f = open(matabasefilename+ ".txt", "a+")
                f.write(hashurl.hexdigest() + " = "+url + "\n")
                f.close()
            except IOError:
                f = open(matabasefilename+ ".txt", "a+")
                f.write(hashurl.hexdigest() + " = "+url+ "\n")
                f.close()

    def parse_item(self, response):
        print('parse_item()')
        self.writeToFile(response.url, response.text)

    def after_no_login(self, response):
        print('############')
        print("No Login success")
        print(response.url)
        self.writeToFile(response.url, response.text)
        le = LxmlLinkExtractor(allow_domains=self.strip_domain_list)
        print(le.extract_links(response))
        for link in le.extract_links(response):
            yield SplashRequest(url=link.url, callback=self.parse_item, endpoint='render.html')

    def after_login_with_cookies(self, response):
        print('############')
        print("Login cookies success")
        print(response.url)
        self.writeToFile(response.url, response.text)
        le = LxmlLinkExtractor(allow_domains=self.strip_domain_list)
        print(le.extract_links(response))
        for link in le.extract_links(response):
            # yield SplashRequest(url=link.url, callback=self.parse_item, endpoint='render.html',
            #               cookies=self.authcookies, args={'lua_source': self.lua_script, 'wai': 3})
            yield SplashRequest(url=link.url, callback=self.parse_item, endpoint='render.html',
                                cookies=self.authcookies)#,args={'wait:0.1'}

    def after_login(self, response):
        print('############')

        if authentication_failed(response):
            self.logger.error("Login failed")
        else:
            print("Login success")
            print(response.url)
            self.writeToFile(response.url, response.text)
            le = LxmlLinkExtractor(allow_domains= self.strip_domain_list)
            print(le.extract_links(response))
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_item, endpoint='render.html',cookies=self.browser.get_cookies())

    def closed( self, reason ):
        print('closing crawler')
        avgeLoginTime = sum(self.loginTimes)/len(self.loginTimes)
        collection.update({'_id': self.authObj['_id']}, {'$set': {str(self.statusstring)+'_monit_scraped_urls': self.scraped_urls,str(self.statusstring)+'_monit_avg_login_time':avgeLoginTime, str(self.statusstring)+'_monit_all_login_time':self.loginTimes}})
        self.browser.quit()


# the wrapper to make it run more times
def run_spider(spider, x, authObject,statusstring,sfoldername,needmoretime):
    def f(q):
        try:
            runner = CrawlerRunner()
            print('hii')
            deferred = runner.crawl(spider, aobj = authObject,round=x,statusstring=statusstring,sfoldername=sfoldername,needmoretime=needmoretime)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
            print('done crawling')
            #return
            # reactor.stop()
            # print('reactor stop')
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

def check(serviceID,sfoldername):
    clusterbynamedict = {}
    crawledTotalForEachCount = {}
    foldername = str(sfoldername)+'/scraped_' + serviceID
    baseFolderName = './' + foldername + '/'
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
        return clusterbynamedict, crawledTotalForEachCount
    except OSError:
        return clusterbynamedict, crawledTotalForEachCount

def crawl(num, count,serviceID,authObject,statusstring,sfoldername,needmoretime):
    count = count - 1
    print(str(num) + ' run:')

    run_spider(LoginSpider, num, authObject,statusstring,sfoldername,needmoretime)
    clusterbynamedict, crawledTotalForEachCount = check(serviceID,sfoldername)
    if (len(crawledTotalForEachCount) < (num + 1)):
        time.sleep(15)
        if count > 0:
            crawl(num, count, serviceID,authObject,statusstring,sfoldername,needmoretime)
    elif len(crawledTotalForEachCount) == (num + 1):
        return True
    return False

#################################### Read Database and for each service login and scrape ###############################

scrappedDetails = {}
threads = []
s1 = timeit.default_timer()
i = 0
###################################################################
###################### SELECT from HERE
#statusstring = 'before'
#statusstring = 'after'
# if  statusstring == 'before':
#     default_start_no = 0
#     default_end_no = 1
#
# elif statusstring == 'after':
#     default_start_no = 1
#     default_end_no = 2
####################################################################
def getaction_servicelist(beforeorafter):
    selected_services_require_scraping = ['bitly', 'facebook', 'google_contacts', 'instapaper', 'slack', 'twitter',
                                          'youtube', 'wordpress', 'withings', 'weebly',
                                          'toodledo', 'todoist', 'tesco', 'strava', 'medium', 'musixmatch', 'pocket',
                                          'reddit', 'google_docs', 'google_drive',
                                          'google_sheets', 'instagram', 'fitbit', 'flickr', 'gmail', 'google_calendar',
                                          'blogger', 'dropbox', 'diigo', 'evernote']
    ######################################
    if beforeorafter == 'before':
        default_start_no = 0
        default_end_no = 1
        statusstring = beforeorafter
        successactionservicelist = []
        for service_identifier in selected_services_require_scraping:
            foldername = 'scraped_monitoring/evalscraped_' + service_identifier  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
            baseFolderName = './' + foldername + '/'
            BASE_FOLDERNAME = baseFolderName
            print(BASE_FOLDERNAME)
            try:
                htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
                print(htmlfiles)
                for htmlf in htmlfiles:
                    page_split = htmlf.split('_')
                    if page_split[1] == '0.html':
                        print(htmlf)

                if not htmlfiles:
                    successactionservicelist.append(service_identifier)

            except OSError as ex:
                print(ex)
                pass
        return successactionservicelist, default_start_no, default_end_no,statusstring

    #######################################
    if beforeorafter == 'after':
        default_start_no = 1
        default_end_no = 2
        statusstring = beforeorafter
        db3 = client['evalapplets']
        scollect3 = db3.get_collection(applet_folder_name)
        db2 = client[applet_folder_name]
        scollect = db2.get_collection('succeed')
        successappletlist = []
        for sc in scollect.find({}):
            successappletlist.append(sc['applet_id'])
        successactionservicelist = []
        for sc3 in scollect3.find({}):
            if sc3['applet_id'] in successappletlist:
                successactionservicelist.append(sc3['action_service'])

        return successactionservicelist, default_start_no,default_end_no,statusstring
# facebook ->
# #20['bitly''blogger', 'wordpress', 'diigo', 'instapaper', 'pocket', 'dropbox', 'google_docs', 'google_drive', 'google_sheets', 'evernote', 'flickr', 'twitter', 'google_contacts', 'fitbit', 'reddit', 'slack', 'google_calendar', 'line', 'todoist']
# # voip_calls, line, twitter, toodledo, reddit, slack (bee channel), android_device(wallpaper)
# instagram ->
# 22 ['blogger', 'wordpress', 'diigo', 'instapaper', 'pocket', 'google_calendar', 'dropbox', 'google_docs', 'google_drive', 'google_sheets', 'line', 'strava', 'android_device', 'ios_health', 'ios_reading_list', 'evernote', 'android_messages', 'if_notifications', 'voip_calls', 'flickr', 'ios_photos', 'todoist']
# android_photos ->
# 25 ['ios_photos', 'android_device', 'if_notifications', 'voip_calls', 'instapaper', 'toodledo', 'reddit', 'google_docs', 'flickr', 'fitbit', 'ios_health', 'blogger', 'slack', 'google_drive', 'ios_reading_list', 'twitter', 'google_sheets', 'ios_reminders', 'wordpress', 'pocket', 'dropbox', 'line', 'todoist', 'diigo', 'android_messages']
# failed: musixmatch, tesco, google_contacts
# twitter ->
# 28 ['blogger', 'wordpress', 'bitly', 'diigo', 'instapaper', 'pocket', 'google_calendar', 'dropbox', 'google_docs', 'google_drive', 'google_sheets', 'line', 'slack', 'fitbit', 'strava', 'android_device', 'ios_health', 'ios_reading_list', 'ios_reminders', 'evernote', 'android_messages', 'if_notifications', 'voip_calls', 'flickr', 'ios_photos', 'reddit', 'todoist', 'toodledo']
#
###################################################################################################################
###################################################################################################################
###################################################################################################################
###########################################INIT PARAMETERS################################################
before = 'before'
after = 'after'
successactionservicelist, default_start_no,default_end_no,statusstring = getaction_servicelist(after)
print(successactionservicelist)
print(len(successactionservicelist))
###################################################################################################################
###################################################################################################################
###################################################################################################################
all_current_action_servicess = ['bitly','facebook','google_contacts','instapaper','slack','twitter','youtube','wordpress','withings','weebly',
               'toodledo','todoist','tesco','strava','medium','musixmatch','pocket','reddit','google_docs','google_drive',
               'google_sheets','instagram','fitbit','flickr','gmail','google_calendar','blogger','dropbox','diigo','evernote',
                'ios_health', 'if_notifications','android_device', 'location','do_button', 'android_phone','android_messages', 'voip_calls','line', 'do_camera',
                'ios_photos', 'ios_reading_list','foursquare', 'android_battery','android_photos', 'qualitytime','ios_reminders', 'ios_contacts','do_note']
moretimeneed = ['dropbox', 'reddit', 'evernote']
###################################################################################################################
greenlist =['withings','fitbit','strava','google_drive','flickr','blogger','adafruit','instapaper','slack','reddit','tado_heating','rachio_iro','facebook','yeelight','square','google_docs','google_contacts','toodledo','email','gmail','spotify','tesco']
greencaptchalist = ['bitly','weebly','twitter','google_sheets','google_calendar','instagram','dropbox','wordpress','irobot','netatmo','ring','wemo_light_switch','youtube','pocket','todoist','mailchimp','netatmo_thermostat','diigo','musixmatch','evernote','medium']
yellolist = ['ios_health','if_notifications','android_device','google_assistant','location','amazon_alexa','do_button','android_phone','android_messages','voip_calls','line','mesh','do_camera','ios_photos','ios_reading_list','foursquare','uber','arlo','android_wear','android_battery','android_photos','wemo_switch','qualitytime','ios_reminders','ios_contacts','wemo_insight_switch','lametric','lifx','do_note']
bluelist= ['optus_smart_living','feed','nytimes','space','ifttt','hacker_news','app_store','pew_research','time','who','bea','brainyquote','usda','grants','npr','wikipedia','weather','finance','foxnews','nsf','propublica','giphy','sec','epa','loc','dos','songkick']

# click google option: bitly, soundcloud, evernote, medium
no_manula_effort_list = ['withings','fitbit','strava','google_drive','flickr','blogger', 'instapaper','google_docs','google_contacts','google_calendar','google_sheets','email','gmail','todoist','pocket','medium''youtube','toodledo','weebly']
manual_effort_list = ['twitter','bitly', 'dropbox','reddit', 'diigo', 'musixmatch', 'wordpress', 'evernote','instagram', 'slack', 'faebook', 'tesco']
####################################################################################################################
for service in ['flickr']:#list(set(executed_services + fromscript)): # successactionservicelist//////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!! 'withings', 'instagram',
    #continue
    if service in yellolist:
        continue
    if service in no_manula_effort_list:
        continue
    ###########################
    if service in moretimeneed:
        needmoretime = True
    else:
        needmoretime = False
    ########################
    average_time_to_scrape_with_login = ''
    time_to_scrape_with_login = 0
    all_time_values_with_Login = []
    average_time_to_scrape_without_login = ''
    time_to_scrape_without_login = 0
    all_time_values_without_Login = []
    serviceObjectID = ''
    for num in range(default_start_no, default_end_no):
        startWithLogin = timeit.default_timer()# including login
        for x in collection.find({'service_idnetifier': service}):  # {'service_idnetifier':'wordpress'}#toodledo
            # only the action services are scrapped
            serviceObjectID = x['_id']
            serviceID = x['service_idnetifier']
            credentials = []
            credentials.append(x['username'])
            credentials.append(x['password'])
            # #######################################################################################################
            sfoldername = 'scraped_monitoring'
            print(serviceID)

            # ##########################################################################################################
            # ##########################################################################################################
            scrapedhashdic = x['scraped_hash']
            scrapedurlsdic = x['scraped_urls_dic']
            print(scrapedhashdic)
            print(scrapedurlsdic)
            ########################################################################################################
            if True: # len(scrapedhashdic[str(num)]) == 0:
                successs = crawl(num, 1, serviceID, x,statusstring,sfoldername,needmoretime)
                if num == default_end_no:
                    stop = timeit.default_timer()
                    print('Time taken: ', stop - startWithLogin)
                    print(scrappedDetails)

            else:
                print('already in')
        ########################################################################################################
        stopWithLogin = timeit.default_timer()
        timeWithLogin = stopWithLogin -startWithLogin
        time_to_scrape_with_login = time_to_scrape_with_login + timeWithLogin
        all_time_values_with_Login.append(timeWithLogin)

    e1 = timeit.default_timer()
    print('Total Time = ' + str(e1 - s1))

    loginTime = 0
    time_to_scrape_without_login = 0
    try:
        for x in collection.find({'_id': serviceObjectID}):
            avgloginTime = x[str(statusstring)+'_monit_avg_login_time']
        for val in all_time_values_with_Login:
            all_time_values_without_Login.append(val - avgloginTime)
            time_to_scrape_without_login = time_to_scrape_without_login + (val - avgloginTime)
        # ###############
        average_time_to_scrape_with_login = time_to_scrape_with_login / len(all_time_values_with_Login)
        average_time_to_scrape_without_login = time_to_scrape_without_login / len(all_time_values_without_Login)
        collection.update({'_id': serviceObjectID},
                          {'$set': {  str(statusstring)+'_monitoring_with_Login_time': all_time_values_with_Login,
                                    str(statusstring)+'_monitoring_without_Login_time': all_time_values_without_Login}})
        print(average_time_to_scrape_with_login)
        print(average_time_to_scrape_without_login)
    except KeyError:
        print('key error')

########################################################################################################################
########################################################################################################################
script_ended = timeit.default_timer()
print('script Run Time = ' + str(script_ended - script_ended))
