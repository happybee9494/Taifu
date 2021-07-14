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

########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
collection = db.get_collection('authdetails')
all_auth_details = collection.find({})
#####################################################################################
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
        self.browser = webdriver.Firefox(capabilities=cap, service=Service(r'/root/Tools/Firefox/geckodriver'),options=options)
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
                # call authentication method
                login_type, self.browser = authentication(self.browser, self.data_list, self.loginurl)
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
                    yield SplashRequest(url=self.browser.current_url, callback=self.after_login,
                                        endpoint='render.html',
                                        cookies=self.browser.get_cookies())
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

        foldername = 'scraped_'+self.name
        # encode url
        encodedurl = url.encode('utf-8')
        hashurl = hashlib.md5(encodedurl)
        pageHashdict[hashurl] = url
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
def run_spider(spider, x, authObject,statusstring,sfoldername):
    def f(q):
        try:
            runner = CrawlerRunner()
            print('hii')
            deferred = runner.crawl(spider, aobj = authObject,round=x,statusstring=statusstring,sfoldername=sfoldername)
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

def crawl(num, count,serviceID,authObject,statusstring,sfoldername):
    count = count - 1
    print(str(num) + ' run:')

    run_spider(LoginSpider, num, authObject,statusstring,sfoldername)
    clusterbynamedict, crawledTotalForEachCount = check(serviceID,sfoldername)
    if (len(crawledTotalForEachCount) < (num + 1)):
        time.sleep(15)
        if count > 0:
            crawl(num, count, serviceID,authObject,statusstring,sfoldername)
    elif len(crawledTotalForEachCount) == (num + 1):
        return True
    return False

#################################### Read Database and for each service login and scrape ###############################

scrappedDetails = {}
threads = []
s1 = timeit.default_timer()
i = 0


# narro, pocket,amazonclouddrive,toodledo
# before: ============ default_start_no = 0,  default_end_no = 1
# after: ============ default_start_no = 1,  default_end_no = 2
default_start_no = 2
default_end_no = 3
statusstring = 'after'
###
# default_start_no = 0
# default_end_no = 1
# statusstring = 'before'
####################################################################################################################
for service in remaining: # //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if service in mobileSet:
        continue
    if service not in wordpressrheadlessFalse:# if testing headless add not
        headlesslist.append(service)
        continue
    average_time_to_scrape_with_login = ''
    time_to_scrape_with_login = 0
    all_time_values_with_Login = []
    average_time_to_scrape_without_login = ''
    time_to_scrape_without_login = 0
    all_time_values_without_Login = []
    serviceObjectID = ''
    pools = ThreadPool(processes=5)
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
            if not x['is_action_service']:
                continue
            if not x['connected']:
                continue
            # if serviceID != 'wordpress':
            #     continue
            # if serviceID not in androidphoto:#//////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #     continue
            print(serviceID)
            # try:
            #     if x['login_result'] == 'problem':
            #         print('problem login')
            #         #continue
            # except KeyError:
            #     print('no problem in login')
            # #######################################################################################################
            # if serviceID == 'musixmatch':  # or serviceID =='google_sheets' :serviceID == 'coqon'or
            #     continue
            clusterbynamedict, crawledTotalForEachCount = check(serviceID,sfoldername)
            if crawledTotalForEachCount:
                if (num not in crawledTotalForEachCount.keys()) and len(crawledTotalForEachCount) != (num + 1):
                    # # ############################################################################################
                    ## crawl: second argument is retry no
                    successs = crawl(num, 1, serviceID, x,statusstring,sfoldername)
                    if successs:
                        if num == default_end_no:
                            stop = timeit.default_timer()
                            print('Time taken: ', stop - startWithLogin)
                            print(scrappedDetails)
                else:
                    print('already in')
            else:
                # first round
                # # ############################################################################################
                crawl(num, 1, serviceID, x,statusstring,sfoldername)


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
print(headlesslist)
