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
from pymongo import MongoClient
import timeit
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
#all_auth_details = collection.find({})
#######################
# client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
# db = client.get_database('services')
# collection = db.get_collection('authdetails')
# all_auth_details = collection.find({})
# all_credentials_in_db = {}
########################################################################################################################
# Service Settings
NAME = ''
LOGIN_URL = ''
DOMAIN = ''
data_list =[]
# Fitbit Settings
NAME = 'fitbit'
LOGIN_URL = 'https://accounts.fitbit.com/login'
DOMAIN = 'fitbit.com'
USERNAME_KEY = 'email'
USERNAME = '******@gmail.com'
PASSWORD_KEY = 'password'
PASSWORD = '********'
########################################################################################################################
pageHashdict = {}
urlencounter = {}
# ################################################# Setup Web Driver ###################################################
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
options = Options()
options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
serv = Service(r'/root/Tools/Firefox/geckodriver')
browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
########################################################################################################################
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
        self.name = NAME
        self.start_urls = [LOGIN_URL]
        self.rules = (
            Rule(LinkExtractor(allow_domains=DOMAIN)), Rule(callback='parse_item')
        )
        print('init')
        print(DOMAIN)
        print(LOGIN_URL)
        print(NAME)
        print(data_list)
        print(kwargs.get('round'))
        super(LoginSpider, self).__init__(*args, **kwargs)
        self.round = kwargs.get('round')
        self.browser = kwargs.get('brow')

    def parse(self, response):
        print('parse')
        #self.browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
        self.browser.get(LOGIN_URL)
        print (self.browser.current_url)
        login_type, self.browser = authentication(self.browser,  data_list)
        print (self.browser.current_url)
        print(self.browser.get_cookies())
        self.writeToFile(self.browser.current_url, self.browser.page_source)
        yield SplashRequest(url=self.browser.current_url, callback=self.after_login, endpoint='render.html',cookies=self.browser.get_cookies())

    def writeToFile(self,url,htmltext):
        print('writeToFile()')
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
        if not os.path.exists("scraped_monitoring"):
            os.makedirs("scraped_monitoring")
        # create folder
        if not os.path.exists("scraped_monitoring/"+foldername):
            os.makedirs("scraped_monitoring/"+foldername)
        # create folder
        if not os.path.exists("scraped_monitoring/metadata"):
            os.makedirs("scraped_monitoring/metadata")
        ##############################################
        # create file and page content
        basefilename = "scraped_monitoring/"+foldername+"/"+str(hashurl.hexdigest()) +"_" + str(self.round)
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
        matabasefilename = "scraped_monitoring/metadata"+"/"+str(self.name)
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

    def after_login(self, response):
        print('############')

        if authentication_failed(response):
            self.logger.error("Login failed")
        else:
            print("Login success")
            print(response.url)
            self.writeToFile(response.url, response.text)
            le = LxmlLinkExtractor(allow_domains= DOMAIN)
            print(le.extract_links(response))
            for link in le.extract_links(response):
                yield SplashRequest(url=link.url, callback=self.parse_item, endpoint='render.html',cookies=self.browser.get_cookies())

# the wrapper to make it run more times
def run_spider(spider, x, y):
    def f(q):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider, round=x, brow = y)
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
#
def check(serviceID):
    clusterbynamedict = {}
    crawledTotalForEachCount = {}
    foldername = 'scraped_monitoring/scraped_' + serviceID
    baseFolderName = './' + foldername + '/'
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
        return clusterbynamedict, crawledTotalForEachCount
    except OSError:
        return clusterbynamedict, crawledTotalForEachCount

def crawl(num, isConnected,count,serviceID):
    if isConnected:
        count = count -1
        print(str(num) + ' run:')
        run_spider(LoginSpider, num, browser)
        clusterbynamedict, crawledTotalForEachCount = check(serviceID)
        if (len(crawledTotalForEachCount) < (num + 1)):
            time.sleep(15)
            if count > 0:
                crawl(num, isConnected, count,serviceID)
        elif len(crawledTotalForEachCount) == (num + 1):
            return True

    return False
def monitoring(default_start_no, default_end_no,action_services_to_monitor):
    global NAME, LOGIN_URL,DOMAIN,data_list
    scrappedDetails = {}
    for num in range(default_start_no, default_end_no):
        if num == default_start_no:
            start = timeit.default_timer()

        for x in collection.find({}):
            print(num)
            serviceID = x['service_idnetifier']
            if serviceID in action_services_to_monitor:
                print('do monitoring')
            else:
                continue
            print(serviceID)
            loginURL = x['loginurl']
            domains = x['domains']
            credentials = []
            credentials.append(x['username'])
            credentials.append(x['password'])
            isConnected = x['connected']
            ######################## set values ######
            NAME = serviceID
            LOGIN_URL = loginURL
            DOMAIN = domains
            data_list = credentials
            print(NAME)
            ####################### open login page ##
            if serviceID == 'coqon':  # or serviceID =='google_sheets' :serviceID == 'coqon'or
                continue

            clusterbynamedict, crawledTotalForEachCount = check(serviceID)
            if crawledTotalForEachCount:
                if (num not in crawledTotalForEachCount.keys()) and len(crawledTotalForEachCount) != (num + 1):
                    successs = crawl(num, isConnected, 2,serviceID)
                    if successs:
                        print(scrappedDetails)
            else:
                # first round
                crawl(num, isConnected, 3, serviceID)

        if num == default_end_no:
            stop = timeit.default_timer()
            print('Time taken: ', stop - start)
            print(scrappedDetails)



