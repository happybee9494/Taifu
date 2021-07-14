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
import urllib


cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False
browser = webdriver.Firefox(capabilities=cap, executable_path=r'/home/python tool/geckodriver')
browser.get('https://ifttt.com/login?wp_=1')

username = browser.find_element_by_id("user_username")
password = browser.find_element_by_id("user_password")

username.send_keys("******@gmail.com")
password.send_keys("*******")

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



def func_applet_analysis(lists, browser):
    second_time = 'No'
    applet_title = ''
    applet_id = ''
    a_href_val = ''
    trigger_service = ''
    action_service = ''
    result = ''

    k = 1
    for li in lists:
        if k is 2:
            continue
        alinks = li.findChildren("a", recursive=False)
        print(alinks)
        for a in alinks:
            span = a.findChildren("span", {'class': 'title'}, recursive=True)
            a_href_val = a['href']
            split1 = a_href_val.split("-", 1)
            split2 = split1[0].split("/", 2)
            applet_id = 'applet-' + split2[2]
            print(str(k) + ' ' + applet_id)
            for s in span:
                applet_title = s.text.strip()
                print(s.text.strip())


        k += 1

        # # ////////////// Check DB for already analysed applet //////////////////
        sql = "SELECT result FROM existing_applets_run1 WHERE applet_id = " + "'" + str(applet_id) + "'"
        mycursor.execute(sql)
        results_values = mycursor.fetchall()
        rc = mycursor.rowcount
        print(rc)

        if rc > 1:
            continue

        if rc == 1:
            results_value = 'Yes'
            for r in results_values:
                print(r[0])
                results_value = r[0]
            if results_value is '':
                print('no result hence continue .....')
                second_time = 'Yes'
            else:
                continue

        # ///////////Click on Applet and Analyse the applet page ////////////

        for a in alinks:
            try:
                #a_href_val = a_href_val.replace("%20", " ")
                #a_href_val = a_href_val.replace("%E2%84%A2", "")
                a_href_val = a_href_val.replace("%27", "''")
                a_href_val = a_href_val.replace("+", " ")
                a_href_val = urllib.parse.unquote(a_href_val)
                print(a_href_val)
                first_link = browser.find_element(By.XPATH, ".//*[@href='" + a_href_val + "']")
                first_link.send_keys(Keys.SHIFT + Keys.RETURN)
                browser.switch_to_window(browser.window_handles[1])
                time.sleep(3)
                # ////////////////////////////////////////////
                applet_page_response = browser.page_source
                applet_page_content = BeautifulSoup(applet_page_response, "html.parser")

                # //////// Collect  Service Information///////////////
                div_perm = applet_page_content.findAll('div', {'class': 'permissions-meta'})
                for dperm in div_perm:
                    ulList = dperm.findChildren("li", recursive=True)
                    services_list = []
                    for li in ulList:
                        heading5 = li.findChildren("h5", recursive=True)
                        for h5 in heading5:
                            services_list.append(h5.text.strip())

                    if len(services_list) == 2:
                        trigger_service = services_list[0]
                        action_service = services_list[1]
                    if len(services_list) == 3:
                        if 'Notifications' in services_list:
                            services_list.remove('Notifications')
                        else:
                            print(services_list)
                            second = services_list[1] + " and " + services_list[2]
                            services_list.remove(services_list[1])
                            services_list.remove(services_list[1])
                            services_list.append(second)

                        trigger_service = services_list[0]
                        action_service = services_list[1]


                print('trigger_service = ' + trigger_service)
                print('action_service = ' + action_service)

                # ////////// toggle button if exists/////////////
                div = applet_page_content.find('div', {'id': 'card'})
                if div:
                    result = func_result_page_analysis(browser, div)
                else:
                    print('Try Again..................')
                    applet_page_response = browser.page_source
                    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")

                    try:
                        div = applet_page_content.find('div', {'class': 'container'})
                        message = div.findChildren("div", {'class': 'message'}, recursive=True)
                        if message is not None:
                            continue
                        print('applet page not available')
                    except:
                        print('error page not available')

                    div = applet_page_content.find('div', {'id': 'card'})
                    result = func_result_page_analysis(browser, div)
                # //////////////

            except NoSuchElementException:
                print('exception 4')

            # //////////////// Add to database or update //////////////////////////////
            if second_time is 'Yes':
                sql = "UPDATE existing_applets_run1 SET result = " + "'" + str(
                    result) + "'" + ", trigger_service = " + "'" + str(
                    trigger_service) + "'" + ", action_service = " + "'" + str(
                    action_service) + "'" +  "WHERE applet_id = " + "'" + str(applet_id) + "'"
                mycursor.execute(sql)
                mydb.commit()
                print(mycursor.rowcount, "record updated.")
                second_time = 'No'
            else:
                sql = "INSERT INTO existing_applets_run1 (applet_id,applet_title, trigger_service,action_service,result) VALUES (%s, %s,%s, %s,%s)"
                val = (applet_id, applet_title, trigger_service, action_service, result)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")

            # ////////////////End adding database record /////////////
        print('///////////////////////////////////////////////')
        browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
        time.sleep(2)

        browser.switch_to_window(main_window)


    return;




#//////////////// Main Funtion ////////////////////////////////////

#/////////// obtain a list of service names from service database
sql = "SELECT service_name FROM services"
mycursor.execute(sql)
search_values = mycursor.fetchall()
rc = mycursor.rowcount

#///// search by service names
i = 0
print(len(search_values))
print(search_values)


ri = 1
while ri  <= 472:
    search_values.remove(search_values[0])
    ri += 1

e = 1
for r in search_values:
    print(str(e) + ' '+r[0])
    e += 1



counter = 473
for r in search_values:
    print(r[0])
    search_value = r[0]
    if i is 0:
        search = browser.find_element_by_id("search-field-input")
        search.send_keys(search_value)
        search.send_keys(Keys.ENTER)
        i += 1

    else:
        browser.find_element_by_id("service-search").clear()
        search = browser.find_element_by_id("service-search")
        search.send_keys(search_value)
        search.send_keys(Keys.ENTER)


    time.sleep(5)
    applet_page_response = browser.page_source
    applet_page_content = BeautifulSoup(applet_page_response, "html.parser")
    main_window = browser.current_window_handle
    # /////////////////////////////////////////////////////////////////
    # // analyse the applet list page
    main = applet_page_content.find('main', {'class': 'search container'})
    if main is None:
        continue
    lists = main.findChildren("li", {'class': 'my-web-applet-card web-applet-card'}, recursive=True)
    print('Service No ...' + str(counter))
    func_applet_analysis(lists, browser)
    counter += 1




