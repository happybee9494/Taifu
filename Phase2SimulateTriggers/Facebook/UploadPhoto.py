# from facebook import Facebook
#
#
# user_token = 'EAAKwAxAYaaYBAFCC0oCTLC3hyL624p7LT5GinEZBOmVrC40647qE3lNeFQLuoPWK3htMQX1vH0ec4LgzUivsTErlBFWiKPcM53Bg0l83ZAhmDNdy3bPZCGKSCA0PGZADK7oFItVPZCd9dijOJ7yPrUqRJU9ZCJD32CPm4T3rVsxgErhaQxVJvTHZCvSU61ZBe1tMy3gzMbkvrIqVIaBHco6jiXviFJsY7A7ZCUZATz4iubWh4EY5ZCAX4N9SjD8IRC8u6gZD'
#
# graph = GraphAPI(access_token=user_token, version = 2.7)
# events = graph.request('/search?q=Poetry&type=event&limit=10000')


#https://github.com/hikaruAi/FacebookBot


# from FacebookWebBot import *
# bot=FacebookBot()
# bot.set_page_load_timeout(10)
# bot.login("wijitha.mahadewa@email.com","hi5@NUS")
# allpost=bot.getPostInProfile("https://mbasic.facebook.com/your-gf-profile",deep=50)
# for p in allpost:
# 	print(p)


import re
from builtins import print

import requests
import robobrowser
import lxml
import pprint


MOBILE_USER_AGENT = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"


def get_fb_access_token(email, password):
    access_token = ''
    s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    f = s.get_form()
    try:
        s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
        # print(browser.response.content.decode())
        access_token = re.search(
            r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]

        print(access_token)
    except requests.exceptions.InvalidSchema as browserAddress:
        # print(type(browserAddress))
        access_token = re.search(
            r"access_token=([\w\d]+)", str(browserAddress)).groups()[0]
        print(access_token)

    return access_token



def get_fb_id(access_token):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get(
        'https://graph.facebook.com/me?access_token=' + access_token)
    return req.json()["id"]


access_token = get_fb_access_token('wijitha.mahadewa@gmail.com','hi5@NUS')

# x = get_fb_id(access_token)
#
# print(x)

from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.facebook import Facebook

facebook = Facebook(
    app_id='{app_id}',
    app_secret='{app_secret}',
    default_graph_version='v2.12',
)

facebook.set_default_access_token(access_token=access_token)
try:
    response = facebook.get(endpoint='/me?fields=id,name')
except FacebookResponseException as e:
    print(e.message)
else:
    print('User id: %(name)s' % {'name': response.json_body.get('id')})
    print('User name: %(name)s' % {'name': response.json_body.get('name')})

batch = {
    'photo-one': facebook.request(
        endpoint='/me/photos',
        params={
            'message': 'Foo photo.',
            'source': facebook.file_to_upload('path/to/foo.jpg'),
        },
    ),
    'photo-two': facebook.request(
        endpoint='/me/photos',
        params={
            'message': 'Bar photo.',
            'source': facebook.file_to_upload('path/to/bar.jpg'),
        },
    ),
    'photo-three': facebook.request(
        endpoint='/me/photos',
        params={
            'message': 'Other photo.',
            'source': facebook.file_to_upload('path/to/other.jpg'),
        },
    )
}

try:
    responses = facebook.send_batch_request(requests=batch)
except FacebookResponseException as e:
    print(e.message)

