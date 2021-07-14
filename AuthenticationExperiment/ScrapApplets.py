from builtins import print
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import mysql.connector
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
browser = webdriver.Firefox(capabilities=cap, executable_path=r'/home/python tool/geckodriver')
browser.get('https://ifttt.com/login?wp_=1')

username = browser.find_element_by_id("user_username")
password = browser.find_element_by_id("user_password")

username.send_keys("****@gmail.com")
password.send_keys("****")

browser.find_element_by_name("commit").click()



#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////


#//////////////////////Initi values///////////////////////////////
trigger_service = ''
action_service = ''
applet_title = ''
applet_id = ''
result = ''

second_time = 'No'

#//////////////// Function 1 /////////////////////////////////////
def func_result_page_analysis(browser, div):
    time.sleep(2)
    toggle_div = div.findChildren("div", {'class': 'toggle'}, recursive=True)
    result = ''


    try:
        WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]'))).click()

    except TimeoutException:
        print('')

    try:
        WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]'))).click()

    except TimeoutException:
        print('')


    for toggle in toggle_div:
        browser.find_element_by_class_name('toggle').click()
        print('Results......>>')

        try:
            if browser.find_element_by_class_name('permissions-nav'):
                #/////// Get Service Name
                page_response = browser.page_source
                page_response = BeautifulSoup(page_response, "html.parser")

                try:
                    divp = page_response.findAll('div', {'class': 'applet-permissions permissions-one-account'})

                    for dp in divp:
                        seperator = dp.findChildren("div", {'class': 'separator'}, recursive=True)
                        for sep in seperator:
                            heading3 = sep.findChildren("h3", recursive=True)
                            for h3 in heading3:
                                print(h3.text.strip() + ' Auth Required')
                                result = h3.text.strip() + ' Auth Required'

                except NoSuchElementException:
                    print('')

                try:
                    divp = page_response.findAll('div', {'class': 'applet-permissions permissions-many-accounts'})

                    for dp in divp:
                        seperator = dp.findChildren("div", {'class': 'separator'}, recursive=True)
                        for sep in seperator:
                            if len(seperator) > 1:
                                if sep is not seperator[0]:
                                    result = result + ' and '

                                heading3 = sep.findChildren("h3", recursive=True)
                                for h3 in heading3:
                                    print(h3.text.strip() + ' Auth Required')
                                    result = result + h3.text.strip() + ' Auth Required'


                except NoSuchElementException:
                    print('')
                #////////////////////////////

        except NoSuchElementException:
            print('')


        try:
            applet_name = ''
            header = browser.find_element_by_class_name('header')
            page_response = browser.page_source
            page_response = BeautifulSoup(page_response, "html.parser")
            divp = page_response.findAll('div', {'class': 'full-applet-card editing'})
            for d in divp:
                dcontent = d.findChildren("div", {'class': 'applet-content'}, recursive=True)
                for dc in dcontent:
                    img = dc.findChildren("img", {'class': 'applet-logo'}, recursive=True)
                    for i in img:
                        applet_name = i['title']


            if header.text == 'Configure':
                print('Need Configuration')
                result = str(applet_name) +' Need Configuration'
        except NoSuchElementException:
            print('')

        try:
            if browser.find_element_by_class_name('suggested-applets'):
                print('No Auth Required or No Config Required')
                result = 'No Auth Required or No Config Required'
        except NoSuchElementException:
            print('')
        try:
            if browser.find_element_by_class_name('toggle'):
                print('No Auth Required or No Config Required')
                result = 'No Auth Required or No Config Required'
        except NoSuchElementException:
            print('')


    return result;

#//////////////// Function 2 /////////////////////////////////////
def func_applet_analysis(main_window,browser,lists):
    i = 1
    for li in lists:
        applet_id = li.get('id')
        print(str(i) +' '+li.get('id'))

        #////////////// Check DB for already analysed applet //////////////////
        sql = "SELECT result FROM existing_applets_run1 WHERE applet_id = " + "'"+str(applet_id)+"'"
        mycursor.execute(sql)
        results_values = mycursor.fetchall()
        rc = mycursor.rowcount
        if rc == 1:
            print(rc)
            results_value = 'Yes'
            for r in results_values:
                print(r[0])
                results_value = r[0]
            if results_value is '':
                print('no result hence continue .....')
                second_time = 'Yes'
            else:
                continue

        #////////////////// If the previous record is null then perform analysis, otherwise go to next in for loop ///////////////
        alinks = li.findChildren("a", recursive=False)
        for a in alinks:
            span = a.findChildren("span", {'class': 'title'}, recursive=True)
            a_href_val = a['href']
            for s in span:
                applet_title = s.text.strip()
                print(s.text.strip())

            try:
                first_link =browser.find_element(By.XPATH, ".//*[@href='"+a_href_val+"']")
                time.sleep(2)
                first_link.send_keys(Keys.SHIFT + Keys.RETURN)
                browser.switch_to_window(browser.window_handles[1])
                # ////////////////////////////////////////////
                applet_page_response = browser.page_source
                applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
                # //////// Collect  Service Information///////////////
                div_perm = applet_page_content.findAll('div', {'class': 'permissions-meta'})
                for dperm in div_perm:
                    ulList = dperm.findChildren("li",  recursive=True)
                    services_list = []
                    for li in ulList:
                        heading5 = li.findChildren("h5",  recursive=True)
                        for h5 in heading5:
                            services_list.append(h5.text.strip())

                    if len(services_list) == 2:
                        trigger_service = services_list[0]
                        action_service = services_list[1]
                    if len(services_list) == 3:
                        if 'Notifications' in services_list:
                            services_list.remove('Notifications')
                        trigger_service = services_list[0]
                        action_service = services_list[1]

                print('trigger_service = '+ trigger_service)
                print('action_service = ' + action_service)

                # ////////// toggle button if exists/////////////
                div = applet_page_content.find('div', {'id': 'card'})
                if div:
                    result = func_result_page_analysis(browser, div)
                else:
                    print('Try Again..................')
                    applet_page_response = browser.page_source
                    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
                    div = applet_page_content.find('div', {'id': 'card'})
                    result = func_result_page_analysis(browser, div)

            except NoSuchElementException:
                print('exception 4')

        time.sleep(2)

        #//////////////// Add to database or update //////////////////////////////
        if second_time is 'Yes':
            sql = "UPDATE existing_applets_run1 SET result = " + "'" + str(result) + "'" + "WHERE applet_id = " + "'"+str(applet_id)+"'"
            #mycursor.execute(sql)
            #mydb.commit()
            print(mycursor.rowcount, "record updated.")
            second_time = 'No'
        else:
            sql = "INSERT INTO existing_applets_run1 (applet_id,applet_title, trigger_service,action_service,result) VALUES (%s, %s,%s, %s,%s)"
            val = (applet_id, applet_title, trigger_service, action_service, result)
            #mycursor.execute(sql, val)
            #mydb.commit()
            print(mycursor.rowcount, "record inserted.")

        # ////////////////End adding database record /////////////
        print('///////////////////////////////////////////////')
        browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
        time.sleep(2)
        i += 1
        browser.switch_to_window(main_window)
    return;

#//////////////// Main Funtion ////////////////////////////////////
i = 0
while i < 15:
    browser.find_element_by_class_name('more').click()
    time.sleep(2)
    i += 1

time.sleep(2)
applet_page_response = browser.page_source
applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
# Save the window opener
main_window = browser.current_window_handle
#/////////////////////////////////////////////////////////////////
section = applet_page_content.find('section', {'class': 'applets'})
lists = section.findChildren("li", {'class': 'web-applet-card'}, recursive=True)
print('///////////////////////')

#/////////////.Start Applet Exploring.........////////////////////
func_applet_analysis(main_window,browser,lists)

browser.switch_to_window(main_window)
browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')




