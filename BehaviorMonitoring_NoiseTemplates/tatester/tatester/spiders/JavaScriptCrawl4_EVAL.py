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
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
#collection = db.get_collection('authdetails')
#collection = db.get_collection('evalauthdetails')# use a new collection for evaluation of 105 services
collection =  db.get_collection('newevalauthdetails')
all_auth_details = collection.find({})
############# reset scarped details ##########
# for x in collection.find({'service_idnetifier': 'youtube'}):
#     collection.find_one_and_update({'service_idnetifier': x['service_idnetifier']}, {
#         "$set": {'scraped_hash': {'0': [],'1': [], '2':[]},
#                  'scraped_urls': [],
#                  'scraped_urls_dic': {'0': [], '1': [], '2': []},
#                  'scraped_hash_url_map': {},
#                  'login_result': ''
#                  }
#     }, upsert=True)  # upsert true will create a new document if not exist

############## IF REQUIRE TO DELETE A DOCUMENT ##############################################################
# for x in collection.find({'service_idnetifier': 'medium'}):
#     print('deleting')
#     print(x['_id'])
#     print(type(x['_id']))
#     if x['_id'] == ObjectId("5e94c9344a9fd89cdb62b06d"):
#         print('deleted')
#         collection.delete_one(x)

#######################
# client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
# db = client.get_database('services')
# collection = db.get_collection('authdetails')
# all_auth_details = collection.find({})
# all_credentials_in_db = {}
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
        self.scraped_urls = []
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
        #     self.browser.get(self.after_login())
        #     time.sleep(1)
        #     try:
        #         for cookie in self.authcookies:
        #             print(cookie)
        #             #self.browser.add_cookie(cookie)
        #             self.browser.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path')})#, 'expiry'
        #     except Exception as ex:
        #         ################### check exception details ####################################################
        #         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #         message = template.format(type(ex).__name__, ex.args)
        #         print (message)
        #         print('exception caught')
        #
        #     #self.browser.get(self.afterloginurl)
        #     print(self.browser.current_url)
        #     self.writeToFile(self.current_url, self.browser.page_source)
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
                time.sleep(20) # for services with NO CAPTCHA
                #time.sleep(160)# for service with CAPTCHA
                print(login_type)
                # save login cookies and logged in url to authdetails collection #######################################
                if self.browser.current_url != self.loginurl:
                    print('logged in ')
                    self.writeToFile(self.browser.current_url, self.browser.page_source)
                    endLogin = timeit.default_timer()
                    loginTime = endLogin - startLoging
                    self.loginTimes.append(loginTime)
                    collection.update({'_id': self.authObj['_id']}, {
                        '$set': {'cookies': self.browser.get_cookies(), 'afterloginurl': self.browser.current_url,
                                 'login_time': loginTime}})
                    # ################################# commented for cutting the crawled content
                    # yield SplashRequest(url=self.browser.current_url, callback=self.after_login,
                    #                     endpoint='render.html',
                    #                     cookies=self.browser.get_cookies())
                    ##############################################################################
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
        print('came here 0')
        ################################## update database #############################
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


        ################################################################################
        print('came here 2')
        # create folder
        if not os.path.exists("evalscraped"):
            os.makedirs("evalscraped")
        # create folder
        if not os.path.exists("evalscraped/"+foldername):
            os.makedirs("evalscraped/"+foldername)
        # create folder
        if not os.path.exists("evalscraped/metadata"):
            os.makedirs("evalscraped/metadata")
        # create folder
        if not os.path.exists("evalscraped/screens"):
            os.makedirs("evalscraped/screens")
        # create folder
        if not os.path.exists("evalscraped/screens/"+foldername):
            os.makedirs("evalscraped/screens/"+foldername)
        #################################################################################
        # create file and page content
        basefilename = "evalscraped/"+foldername+"/"+str(hashurl.hexdigest()) +"_" + str(self.round)
        print('came here 3')
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
        screenbasefilename = "evalscraped/screens/" + foldername + "/" + str(hashurl.hexdigest()) + "_" + str(self.round)
        if urlencounter[url] == 1:
            print('came here 4')
            ################################# to save the current url #######
            self.browser.get(url)
            time.sleep(5)
            #################################################################
            print('came here 5')
            self.browser.save_screenshot(screenbasefilename+ '.png')
            time.sleep(2)
        #################################################################################
        # create and write meta data
        matabasefilename = "evalscraped/metadata"+"/"+str(self.name)
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
        collection.update({'_id': self.authObj['_id']}, {'$set': {'scraped_urls': self.scraped_urls,'avg_login_time':avgeLoginTime, 'all_login_time':self.loginTimes}})
        self.browser.quit()


# the wrapper to make it run more times
def run_spider(spider, x, authObject):
    print('run spider started')
    def f(q):
        try:
            runner = CrawlerRunner()
            print('create runner...')
            deferred = runner.crawl(spider, aobj = authObject,round=x)
            print('runner.crawler call')
            deferred.addBoth(lambda _: reactor.stop())
            print('start run')
            reactor.run()
            q.put(None)
            print('done crawling')
            #return
            ## was commented
            # reactor.stop()
            # print('reactor stop')
            ################
        except Exception as e:
            print('exception ....')
            q.put(e)
            ################## check exception details ####################################################
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            print('exception caught')

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

def check(serviceID):
    clusterbynamedict = {}
    crawledTotalForEachCount = {}
    foldername = 'evalscraped/scraped_' + serviceID
    baseFolderName = './' + foldername + '/'
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
        return clusterbynamedict, crawledTotalForEachCount
    except OSError:
        return clusterbynamedict, crawledTotalForEachCount

def crawl(num, count,serviceID,authObject):
    count = count - 1
    print(str(num) + ' run:')

    run_spider(LoginSpider, num, authObject)
    # clusterbynamedict, crawledTotalForEachCount = check(serviceID)
    # if (len(crawledTotalForEachCount) < (num + 1)):
    #     time.sleep(15)
    #     if count > 0:
    #         crawl(num, count, serviceID,authObject)
    # if len(crawledTotalForEachCount) == (num + 1):
    #     return True
    return False

#################################### Read Database and for each service login and scrape ###############################

scrappedDetails = {}
threads = []
s1 = timeit.default_timer()
i = 0


servicelist = ['withings', 'fitbit', 'strava', 'ios_health', 'google_sheets', 'if_notifications', 'google_calendar', 'instagram', 'twitter', 'google_drive', 'dropbox', 'wordpress', 'flickr', 'blogger', 'onedrive', 'android_device', 'adafruit', 'location', 'do_button', 'android_phone', 'android_messages', 'voip_calls', 'optus_smart_living', 'feed', 'instapaper', 'pocket', 'nytimes', 'date_and_time', 'slack', 'space', 'do_camera', 'ifttt', 'todoist', 'hacker_news', 'app_store', 'reddit', 'ios_photos', 'pew_research', 'time', 'who', 'bea', 'ios_reading_list', 'rachio_iro', 'facebook', 'foursquare', 'android_wear', 'android_battery', 'android_photos', 'soundcloud', 'weebly', 'maker_webhooks', 'brainyquote', 'qualitytime', 'square', 'usda', 'grants', 'npr', 'wikipedia', 'ios_reminders', 'ios_contacts', 'google_docs', 'google_contacts', 'weather', 'toodledo', 'finance', 'foxnews', 'nsf', 'propublica', 'giphy', 'diigo', 'musixmatch', 'evernote', 'email', 'gmail', 'spotify', 'sec', 'do_note', 'medium', 'epa', 'loc', 'onenote', 'tesco', 'dos', 'songkick']
#servicelist = ['withings']
captchmaybe  =['instagram', 'dropbox', 'amazon_alexa', 'ring', 'bitly', 'line', 'uber', 'mailchimp', 'evernote', 'gmail', 'spotify', 'medium', 'onenote']


credentialservicelist = ['withings', 'fitbit', 'strava', 'google_sheets', 'google_calendar', 'instagram', 'twitter', 'google_drive', 'dropbox', 'wordpress', 'blogger',
                         'adafruit', 'amazon_alexa', 'irobot', 'netatmo', 'ring', 'bitly', 'youtube', 'instapaper', 'pocket', 'line', 'mesh', 'slack', 'todoist', 'reddit', 'tado_heating',
                         'facebook', 'foursquare', 'arlo',  'qualitytime', 'google_docs', 'google_contacts', 'toodledo', 'mailchimp',  'netatmo_thermostat', 'diigo',
                         'musixmatch', 'lametric', 'evernote', 'gmail', 'lifx', 'spotify', 'onenote', 'tesco']#'soundcloud', 'onedrive','tplink_router',
homepagenotenough = ['facebook', 'instapaper','reddit','adafruit']
popupservicelist = ['todoist','netatmo_thermostat','netatmo']
mobileapp = ['mesh', 'arlo', 'amazon_alexa', 'lametric', 'lifx']
loginurlmissing = ['qualitytime', 'onenote', 'tesco', 'foursquare']
newcaptch = ['pocket']
problemloginlist = ['onedrive','soundcloud']
omit = captchmaybe + newcaptch+ homepagenotenough + popupservicelist + mobileapp + loginurlmissing + problemloginlist
credentialservicelist = list(set(credentialservicelist))
for ss in credentialservicelist :
    if ss in omit:
        credentialservicelist.remove(ss)
###################################################################################################################
greenlist =['withings','fitbit','strava','twitter','google_drive','flickr','blogger','adafruit','bitly','instapaper','slack','reddit','tado_heating','rachio_iro','facebook','yeelight','weebly','square','google_docs','google_contacts','toodledo','email','gmail','spotify','tesco']
greencaptchalist = ['google_sheets','google_calendar','instagram','dropbox','wordpress','irobot','netatmo','ring','wemo_light_switch','youtube','pocket','todoist','mailchimp','netatmo_thermostat','diigo','musixmatch','evernote','medium']
yellolist = ['ios_health','if_notifications','android_device','google_assistant','location','amazon_alexa','do_button','android_phone','android_messages','voip_calls','line','mesh','do_camera','ios_photos','ios_reading_list','foursquare','uber','arlo','android_wear','android_battery','android_photos','wemo_switch','qualitytime','ios_reminders','ios_contacts','wemo_insight_switch','lametric','lifx','do_note']
bluelist= ['optus_smart_living','feed','nytimes','space','ifttt','hacker_news','app_store','pew_research','time','who','bea','brainyquote','usda','grants','npr','wikipedia','weather','finance','foxnews','nsf','propublica','giphy','sec','epa','loc','dos','songkick']
###################################################################################################################
nologin = []
problmeinlogin = []
mobileapplist = []
nologinurl = []
print(len(credentialservicelist))
print(credentialservicelist)
####################################################################################################################
for service in ['youtube']:#foursquare,
    #continue
    if service in ['onedrive','soundcloud']:
        continue
    average_time_to_scrape_with_login = ''
    time_to_scrape_with_login = 0
    all_time_values_with_Login = []
    average_time_to_scrape_without_login = ''
    time_to_scrape_without_login = 0
    all_time_values_without_Login = []
    serviceObjectID = ''
    NOOFROUNDS = 2 # set the no of rounds of scraping for each service
    #pools = ThreadPool(processes=NOOFROUNDS)
    for num in range(NOOFROUNDS):
        startWithLogin = timeit.default_timer()# including login
        nologinF = False
        for x in collection.find({'service_idnetifier': service}):
            serviceObjectID = x['_id']
            print(serviceObjectID)
            serviceID = x['service_idnetifier']
            print(serviceID)
            # try:
            #     if x['login_result'] == 'problem':
            #         problmeinlogin.append(serviceID)
            #         print('login_result:')
            #         print(list(set(problemloginlist)))
            #         continue
            # except KeyError:
            #     pass
            try:
                if x['loginurl'] == 'mobileapp':
                    mobileapplist.append(serviceID)
                    print('mobileapp:')
                    print(list(set(mobileapplist)))
                    continue
            except KeyError:
                continue

            try:
                if x['loginurl'].strip() == '':
                    nologinurl.append(serviceID)
                    print('loginurl:')
                    print(list(set(nologinurl)))
                    continue
            except KeyError:
                continue

            ############################################# GET CREDENTIALS FOR LOGIN#####################################
            credentials = []
            try:
                if x['username'].strip() == 'no_login':
                    nologin.append(service)
                    nologinF = True
                elif x['username'].strip() != '':
                    credentials.append(x['username'])
                else:
                    x['username'] = 'no_login'
                    credentials.append(x['username'])
                    nologin.append(service)
                    nologinF = True
            except KeyError:
                nologinF = True
                pass
            print(nologinF)
            if nologinF:
                continue

            try:
                if x['password'] != '':
                    credentials.append(x['password'])
            except KeyError:
                pass
            # ##########################################################################################################
            # ##########################################################################################################
            ########
            scrapedhashdic = x['scraped_hash']
            scrapedurlsdic = x['scraped_urls_dic']
            print(scrapedhashdic)
            print(scrapedurlsdic)
            ########################################################################################################
            if len(scrapedhashdic[str(num)]) == 0:
                successs = crawl(num, 1, serviceID, x)
                if num == (NOOFROUNDS - 1):
                    stop = timeit.default_timer()
                    print('Time taken: ', stop - startWithLogin)
                    print(scrappedDetails)

            else:
                print('already in')


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
            avgloginTime = x['avg_login_time']
        for val in all_time_values_with_Login:
            all_time_values_without_Login.append(val - avgloginTime)
            time_to_scrape_without_login = time_to_scrape_without_login + (val - avgloginTime)
        # ###############
        average_time_to_scrape_with_login = time_to_scrape_with_login / len(all_time_values_with_Login)
        average_time_to_scrape_without_login = time_to_scrape_without_login / len(all_time_values_without_Login)
        collection.update({'_id': serviceObjectID},
                          {'$set': {'average_time_to_scrape_with_login': average_time_to_scrape_with_login,
                                    'average_time_to_scrape_without_login': average_time_to_scrape_without_login,
                                    'all_time_values_with_Login': all_time_values_with_Login,
                                    'all_time_values_without_Login': all_time_values_without_Login}})
        print(average_time_to_scrape_with_login)
        print(average_time_to_scrape_without_login)
    except KeyError:
        print('key error')

# pocket: 17.177752407005755
# email: 10.518108017000486
