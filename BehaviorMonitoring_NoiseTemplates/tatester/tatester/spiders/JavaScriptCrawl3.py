import scrapy
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
from Taifu.BehaviorMonitoring_NoiseTemplates.tatester.tatester.spiders.ActionClientAuthentication import authentication
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
collection = db.get_collection('authdetails')
all_auth_details = collection.find({})
#######################
# client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
# db = client.get_database('services')
# collection = db.get_collection('authdetails')
# all_auth_details = collection.find({})
# all_credentials_in_db = {}
########################################################################################################################
########################################################################################################################
options = Options()
options.add_argument('--headless')
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
        self.browser = kwargs.get('brow')
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
            # print('Need to login...')
            # has_credentials = True
            # for data in self.data_list:
            #     if not data.strip():
            #         has_credentials = False
            # if self.round == 0:
            #     if has_credentials:
            #         # load the login page
            #         self.browser.get(self.loginurl)
            #         print(self.browser.current_url)
            #         # call authentication method
            #         login_type, self.browser = authentication(self.browser, self.data_list, self.loginurl)
            #         # save login cookies and logged in url to authdetails collection #######################################
            #         if self.browser.current_url != self.loginurl:
            #             self.writeToFile(self.browser.current_url, self.browser.page_source)
            #             collection.update({'_id': self.authObj['_id']}, {
            #                 '$set': {'cookies': self.browser.get_cookies(), 'afterloginurl': self.browser.current_url}})
            #             yield SplashRequest(url=self.browser.current_url, callback=self.after_login,
            #                                 endpoint='render.html',
            #                                 cookies=self.browser.get_cookies())
            #         else:
            #             print('problem in login')
            #             print(self.loginurl)
            #             collection.update({'_id': self.authObj['_id']}, {
            #                 '$set': {'login_result': 'problem'}})
            #     else:
            #         print('no credentials')
            # else:
                yield SplashRequest(url=self.browser.current_url, callback=self.after_login_with_cookies, endpoint='render.html',cookies=self.browser.get_cookies())


        ### update cookies at authdetails collection ###################################################################

    def writeToFile(self,url,htmltext):
        print('writeToFile()')
        #print(htmltext)
        # check and update url encounter
        if url in urlencounter.keys():
            for k, v in urlencounter.items():
                if k is url:
                    urlencounter[k]=urlencounter[k] + 1
        else:
            urlencounter[url] = 1

        foldername = 'scraped_'+self.name
        # encode url
        encodedurl = url.encode('utf-8')
        hashurl = hashlib.md5(encodedurl)
        pageHashdict[hashurl] = url
        ##############################################
        # create folder
        if not os.path.exists("scraped"):
            os.makedirs("scraped")
        # create folder
        if not os.path.exists("scraped/"+foldername):
            os.makedirs("scraped/"+foldername)
        # create folder
        if not os.path.exists("scraped/metadata"):
            os.makedirs("scraped/metadata")
        ##############################################
        # create file and page content
        basefilename = "scraped/"+foldername+"/"+str(hashurl.hexdigest()) +"_" + str(self.round)
        print(basefilename)
        if urlencounter[url] == 1:
            try:
                f = open(basefilename+ ".html")
                f.close()
            except IOError:
                f = open(basefilename+ ".html", "w+")
                f.write(htmltext)
                f.close()
        ###############################################
        # create and write meta data
        matabasefilename = "scraped/metadata"+"/"+str(self.name)
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

    def spider_closed(self, CrawlSpider):
        self.browser.quit()



# the wrapper to make it run more times
def run_spider(spider, x, y,authObject):
    def f(q):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider, aobj = authObject,round=x, brow = y)
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

def check(serviceID):
    clusterbynamedict = {}
    crawledTotalForEachCount = {}
    foldername = 'scraped/scraped_' + serviceID
    baseFolderName = './' + foldername + '/'
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
        return clusterbynamedict, crawledTotalForEachCount
    except OSError:
        return clusterbynamedict, crawledTotalForEachCount

def crawl(num, count,serviceID,authObject,browser):
    count = count - 1
    print(str(num) + ' run:')

    run_spider(LoginSpider, num, browser,authObject)
    clusterbynamedict, crawledTotalForEachCount = check(serviceID)
    if (len(crawledTotalForEachCount) < (num + 1)):
        time.sleep(15)
        if count > 0:
            crawl(num, count, serviceID,authObject)
    elif len(crawledTotalForEachCount) == (num + 1):
        return True
    return False

#################################### Read Database and for each service login and scrape ###############################
browser_list = []
# ########################################################################################################################
# for service in servicelist:
#     if service != 'spotify':
#         continue
#     for x in collection.find({'service_idnetifier': 'spotify'}):
#         credentials = []
#         credentials.append(x['username'])
#         credentials.append(x['password'])
#         pools = ThreadPool(processes=5)
#         serv1 = Service(r'/root/Tools/Firefox/geckodriver')
#         browser1 = webdriver.Firefox(capabilities=cap, service=serv1, options=options)
#         browser10 = pools.apply_async(authentication, (browser1, credentials, x['loginurl'])).get()[1]
#         print(browser10)
#         browser_list.append(browser10)
#         serv2 = Service(r'/root/Tools/Firefox/geckodriver')
#         browser2 = webdriver.Firefox(capabilities=cap, service=serv2, options=options)
#         browser20 = pools.apply_async(authentication, (browser2, credentials, x['loginurl'])).get()[1]
#         browser_list.append(browser20)
#         serv3 = Service(r'/root/Tools/Firefox/geckodriver')
#         browser3 = webdriver.Firefox(capabilities=cap, service=serv3, options=options)
#         browser30 = pools.apply_async(authentication, (browser3, credentials, x['loginurl'])).get()[1]
#         browser_list.append(browser30)
#         serv4 = Service(r'/root/Tools/Firefox/geckodriver')
#         browser4 = webdriver.Firefox(capabilities=cap, service=serv4, options=options)
#         browser40 = pools.apply_async(authentication, (browser4, credentials, x['loginurl'])).get()[1]
#         browser_list.append(browser40)
#         serv5 = Service(r'/root/Tools/Firefox/geckodriver')
#         browser5 = webdriver.Firefox(capabilities=cap, service=serv5, options=options)
#         browser50 = pools.apply_async(authentication, (browser5, credentials, x['loginurl'])).get()[1]
#         browser_list.append(browser50)
#
#
# e0 = timeit.default_timer()
# print(browser_list)
scrappedDetails = {}
threads = []
s1 = timeit.default_timer()
i = 0

servicelist = ['go', 'android_device', 'narro', 'diigo', 'google_docs', 'dropbox', 'wordpress', 'tumblr', 'office_365_calendar', 'pocket', 'bitly', 'google_calendar', 'amazonclouddrive', 'google_sheets', 'google_drive', 'cisco_spark', 'telegram', 'coqon', 'google_contacts', 'office_365_contacts', 'onedrive', 'particle', 'strava', 'email', 'maker_webhooks', 'github', 'fitbit', 'office_365_mail', 'deezer', 'musixmatch', 'ios_calendar', 'soundcloud', 'spotify', 'newsblur', 'ios_reminders', 'ios_photos', 'evernote', 'flickr', 'sms', 'stockimo', 'twitter', 'beeminder', 'toodledo', 'reddit', 'sina_weibo', 'todoist']
updateservicelist = [ 'narro', 'diigo', 'google_docs', 'dropbox', 'pocket', 'google_calendar', 'amazonclouddrive', 'google_sheets', 'google_drive', 'google_contacts', 'particle','github', 'fitbit','spotify', 'flickr', 'beeminder', 'toodledo', 'reddit', 'todoist']
newList = ['spotify']
####################################################################################################################
for service in newList:
    average_time_to_scrape_with_login = ''
    time_to_scrape_with_login = 0
    all_time_values_with_Login = []
    average_time_to_scrape_without_login = ''
    time_to_scrape_without_login = 0
    all_time_values_without_Login = []
    serviceObjectID = ''
    pools = ThreadPool(processes=5)
    for num in range(5):
        startWithLogin = timeit.default_timer()# including login
        loginTime = 0
        browser_crawl = ''
        for x in collection.find({'service_idnetifier': service}):  # {'service_idnetifier':'wordpress'}#toodledo
            # only the action services are scrapped
            serviceObjectID = x['_id']
            serviceID = x['service_idnetifier']
            credentials = []
            credentials.append(x['username'])
            credentials.append(x['password'])
            # #######################################################################################################
            if not x['is_action_service']:
                continue
            if not x['connected']:
                continue
            # if serviceID != 'wordpress':
            #     continue
            if serviceID not in servicelist:
                continue
            print(serviceID)
            # try:
            #     if x['login_result'] == 'problem':
            #         print('problem login')
            #         #continue
            # except KeyError:
            #     print('no problem in login')
            # #######################################################################################################
            print(num)
            startLoging =  timeit.default_timer()
            browser_crawl = pools.apply_async(authentication, (webdriver.Firefox(capabilities=cap, service=Service(r'/root/Tools/Firefox/geckodriver'),
                                  options=options), credentials, x['loginurl'])).get()[1]
            endLogin =  timeit.default_timer()
            loginTime =  endLogin - startLoging
            print(browser_crawl)
            ####################### open login page ##
            if serviceID == 'musixmatch':  # or serviceID =='google_sheets' :serviceID == 'coqon'or
                continue
            clusterbynamedict, crawledTotalForEachCount = check(serviceID)
            if crawledTotalForEachCount:
                if (num not in crawledTotalForEachCount.keys()) and len(crawledTotalForEachCount) != (num + 1):
                    # # ############################################################################################
                    ## crawl: second argument is retry no
                    successs = crawl(num, 1, serviceID, x, browser_crawl)
                    if successs:
                        if num == 4:
                            stop = timeit.default_timer()
                            print('Time taken: ', stop - startWithLogin)
                            print(scrappedDetails)
                else:
                    print('already in')
            else:
                # first round
                # # ############################################################################################
                crawl(num, 1, serviceID, x, browser_crawl)


        stopWithLogin = timeit.default_timer()
        timeWithLogin = stopWithLogin -startWithLogin
        timeWioutLogin = timeWithLogin - loginTime
        time_to_scrape_with_login = time_to_scrape_with_login + timeWithLogin
        time_to_scrape_without_login = time_to_scrape_without_login + timeWioutLogin
        all_time_values_with_Login.append(timeWithLogin)
        all_time_values_without_Login.append(timeWioutLogin)
        browser_crawl.quit()



    e1 = timeit.default_timer()
    print('Total Time = ' + str(e1 - s1))
    average_time_to_scrape_with_login = time_to_scrape_with_login/5
    average_time_to_scrape_without_login  = time_to_scrape_without_login/5
    collection.update({'_id': serviceObjectID}, {'$set': {'average_time_to_scrape_with_login': average_time_to_scrape_with_login,'average_time_to_scrape_without_login':average_time_to_scrape_without_login,'all_time_values_with_Login':all_time_values_with_Login,'all_time_values_without_Login':all_time_values_without_Login}})

# pocket: 17.177752407005755
# email: 10.518108017000486
