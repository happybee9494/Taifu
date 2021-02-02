from bs4 import BeautifulSoup
from pymongo import MongoClient
import timeit
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
ifttt_services = 'https://ifttt.com/services'
#No of categories: 46
#No of all services: 619
########################################################################################################################
############################################# GET IFTTT SERVICE DETIALS PAGE ###########################################
options = Options()
options.add_argument('--headless')
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
serv = Service(r'/root/Tools/Firefox/geckodriver')
browser = webdriver.Firefox(capabilities=cap, service=serv,options=options)
browser.get(ifttt_services)
service_page_response = browser.page_source
page_content = BeautifulSoup(service_page_response, "html.parser")
div = page_content.find('div', {'class': 'all-categories'})
sections = div.findChildren("section", recursive=False)
########################################################################################################################
number_of_services = 0
number_of_categories = 0
number_of_all_services = 0
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
db = client['services']
collection = db.get_collection('eventdetails')
all_auth_details = collection.find({})
########################################################################################################################

for section in sections:
    ################################## READ CATEGORY OF THE SERVICE ####################################################
    print('.................................................')
    heading = section.findChildren("h3", recursive=False)
    categoryName = ''
    for category in heading:
        number_of_categories += 1
        print(category.text.strip())
        categoryName = category.text.strip()
    print('.................................................')
    ################################### FIND LINKS INCLUDING SERVICES###################################################
    ulList = section.findChildren("ul", recursive=False)
    for ul in ulList:
        links = ul.findChildren('a', href=True)
        ################ Defin variable to stor detaisl ###############
        service_name = ''
        service_identifier = ''
        trigger_list = []
        action_list = []
        no_of_triggers = 0
        no_of_actions = 0
        for link in links:
            newa = link['href'].replace("/", "")
            spans = link.findChildren("span", recursive=True)
            ################################### READ SERVICE NAME ######################################################
            for service in spans:
                number_of_services += 1
                number_of_all_services += 1
                service_identifier = newa
                service_name = service.text.strip()
            ############################### UPDATE DATABASE SERVICE EVENT DETAILS #####################################
            doc = {
                'service_idnetifier': service_identifier,
                'category' : categoryName,
                'service_name':service_name
            }
            collection.update(doc, doc, upsert=True)
            ############################################################################################################


    print('No of services: ' + str(number_of_services))
    number_of_services = 0
    print('.................................................')

print('No of categories: ' + str(number_of_categories))
print('No of all services: ' + str(number_of_all_services))










