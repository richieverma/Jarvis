from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import urllib2,urllib,json
#import matplotlib.pyplot as plt import seaborn as sns
# #needed to convert unicode to numeric
# import unicodedata - See more at: http://blog.nycdatascience.com/students-work/web-scraping-nba-player-statistics-sumanth-reddy-joseph-russo/#sthash.hSvcDU4P.dpuf

#regular season data
leb = 'http://www.cbssports.com/nba/injuries/daily'
player_string_key = leb
req = requests.get(player_string_key)
text = BeautifulSoup(req.text, "html.parser")
print text
stats = text.find('div', {'id':'DailyTable'})
print stats
# find the schema
cols = [i.get_text() for i in stats.find_all('td')]
print cols
cols=cols[7:len(cols)]
print cols
print len(cols)
# convert from unicode to string
cols = [x.encode('UTF8') for x in cols]
# get rows
players_injured=[]
for i in range(2,len(cols)-1,6):
    players_injured.append(cols[i])
print players_injured

request_params = urllib.urlencode({'q':'*:*','fl':'Player','wt': 'json', 'indent': 'true','rows':1000})
req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
content = req.read()
decoded_json_content = json.loads(content.decode())
all_players=[]
play_list_num=decoded_json_content['response']['numFound']
for i in range(0,play_list_num-1):
    all_players.append(decoded_json_content['response']['docs'][i]['Player'])

for play in players_injured:
    if play not in all_players:
        players_injured.remove(play)

request_params = urllib.urlencode({'q':'Injured:true','fl':'Player','wt': 'json', 'indent': 'true' ,'rows':1000})
req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
content = req.read()
decoded_json_content = json.loads(content.decode())
all_injured_players=[]
play_list_num=decoded_json_content['response']['numFound']
for i in range(0,play_list_num-1):
    all_injured_players.append(decoded_json_content['response']['docs'][i]['Player'])

player_healthy=[]
for play in all_injured_players:
    if play not in players_injured:
        player_healthy.append(play)

for play in players_injured:
    request_params = urllib.urlencode({'q':'Player:\"'+play+"\"",'fl':'Injured','wt': 'json', 'indent': 'true' ,'rows':1000})
    req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
    content = req.read()
    decoded_json_content = json.loads(content.decode())
    print decoded_json_content
    inj=decoded_json_content['response']['docs'][0]['Injured']
    print inj[0]
    if inj[0] == False:
        my_data='[{"Player":"'+play+'","Injured":{"add":true}}]'
        req = urllib2.Request(url='http://52.37.29.91:8983/solr/stats/update/json?commit=true', data=my_data)
        req.add_header('Content-type', 'application/json')
        #print req.get_full_url()
        f = urllib2.urlopen(req)
        print(f)
        my_data='[{"Player":"'+play+'","Injured":{"remove":false}}]'
        req = urllib2.Request(url='http://52.37.29.91:8983/solr/stats/update/json?commit=true', data=my_data)
        req.add_header('Content-type', 'application/json')
        #print req.get_full_url()
        f = urllib2.urlopen(req)
        print(f)


for play in player_healthy:
    request_params = urllib.urlencode({'q':'Player:\"'+play+"\"",'fl':'Injured','wt': 'json', 'indent': 'true' ,'rows':1000})
    req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
    content = req.read()
    decoded_json_content = json.loads(content.decode())
    inj=decoded_json_content['response']['docs'][0]['Injured']
    print inj[0]
    if inj[0] == True:
        my_data='[{"Player":"'+play+'","Injured":{"add":false}}]'
        req = urllib2.Request(url='http://52.37.29.91:8983/solr/stats/update/json?commit=true', data=my_data)
        req.add_header('Content-type', 'application/json')
        #print req.get_full_url()
        f = urllib2.urlopen(req)
        print(f)
        my_data='[{"Player":"'+play+'","Injured":{"remove":true}}]'
        req = urllib2.Request(url='http://52.37.29.91:8983/solr/stats/update/json?commit=true', data=my_data)
        req.add_header('Content-type', 'application/json')
        #print req.get_full_url()
        f = urllib2.urlopen(req)
        print(f)




