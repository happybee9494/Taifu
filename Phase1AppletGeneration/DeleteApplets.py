from builtins import print, KeyError
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from pymongo import MongoClient
import timeit
from threading import Thread
import time
##########################################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
dbClient = client['applets']
appletcollection = dbClient.get_collection('appletcollection12')
all_applet_details = appletcollection.find({})

# ##########################################################################
# options = Options()
# options.add_argument('--headless')
# cap = DesiredCapabilities().FIREFOX
# cap["marionette"] = False
# serv = Service(r'/root/Tools/Firefox/geckodriver')
# browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
# browser.get('https://ifttt.com/login?wp_=1')
#
# username = browser.find_element_by_id("user_username")
# password = browser.find_element_by_id("user_password")
#
# username.send_keys("******@gmail.com")
# password.send_keys("*****")
#
# browser.find_element_by_name("commit").click()

##########################################################################

# my_applets = 'https://ifttt.com/my_applets'
# browser.get(my_applets)
# time.sleep(10)
# applets_page_response = browser.page_source
# applets_page_content = BeautifulSoup(applets_page_response, "html.parser")
#
# applets_section = applets_page_content.find('section', {'class':'dashboard-applets'})
# print(applets_section)
#lists = applets_section.findChildren("li", {'class': 'my-web-applet-card enabled_for_user web-applet-card'}, recursive=True)
#lists = applets_section.findChildren("li", {'class': 'my-web-applet-card web-applet-card'}, recursive=True)
def deleteApplet(applet):
    try:
        # sending get request and saving the response as response object
        token = '0dfb5edac5e2201a9ece7b3908dcfd04d57522b6'  # #1b004674987164ecf6ed87c30146aa90b4c21024
        header = {'Authorization': 'Token token="' + token + '"'}
        post_header = {'Authorization': 'Token token="' + token + '"',
                       'Content-Type': 'application/json; charset=utf-8'}

        URL_for_trigger_data = "https://buffalo-android.ifttt.com/grizzly/me/applets/" + str(applet['applet_id'])
        print(URL_for_trigger_data)
        r = requests.delete(URL_for_trigger_data, headers=header)  # ----------------->
        print(r)
        #appletcollection.remove({'_id': applet['_id']}) ## IFT REQUIRED TO REMOVE FROM THE DATABASE, UNCOMMENT THIS
        # print(appletcollection.count())
    except KeyError:
        print('no id key')
    return


threads = []
s1 = timeit.default_timer()
i = 0
for applet in all_applet_details:
    i = i + 1
    if i%50 == 0:
      time.sleep(10)
    process = Thread(target=deleteApplet, args=[applet])
    process.start()
    threads.append(process)
    e1 = timeit.default_timer()
    print('Time for diff library function= ' + str(e1 - s1))

for process in threads:
    process.join()





