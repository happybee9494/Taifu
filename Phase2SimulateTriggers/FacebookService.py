from builtins import print
import requests
from pprint import pprint
from builtins import print
import urllib
import urllib3
import brotli

post_header = {
    'Content-Type':'application/x-www-form-urlencoded',
    'Connection':'keep-alive',
    'Host': 'www.facebook.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8s',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': ' https://www.facebook.com/',
    'Content-Length': 2235,
    'Origin': 'https://www.facebook.com',
    'DNT': 1,
    'Cookie': 'sb=3tnMWhutj2G8JXP2Uo7ab9m8; datr=3tnMWovduIkmglEVd0Y9OvrT; fr=11cf6QRpxPaXzpO6J.AWVy_uOCMcutq9zCUZkklyKyrlA.BdXWpt.sF.F3W.0.0.Bd15xK.AWXRv8h5; wd=972x488; dpr=1.25; locale=en_US'

}
# cookiess = {0.B
#     'sb':'hDnzXDiwuPQP9nJYZWU1Oaxm',
#     'fr':'08PGQfY3RR9MXltYj.AWUkMTCzdmovMMsg9kcxKtduWDg.Bc8zY2.u_.F3N.0.0.Bd3Ndb.AWVyldIq',
#     'wd':'972x488',
#     'datr':'ijnzXGFYkXL4hJYkKZUL6DLF',
#     'dpr':'1.2000000476837158',
#     'locale':'en_US'}

data = {'email':'wijitha.mahadewa@gmail.com','pass':'wdwmahadewa'}

URL_for_trigger_data = "https://www.facebook.com/login/device-based/regular/login/"



data = urllib.parse.urlencode(data)
print(data)
r = requests.post(URL_for_trigger_data,data= data, headers=post_header)#, cookies=cookiess)
pprint(r)
print(brotli.decompress(r.content))

#######################################################
# post_header = {
#     'Content-Type':'application/x-www-form-urlencoded',
#     'Connection':'keep-alive',
#     'Postman-Token':'1b61a07e-0dd3-448c-90f6-78eb034f46b2',
#    'Host': 'www.facebook.com',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
#     'Accept': '*/*',
#     'Accept-Language': 'en-US,en;q=0.5',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Referer': 'https://www.facebook.com/profile.php?id=100010002395463',
#     'Content-Length': 2235,
#     'Origin': 'https://www.facebook.com'
# }
#
#
# cookiess = {
#     'sb':'hDnzXDiwuPQP9nJYZWU1Oaxm',
#     'datr':'ijnzXGFYkXL4hJYkKZUL6DLF',
#     'fr':'08PGQfY3RR9MXltYj.AWXAhlBzhjx0i3q5I372SwugCCs.Bc8zY2.u_.F3N.0.0.Bd3Mv9.AWUl1w36',
#     'wd':'972x488',
#     'dpr':'1.25',
#     'c_user':'100010002395463',
#     'xs':'46%3Al9lNS5xGbXxJaQ%3A2%3A1573735230%3A-1%3A-1',
#     'presence': 'EDvF3EtimeF1574751288EuserFA21B1B2395463A2EstateFDutF1574751288073CEchFDp_5f1B1B2395463F1CC',
#     'act': '1574751237376%2F0',
#     'spin':'r.1001473079_b.trunk_t.1574751225_s.1_v.2_'}
#
#
data = {
'variables':'{"client_mutation_id":"a7c0f5a6-adf3-492b-8ce7-2e6e6c222ffd","actor_id":"100010002395463","input":{"actor_id":"100010002395463","client_mutation_id":"46d05bfa-1a63-472d-8ef6-9e8c8a67c778","source":"WWW","audience":{"web_privacyx":"286958161406148"},"message":{"text":"pppppppppppppppppppppppppppppppppppppppppppppppp","ranges":[]},"logging":{"composer_session_id":"bf6119dc-171e-4eda-9315-5a0a2e8c1912","ref":"timeline"},"with_tags_ids":[],"multilingual_translations":[],"camera_post_context":{"deduplication_id":"bf6119dc-171e-4eda-9315-5a0a2e8c1912","source":"composer"},"composer_source_surface":"timeline","composer_entry_point":"timeline","composer_entry_time":1,"composer_session_events_log":{"composition_duration":12,"number_of_keystrokes":5},"branded_content_data":{},"direct_share_status":"NOT_SHARED","sponsor_relationship":"WITH","web_graphml_migration_params":{"target_type":"feed","xhpc_composerid":"rc.u_ps_jsonp_3_3_1","xhpc_context":"profile","xhpc_publish_type":"FEED_INSERT","xhpc_timeline":true},"extensible_sprouts_ranker_request":{"RequestID":"afBaCwABAAAAJDQxZWQxNDFjLTAwOTItNGZlMC04NTYwLWM3ZGM2NDQ2YzcwMwoAAgAAAABd3KDNCwADAAAAB1FfQU5EX0EGAAQALwsABQAAABhVTkRJUkVDVEVEX0ZFRURfQ09NUE9TRVIA"},"external_movie_data":{},"place_attachment_setting":"HIDE_ATTACHMENT"}}',
'__user':1052094341800636,
'__a':1,
'__dyn':'EAAGm0PX4ZCpsBAFr6EZBcrPIkVeTFDqTjmsILHUR59Ig5nQYiIZAuNXGADZBPGKirS7cE6h3oWNqqZCaljdUuxW3xurbJkggcrdI82RMLTWF025M15glYfL89Ylv0I8HEcxYhgcpPAc7KRj8ZAagDMYHKkKj8PEBeZCqqn2ZAPGkXBOe9t8aWBHXMFiY9bCUEF1nHmfYespTJZC4qlnGXZBvNt29H8xby99WoXZCjroxpnFKVBWVFHw2ZAUB',
'__csr':'',
'__req':'1f',
'__pc':'PHASED:DEFAULT',
'dpr':1.5,
'__rev':1001465009,
'__s':'yz1wd7:hkrnr4:dtru67',
'__hsi':67621222047228216190,
'fb_dtsg':'AQEBfFsTmqik:AQEfpEhacQxK',
'jazoest':2678,
'__spin_r':1001465009,
'__spin_b':'trunk',
'__spin_t':1574429265

}

URL_for_trigger_data = "https://www.facebook.com/webgraphql/mutation/?doc_id=1052094341800636"
r = requests.post(URL_for_trigger_data,data= data, headers=post_header)#, cookies=cookiess)

pprint(r)
print(r.headers)
import brotli
print(brotli.decompress(r.content))