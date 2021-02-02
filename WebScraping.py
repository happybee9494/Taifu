from bs4 import BeautifulSoup
import requests
import mysql.connector

ifttt = 'https://ifttt.com'

ifttt_services = 'https://ifttt.com/services'

page_response = requests.get(ifttt_services, timeout=5)
page_content = BeautifulSoup(page_response.content, "html.parser")

# print soup.prettify()

number_of_services = 0
number_of_categories = 0
number_of_all_services = 0
number_of_all_triggers = 0
number_of_all_actions = 0

#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////



div = page_content.find('div', {'class': 'all-categories'})
sections = div.findChildren("section", recursive=False)
print('.................................................')
for section in sections:
    heading = section.findChildren("h3", recursive=False)
    for category in heading:
        number_of_categories += 1
        print(category.text.strip())
    print('.................................................')
    ulList = section.findChildren("ul", recursive=False)
    for ul in ulList:
        links = ul.findChildren('a', href=True)
        service_name = ''
        service_identifier = ''
        trigger_list = []
        action_list = []
        no_of_triggers = 0
        no_of_actions = 0


        for link in links:
            newa = link['href'].replace("/", "")
            spans = link.findChildren("span", recursive=True)
            for service in spans:
                number_of_services += 1
                number_of_all_services += 1
                service_identifier = newa
                service_name = service.text.strip()
            #///////////////////Explore triggers and actions //////////////////////////////
            service_page_response = requests.get(ifttt+link['href'], timeout=60)
            service_page_content = BeautifulSoup(service_page_response.content, "html.parser")
            divs = service_page_content.findAll('div', {'class': 'tanda'}, recursive=True)
            for div in divs:
                taheading = div.findChildren("h3", recursive=True)
                for tahead in taheading:
                    i=0
                    #print(tahead.text.strip())
                ulList = div.findChildren("ul", recursive=False)
                tirgAcheading = div.findChildren("h4", recursive=True)
                number_of_triggers_or_actions = 0
                for triggerOrAction in tirgAcheading:
                    number_of_triggers_or_actions += 1
                    #print(triggerOrAction.text.strip())
                    if tahead.text.strip() == 'Triggers':
                        trigger_list.append(triggerOrAction.text.strip())
                    if tahead.text.strip() == 'Actions':
                        action_list.append(triggerOrAction.text.strip())

                #print('No of......................... ' + tahead.text.strip() + ':' + str(number_of_triggers_or_actions))
                if tahead.text.strip() == 'Actions':
                    number_of_all_actions += number_of_triggers_or_actions
                    no_of_actions = number_of_triggers_or_actions
                    print('No of actions: ' + str(number_of_triggers_or_actions))

                if tahead.text.strip() == 'Triggers':
                    number_of_all_triggers += number_of_triggers_or_actions
                    no_of_triggers = number_of_triggers_or_actions
                    print('No of triggers: ' + str(number_of_triggers_or_actions))

            #////////////////Add database record ////////////////////
            triggers = ', '.join(str(x) for x in trigger_list)
            actions = ', '.join(str(x) for x in action_list)
            sql = "INSERT INTO services (service_name,service_identifier, trigger_list,no_of_triggers,action_list, no_of_actions) VALUES (%s, %s,%s, %s,%s, %s)"
            val = (service_name,service_identifier,triggers,no_of_triggers,actions,no_of_actions)
            #mycursor.execute(sql, val)

            mydb.commit()

            print(mycursor.rowcount, "record inserted.")
            #////////////////End adding database record /////////////
            trigger_list = []
            action_list = []


    print('No of services: ' + str(number_of_services))
    number_of_services = 0
    print('.................................................')

print('No of categories: ' + str(number_of_categories))
print('No of all services: ' + str(number_of_all_services))
print('No of all trigger: ' + str(number_of_all_triggers))
print('No of all actions: ' + str(number_of_all_actions))









