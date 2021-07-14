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
import time
from multiprocessing import Process, Queue
#https://github.com/scrapy/scrapy

# Twitter Settings
# NAME = onenote
# URL = 'http://mobile.twitter.com'
# LOGIN_URL = 'https://mobile.twitter.com/login'
# DOMAIN = 'mobile.twitter.com'
# USERNAME_KEY = 'session[username_or_email]'
# USERNAME = 'anonymousbee94@gmail.com'
# PASSWORD_KEY = 'session[password]'
# PASSWORD = 'sdrmalkanthi2'

# Fitbit Settings
NAME = 'fitbit'
LOGIN_URL = 'https://accounts.fitbit.com/login'
DOMAIN = 'fitbit.com'
USERNAME_KEY = 'email'
USERNAME = '********@gmail.com'
PASSWORD_KEY = 'password'
PASSWORD = '********'

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

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={USERNAME_KEY: USERNAME, PASSWORD_KEY: PASSWORD},
            callback=self.after_login
        )

    def writeToFile(self,url,htmltext):
        #check and update url encounter
        if url in urlencounter.keys():
            for k, v in urlencounter.items():
                if k is url:
                    urlencounter[k]=urlencounter[k] + 1
        else:
            urlencounter[url] = 1

        foldername = 'scraped_monitor_'+self.name
        #encode url
        encodedurl = url.encode('utf-8')
        hashurl = hashlib.md5(encodedurl)
        pageHashdict[hashurl] = url
        #create folder
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        #create file and write
        basefilename = foldername+"/"+str(hashurl.hexdigest()) +"_" + str(self.round)
        print(urlencounter)
        if urlencounter[url] == 1:
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
        if authentication_failed(response):
            self.logger.error("Login failed")
        else:
            self.logger.error("Login success")
            self.logger.error(response.url)
            #print(response.text)
            le = LxmlLinkExtractor(allow_domains=DOMAIN)
            #print(le.extract_links(response))
            for link in le.extract_links(response):
                yield Request(link.url, callback=self.parse_item)


#1
#process.crawl(LoginSpider,start_urls=start_urls, rules=rules)#args=CrawlSpider)
# x = _crawl(None, LoginSpider)
# process.start(stop_after_crawl=False) # the script will block here until the crawling is finished

# process = CrawlerProcess(get_project_settings())
# process.crawl(LoginSpider)
# process.start()

#2
##Start crawlin process
# configure_logging()
# runner = CrawlerRunner()
# runner.crawl(LoginSpider,round=pl.r)
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())
# reactor.run() # the script will block here until all crawling jobs are finished
# time.sleep(10)
# pl.r = pl.r+1
# print('######################################################################################################## ' +str(pl.r))
#
# if pl.r > 2:
#     print('DONE')
# else:
#     #os.execl(sys.executable, sys.executable, *sys.argv)
#     print('note dones')

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
# time.sleep(150)
# print('\nsecond run:')
# run_spider(LoginSpider,2)
