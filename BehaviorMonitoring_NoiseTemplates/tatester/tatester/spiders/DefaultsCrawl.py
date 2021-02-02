from builtins import print
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
import time
from scrapy_splash import SplashRequest, SplashFormRequest
# Scrapy:  https://github.com/scrapy/scrapy
# Splash: http://scrapingauthority.com/scrapy-javascript # Docs:https://splash.readthedocs.io/en/stable/api.html

# Twitter Settings
NAME = 'twitter'
URL = 'http://mobile.twitter.com'
LOGIN_URL = 'https://mobile.twitter.com/login'
DOMAIN = 'mobile.twitter.com'
USERNAME_KEY = 'session[username_or_email]'
USERNAME = 'anonymousbee94@gmail.com'
PASSWORD_KEY = 'session[password]'
PASSWORD = 'sdrmalkanthi2'

# Fitbit Settings
# NAME = 'fitbit'
# URL = 'https://accounts.fitbit.com'
# LOGIN_URL = 'https://accounts.fitbit.com/login'
# DOMAIN = 'accounts.fitbit.com'
# USERNAME_KEY = 'ember642'
# USERNAME = 'kulanitharaka@gmail.com'
# PASSWORD_KEY = 'ember643'
# PASSWORD = '3me3@UTOWn'

# Bitly
# NAME = 'bitly'
# URL = 'https://app.bitly.com'
# LOGIN_URL = 'https://bitly.com/a/sign_in?rd=/Bj4a6Mgus8Z/bitlinks/'
# DOMAIN = 'app.bitly.com'
# USERNAME_KEY = 'username'
# USERNAME = 'anonymousbee94@gmail.com'
# PASSWORD_KEY = 'password'
# PASSWORD = '3me3@UTOWn'

pageHashdict = {}
urlencounter = {}

def authentication_failed(response):
    print(response)
    pass

class LoginSpider(CrawlSpider):
    name = NAME
    start_urls = [LOGIN_URL]
    rules = (
        Rule(LinkExtractor(allow_domains=DOMAIN)), Rule(callback='parse_item')
    )
    def __init__(self, *args, **kwargs):
        super(LoginSpider, self).__init__(*args, **kwargs)
        self.round = kwargs.get('round')

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield SplashRequest(url=url, callback=self.parse, endpoint='render.html')

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={USERNAME_KEY: USERNAME, PASSWORD_KEY: PASSWORD},
            callback=self.after_login
        )

    def writeToFile(self,url,htmltext):
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
        # create folder
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        # create file and write
        basefilename = foldername+"/"+str(hashurl.hexdigest()) +"_" + str(self.round)
        print(urlencounter)
        if urlencounter[url] is 1:
            try:
                f = open(basefilename+ ".html")
                f.close()
                print("File exist")
            except IOError:
                print("File not exist")
                f = open(basefilename+ ".html", "w+")
                f.write(htmltext)
                f.close()
                print(htmltext)

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        self.writeToFile(response.url, response.text)

    def after_login(self, response):
        print('############')

        if authentication_failed(response):
            self.logger.error("Login failed")
        else:
            print("Login success")
            print(response.url)
            print(response.text)
            le = LxmlLinkExtractor(allow_domains= DOMAIN)
            # print(le.extract_links(response))
            for link in le.extract_links(response):
                yield Request(link.url, callback=self.parse_item)


# #Start crawlin process
# configure_logging()
# runner = CrawlerRunner()
# runner.crawl(LoginSpider)
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())
# reactor.run() # the script will block here until all crawling jobs are finished
# time.sleep(100)
# os.execl(sys.executable, sys.executable, *sys.argv)
#3
# the wrapper to make it run more times
def run_spider(spider, x):
    def f(q):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider, round=x)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

print('first run:')
run_spider(LoginSpider,1)
time.sleep(10)
print('\nsecond run:')
run_spider(LoginSpider,2)