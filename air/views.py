from django.shortcuts import render
from datetime import datetime, date, timedelta
import urllib
import urllib2
import json
import sys
from collections import OrderedDict
from screenNames import map_screen_name
from playerBias import map_playerBias
from teamBias import map_teamBias
from collections import defaultdict

# Create your views here.

def login(request):
    return render(request, 'air/login.html', {})

def check_login(request):
        request_params = urllib.urlencode({'q':"username:"+request.GET['usr'],'fl':'password','wt': 'json', 'indent': 'true'})
        req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
        content = req.read()
        decoded_json_content = json.loads(content.decode())
        if decoded_json_content['response']['numFound'] > 0:
            pas1 = decoded_json_content['response']['docs'][0]['password']
            if pas1 == request.GET['pass']:
                #return display_dashboard(request.GET['usr'],request)
                return display_dashboard(request)
            else:
                return render(request, 'air/login.html', {})

        else:
            print "fail"
            return render(request, 'air/login.html', {})

def display_dashboard(request):
	username = request.GET['usr']
	query_string = 'username:\"'+username+'\"'
	request_params = urllib.urlencode({'q':query_string,'fl':'team','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	team_players = decoded_json_content["response"]["docs"][0]["team"]
	
	query_string = ''
	for p in team_players: 
		query_string += 'Player:\"'+p+'\" '

	request_params = urllib.urlencode({'q':query_string,'fl':'Player Score Team','wt': 'json', 'indent': 'true','rows':50})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)
	
	player_team_dict = {}
	for f in feed_data:
		player_team_dict[f['Player']] = f['Team']

	context_tweets_myteam = display_dashboard_tweets_myteam(team_players)
	context_tweets_experts = display_dashboard_tweets_experts(player_team_dict)
	context_tweets_players = display_dashboard_tweets_players(username)
	context_tweets_teams = display_dashboard_tweets_teams(username)
	context_next_match = display_dashboard_next_match(player_team_dict)

	context = {"team_players": feed_data, "myteam":context_tweets_myteam, "experts":context_tweets_experts, "players":context_tweets_players,"teams":context_tweets_teams,"username":username, "match":context_next_match}

	return render(request, 'air/display_dashboard.html', context)	

def redirect_dashboard(request):
	#global userTobeDel
	#username = userTobeDel
	username = request.GET['usr']
	username=username.replace("\"","")
	query_string = 'username:\"'+username+'\"'
	request_params = urllib.urlencode({'q':query_string,'fl':'team','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	team_players = decoded_json_content["response"]["docs"][0]["team"]
	
	query_string = ''
	for p in team_players: 
		query_string += 'Player:\"'+p+'\" '

	request_params = urllib.urlencode({'q':query_string,'fl':'Player Score Team','wt': 'json', 'indent': 'true','rows':50})
	print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)
	
	player_team_dict = {}
	for f in feed_data:
		player_team_dict[f['Player']] = f['Team']

	context_tweets_myteam = display_dashboard_tweets_myteam(team_players)
	context_tweets_experts = display_dashboard_tweets_experts(player_team_dict)
	context_tweets_players = display_dashboard_tweets_players(username)
	context_tweets_teams = display_dashboard_tweets_teams(username)
	context_next_match = display_dashboard_next_match(player_team_dict)

	context = {"team_players": feed_data, "myteam":context_tweets_myteam, "experts":context_tweets_experts, "players":context_tweets_players,"teams":context_tweets_teams,"username":username, "match":context_next_match}

	return render(request, 'air/display_dashboard.html', context)	    

def display_dashboard_tweets_myteam(team_players):
	query_string = ''
	for p in team_players: 
		try:
			if query_string == '':
				query_string = 'tweet_type:1 AND ('
			if (p in map_screen_name):
				query_string += 'screen_name:\"'+map_screen_name[p]+'\" '
		except:
			pass


	if query_string == '':
		return ''
			
	query_string += ')'
	
	#print(query_string)

	request_params = urllib.urlencode({'q':query_string,'sort':'created_at desc','wt': 'json', 'indent': 'true','rows':30})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)
	return feed_data

def display_dashboard_tweets_experts(team_players):
	query_string = ''
	for p in team_players: 
		try:
			if query_string == '':
				query_string = 'tweet_type:3 AND ('
			team = team_players[p]
			query_string += 'text:\"'+team+'\" '
			if (p in map_screen_name):
				query_string += 'text:\"'+map_screen_name[p]+'\" '
		except:
			pass

		for n in p.split():
			query_string += 'text:\"'+n+'\" '

	if query_string == '':
		return ''
	query_string += ')'
	
	#print(query_string)

	request_params = urllib.urlencode({'q':query_string,'sort':'created_at desc','wt': 'json', 'indent': 'true','rows':30})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)
	return feed_data

def display_dashboard_tweets_players(username):
	query_string = 'username:\"'+username+"\""
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true','rows':30})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	player_query = ''
	for data in feed_data[0]:
		bias = feed_data[0][data]
		if ((data in map_playerBias) and (bias ==4)):
			if player_query == '':
				player_query = 'tweet_type:1 AND ('
			if (map_playerBias[data] in map_screen_name):
				player_query += 'screen_name:\"'+map_screen_name[map_playerBias[data]]+'\" '

	print player_query
	if player_query=='':
		return ""
	
	player_query += ')'			

	request_params = urllib.urlencode({'q':player_query,'sort':'created_at desc','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	return feed_data

def display_dashboard_tweets_teams(username):
	query_string = 'username:\"'+username+"\""
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true','rows':30})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	team_query = ''
	for data in feed_data[0]:
		bias = feed_data[0][data]
		if ((data in map_teamBias) and (bias >=4)):
			if team_query == '':
				team_query = 'tweet_type:2 AND ('
			if (map_teamBias[data] in map_screen_name):
				team_query += 'screen_name:\"'+map_screen_name[map_teamBias[data]]+'\" '
	
	if team_query=='':
		return ""

	team_query += ')'	

	#print team_query


	request_params = urllib.urlencode({'q':team_query,'sort':'created_at desc','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)
	
	return feed_data

def display_dashboard_next_match(player_team_dict):
	teams = []
	now = datetime.now()
	team_matchTime_dict = {}
	minDiff = sys.maxint
	minTime = ""
	minDate = datetime.now()
	final_matchTime = []

	for key,val in player_team_dict.iteritems():
		if val not in teams:
			teams.append(val)
	#print teams
	query_string = '*:*'
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true','rows':50})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/matches/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)	
	#print feed_data

	for feed in feed_data:
		#print feed
		team_matchTime_dict[feed['team']] = feed['date']
		match_date = datetime.strptime(feed['date'], "%Y-%m-%dT%H:%M:%SZ")
		diff = (match_date-now)
		if (diff.total_seconds() < minDiff and diff.total_seconds() > 0 and feed['team'] in teams):
			minTime = feed['date']
			minDate = match_date
			minDiff = diff.total_seconds()
			#print feed['date']


	for key,val in team_matchTime_dict.iteritems():
		if val == minTime:
			final_matchTime.append(key)
	final_matchTime.append(minDate.strftime("%A %d %B %Y %H:%M"))
	#YYYY-MM-DD hh24:mm:ss
	final_matchTime.append(minDate.strftime("%Y-%m-%d %H:%M:%S"))
	match_end_time = minDate + timedelta(hours=1)
	final_matchTime.append(match_end_time.strftime("%Y-%m-%d %H:%M:%S"))
	#print final_matchTime
	return final_matchTime


def fix_unicode(data):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    elif isinstance(data, dict):
        data = dict((fix_unicode(k), fix_unicode(data[k])) for k in data)
    elif isinstance(data, list):
        for i in xrange(0, len(data)):
            data[i] = fix_unicode(data[i])
    return data	

def suggestor(request):
	player="\""+request.GET['player']+"\""
	username="\""+request.GET['usr']+"\""
	#player="Aaron Brooks"
	#username="test"
	playertobeDel=request.GET['player']
	now = datetime.now()
	request_params = urllib.urlencode({'q':"username:"+username,'fl':'team','wt': 'json', 'indent': 'true'})
	print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	players_inTeam=decoded_json_content['response']['docs'][0]['team']

	request_params = urllib.urlencode({'q':"Player:"+player,'fl':'Position','wt': 'json', 'indent': 'true'})
	print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	pos=decoded_json_content['response']['docs'][0]['Position']

	request_params = urllib.urlencode({'q':"Position:"+pos[0],'fl':'Player Team Injured','wt': 'json', 'indent': 'true','rows':'1000'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	print req
	content = req.read()
	decoded_json_content_later = json.loads(content.decode())
	numing=decoded_json_content_later['response']['numFound']
	players=[]
	players_nomatch=[]
	players_injured=[]
	for i in range(0,numing-1):
		play_tobeadd=decoded_json_content_later['response']['docs'][i]['Player']
		tm=decoded_json_content_later['response']['docs'][i]['Team']
		inj=decoded_json_content_later['response']['docs'][i]['Injured']
		if tm != "FreeAgent" and tm != "NDL" and inj==0 and play_tobeadd!=player.replace("\"",""):
			query2='team:'+"\""+tm+"\""
			request_params3 = urllib.urlencode({'q':query2,'wt': 'json', 'indent': 'true','rows':500})
			req3 = urllib2.urlopen('http://52.37.29.91:8983/solr/matches/select',request_params3)
			content3 = req3.read()
			decoded_json_content = json.loads(content3.decode())
			match_date = datetime.strptime(decoded_json_content['response']['docs'][0]['date'], "%Y-%m-%dT%H:%M:%SZ")
			diff = (match_date-now).days
			diff_seconds = (match_date-now).total_seconds()
			if (diff > 7 or diff_seconds < 0):
				players_nomatch.append(play_tobeadd)
			else:
				players.append(play_tobeadd)
		elif tm != "FreeAgent" and tm != "NDL" and inj!=0 and play_tobeadd!=player.replace("\"",""):
			players_injured.append(play_tobeadd)

	for player in players:
		if player in players_inTeam:
			players.remove(player)

	return suggest_ranking(request, players, players_injured, players_nomatch, username, playertobeDel)

def suggestor_addPlayer(request):
	username="\""+request.GET['usr']+"\""
	#player="Aaron Brooks"
	#username="test"
	now = datetime.now()
	request_params = urllib.urlencode({'q':"username:"+username,'fl':'team','wt': 'json', 'indent': 'true'})
	print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	players_inTeam=decoded_json_content['response']['docs'][0]['team']

	request_params = urllib.urlencode({'q':"*:*",'fl':'Player Team Injured','wt': 'json', 'indent': 'true','rows':'1000'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	print req
	content = req.read()
	decoded_json_content_later = json.loads(content.decode())
	numing=decoded_json_content_later['response']['numFound']
	players=[]
	players_nomatch=[]
	players_injured=[]
	for i in range(0,numing-1):
		play_tobeadd=decoded_json_content_later['response']['docs'][i]['Player']
		tm=decoded_json_content_later['response']['docs'][i]['Team']
		inj=decoded_json_content_later['response']['docs'][i]['Injured']
		if tm != "FreeAgent" and tm != "NDL" and inj==0:
			query2='team:'+"\""+tm+"\""
			request_params3 = urllib.urlencode({'q':query2,'wt': 'json', 'indent': 'true','rows':500})
			req3 = urllib2.urlopen('http://52.37.29.91:8983/solr/matches/select',request_params3)
			content3 = req3.read()
			decoded_json_content = json.loads(content3.decode())
			match_date = datetime.strptime(decoded_json_content['response']['docs'][0]['date'], "%Y-%m-%dT%H:%M:%SZ")
			diff = (match_date-now).days
			diff_seconds = (match_date-now).total_seconds()
			if (diff > 7 or diff_seconds < 0):
				players_nomatch.append(play_tobeadd)
			else:
				players.append(play_tobeadd)
		elif tm != "FreeAgent" and tm != "NDL" and inj!=0 :
			players_injured.append(play_tobeadd)

	for player in players:
		if player in players_inTeam:
			players.remove(player)
	print players
	return suggest_ranking_addPlayer(request,players,players_injured,players_nomatch,username)


def suggest_ranking_addPlayer(request,players,players_injured,players_nomatch,username):
	full_thing=[]
	d=defaultdict(float)
	d_stat=defaultdict(float)
	suggest_ranking_inj(players_injured,players_nomatch,username)
	d_team={}
	for player in players:
		sa_wt= 25.0
		score=0.0

		#print score
		pla_temp=player.replace(" ","")
		pla_temp=pla_temp.replace(".","")
		pla_temp=pla_temp.replace("'","")
		pla_temp=pla_temp.replace("-","")
		pla_user=pla_temp.lower()
		request_params = urllib.urlencode({'q':'username:'+username,'fl':''+pla_user,'wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		bias=int(decoded_json_content['response']['docs'][0][pla_user])

		if bias>0.0:
			score= score + (25.0 * (bias/5.0))
		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score sentiment Team','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		team=decoded_json_content['response']['docs'][0]['Team']
		score=score + (50.0 * (stat_score/100.0))
		score=score+sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		#full_thing.append(d)
	listname = []
	for key, value in d.iteritems():
		diction= {"Player":key, "Score":value, "team_url":"/static/images/"+d_team[key]+".jpg"}
		listname.append(diction)
	with open('air/static/js/data2.json', 'wb') as outfile:
		json.dump(listname,outfile)

	listname2 = []
	for key, value in d_stat.iteritems():
		diction= {"Player":key, "Score":value,"team_url":"/static/images/"+d_team[key]+".jpg"}
		listname2.append(diction)
	with open('air/static/js/data3.json', 'wb') as outfile:
		json.dump(listname2,outfile)

	username = username.replace("\"","")
	context = {"username":username}
	return render(request, 'air/addPlayer.html', context)

def addPlayerTeam(request):
	player="\""+request.GET['player']+"\""
	play=request.GET['player']
	ub="\""+request.GET['usr']+"\""
	#query_string = "username:\""+userTobeDel+"\""
	query_string1 = 'username:'+ub
	request_params1 = urllib.urlencode({'q':query_string1,'fl':'team','wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	team_players = decoded_json_content1["response"]["docs"][0]["team"]
	if play not in team_players:
		my_data='[{"username":'+ub+',"team":{"add":'+player+'}}]'
		req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
		req.add_header('Content-type', 'application/json')
		print req.get_full_url()
		f = urllib2.urlopen(req)
		print(f)
	return redirect_dashboard(request)


def suggest_ranking_inj(players_injured, players_nomatch, username):
	full_thing=[]
	d=defaultdict(float)
	d1=defaultdict(float)
	d_stat=defaultdict(float)
	d_team={}
	d_nom={}
	d_injtp={}
	d_comm={}
	for player in players_injured:
		sa_wt= 25.0
		score=0.0
		#print score
		pla_temp=player.replace(" ","")
		pla_temp=pla_temp.replace(".","")
		pla_temp=pla_temp.replace("'","")
		pla_temp=pla_temp.replace("-","")
		pla_user=pla_temp.lower()
		request_params = urllib.urlencode({'q':'username:'+username,'fl':''+pla_user,'wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		bias=int(decoded_json_content['response']['docs'][0][pla_user])

		if bias>0.0:
			score= score + (25.0 * (bias/5.0))
		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score sentiment Team injured_url Injured','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		team=decoded_json_content['response']['docs'][0]['Team']
		score=score + (50.0 * (stat_score/100.0))
		score=score+sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		if decoded_json_content['response']['docs'][0]['Injured'] == 1:
			d_injtp[player]="Game Time Decision"
		else:
			d_injtp[player]="OUT"
		d_comm[player]=decoded_json_content['response']['docs'][0]['injured_url']

		if player in players_nomatch:
			d_nom[player]="NoMatch.jpg"
			players_nomatch.remove(player)
		else:
			d_nom[player]="Match.png"
	listname = []
	for key, value in d.iteritems():
		diction= {"Player":key, "CScore":value,"SScore":d_stat[key], "team_url":"/static/images/"+d_team[key]+".jpg" ,"Match":"/static/images/"+d_nom[key],"Injured":"/static/images/NBAInjured.jpeg","Injured_type":d_injtp[key],"Info":d_comm[key]}
		listname.append(diction)

	for player in players_nomatch:
		sa_wt= 25.0
		score=0.0
		#print score
		pla_temp=player.replace(" ","")
		pla_temp=pla_temp.replace(".","")
		pla_temp=pla_temp.replace("'","")
		pla_temp=pla_temp.replace("-","")
		pla_user=pla_temp.lower()
		request_params = urllib.urlencode({'q':'username:'+username,'fl':''+pla_user,'wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		bias=int(decoded_json_content['response']['docs'][0][pla_user])

		if bias>0.0:
			score= score + (25.0 * (bias/5.0))
		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score sentiment Team','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		team=decoded_json_content['response']['docs'][0]['Team']
		score=score + (50.0 * (stat_score/100.0))
		score=score + sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d1[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team

		#full_thing.append(d)
	for key, value in d1.iteritems():
		diction= {"Player":key, "CScore":value,"SScore":d_stat[key], "team_url":"/static/images/"+d_team[key]+".jpg" ,"Match":"/static/images/NoMatch.jpg","Injured":"/static/images/NBANotInjured.jpg"}
		listname.append(diction)
	with open('air/static/js/data4.json', 'wb') as outfile:
		json.dump(listname,outfile)

	return



def suggest_ranking(request, players, players_injured, players_nomatch, username, playertobeDel):
	full_thing=[]
	d=defaultdict(float)
	d_stat=defaultdict(float)
	suggest_ranking_inj(players_injured,players_nomatch,username)
	d_team={}
	for player in players:
		sa_wt= 25.0
		score=0.0
		#print score
		pla_temp=player.replace(" ","")
		pla_temp=pla_temp.replace(".","")
		pla_temp=pla_temp.replace("'","")
		pla_temp=pla_temp.replace("-","")
		pla_user=pla_temp.lower()
		request_params = urllib.urlencode({'q':'username:'+username,'fl':''+pla_user,'wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		bias=int(decoded_json_content['response']['docs'][0][pla_user])

		if bias>0.0:
			score= score + (25.0 * (bias/5.0))
		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score Team sentiment','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		team=decoded_json_content['response']['docs'][0]['Team']
		score=score + (50.0 * (stat_score/100.0))
		score=score + sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		#full_thing.append(d)
	listname = []
	for key, value in d.iteritems():
		diction= {"Player":key, "Score":value, "team_url":"/static/images/"+d_team[key]+".jpg"}
		listname.append(diction)
	with open('air/static/js/data2.json', 'wb') as outfile:
		json.dump(listname,outfile)

	listname2 = []
	for key, value in d_stat.iteritems():
		diction= {"Player":key, "Score":value,"team_url":"/static/images/"+d_team[key]+".jpg"}
		listname2.append(diction)
	with open('air/static/js/data3.json', 'wb') as outfile:
		json.dump(listname2,outfile)

	username = username.replace("\"","")
	context = {"username":username,"playertobeDel":playertobeDel}
	return render(request, 'air/suggestor.html', context)

def replace_players(request):
	injured_players = []
	no_match_team = []
	final_player = []
	final_team = []
	final_score = []
	reason = []
	now = datetime.now()

	username = request.GET['usr']
	query_string1 = 'username:\"'+username+'\"'
	request_params1 = urllib.urlencode({'q':query_string1,'fl':'team','wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	team_players = decoded_json_content1["response"]["docs"][0]["team"]
	
	query_string2 = ''
	for p in team_players: 
		query_string2 += 'Player:\"'+p+'\" '

	request_params2 = urllib.urlencode({'q':query_string2,'fl':'Player Team Score Injured','wt': 'json', 'indent': 'true', 'rows':100})
	req2 = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params2)
	
	content2 = req2.read()
	decoded_json_content2 = json.loads(content2.decode('utf-8'))
	json_response2 = decoded_json_content2["response"]
	feed_data2 = json_response2["docs"]
	feed_data2 = fix_unicode(feed_data2)
	
	player_team_dict = {}
	team_player_dict = {}
	player_score_dict = {}
	final_dict = OrderedDict()

	query_string3 = ''
	for f in feed_data2:
		player_team_dict[f['Team']] = f['Player']
		team_player_dict[f['Player']] = f['Team']
		player_score_dict[f['Player']] = f['Score']
		
		if (f['Injured'] != 0 ):
			injured_players.append(f['Player'])
			final_dict[f['Player']] = f['Team']
			final_player.append(f['Player'])
			final_team.append(f['Team'])
			final_score.append(player_score_dict[f['Player']])
			reason.append("Injured")

		query_string3 += 'team:\"'+f['Team']+'\" '

	player_score_dict = OrderedDict(sorted(player_score_dict.items(), key=lambda t: t[1]))

	request_params3 = urllib.urlencode({'q':query_string3,'wt': 'json', 'indent': 'true','rows':100})
	req3 = urllib2.urlopen('http://52.37.29.91:8983/solr/matches/select',request_params3)
	
	content3 = req3.read()
	decoded_json_content3 = json.loads(content3.decode('utf-8'))
	json_response3 = decoded_json_content3["response"]
	feed_data3 = json_response3["docs"]
	feed_data3 = fix_unicode(feed_data3)		
	#print feed_data3
	team_match_dict = {}

	for f in feed_data3:
		team_match_dict[f['team']] = f['date']
		match_date = datetime.strptime(f['date'], "%Y-%m-%dT%H:%M:%SZ")
		diff = (match_date-now).days
		#print "--------TOTAL"
		diff_seconds = (match_date-now).total_seconds()
		if (diff > 7 or diff_seconds < 0):
			no_match_team.append(f['team'])
			for f2 in feed_data2:
				if ((f2['Team'] == f['team']) and (f2['Player'] not in final_dict)):
					final_dict[f2['Player']] = f2['Team']
					final_player.append(f2['Player'])
					final_team.append(f2['Team'])
					final_score.append(player_score_dict[f2['Player']])					
					reason.append("Match")
					#print("No Matches in the next 7 days")
					


	for key,val in player_score_dict.iteritems():
		if ((key not in final_dict)):
			final_dict[key] = team_player_dict[key]	
			final_player.append(key)
			final_team.append(team_player_dict[key])
			final_score.append(player_score_dict[key])				
			reason.append("Score")

	#final_json = json.dumps(final_dict)

	#context = {"team_players":final_dict.iteritems()}
	context = {"team_players":zip(final_player,final_team, final_score, reason),"username":username}
	print context
	print final_dict
	return render(request, 'air/replace_players.html', context)

def deletePlayer(request):
	player="\""+request.GET['player']+"\""
	play=request.GET['player']
	del_p="\""+request.GET['playertobeDel']+"\""
	ub="\""+request.GET['usr']+"\""
	#query_string = "username:\""+userTobeDel+"\""
	query_string1 = 'username:'+ub
	request_params1 = urllib.urlencode({'q':query_string1,'fl':'team','wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	team_players = decoded_json_content1["response"]["docs"][0]["team"]
	print team_players
	if play not in team_players:
		my_data='[{"username":'+ub+',"team":{"add":'+player+'}}]'
		req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
		req.add_header('Content-type', 'application/json')
		#print req.get_full_url()
		f = urllib2.urlopen(req)
		print(f)
	my_data='[{"username":'+ub+',"team":{"remove":'+del_p+'}}]'
	req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
	req.add_header('Content-type', 'application/json')
	#print req.get_full_url()
	f = urllib2.urlopen(req)
	print(f)
	ub=ub.replace("\"","")
	return redirect_dashboard(request)

def deleteSelectedPlayer(request):
	del_p="\""+request.GET['deleteSelectedPlayer']+"\""
	ub="\""+request.GET['usr']+"\""
	#query_string = "username:\""+userTobeDel+"\""
	query_string1 = 'username:'+ub
	request_params1 = urllib.urlencode({'q':query_string1,'fl':'team','wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	team_players = decoded_json_content1["response"]["docs"][0]["team"]
	print team_players
	print del_p
	
	my_data='[{"username":'+ub+',"team":{"remove":'+del_p+'}}]'
	req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
	req.add_header('Content-type', 'application/json')
	#print req.get_full_url()
	f = urllib2.urlopen(req)
	print(f)
	return redirect_dashboard(request)