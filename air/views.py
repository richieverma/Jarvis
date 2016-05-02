from django.shortcuts import render
from datetime import datetime, date, timedelta
import urllib
import urllib2
import json
import sys
from collections import OrderedDict
from screenNames import map_screen_name
from playerBias import map_playerBias, map_biasPlayer
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
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	feed = decoded_json_content["response"]["docs"][0]
	#If a new user logs in, there is no team. Display blank dashboard

	try:
		team_players = feed["team"]
	except:
		return render(request, 'air/display_dashboard.html', {"username":username})	



	query_string = ''
	for p in team_players: 
		query_string += 'Player:\"'+p+'\" '

	request_params = urllib.urlencode({'q':query_string,'fl':'Player Score Team tweets_negative tweets_positive Injured','sort':'Score desc','wt': 'json', 'indent': 'true','rows':50})
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
	context_tweets_players = display_dashboard_tweets_players(username, team_players)
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
	try:
		team_players = decoded_json_content["response"]["docs"][0]["team"]
	except:
		return render(request, 'air/display_dashboard.html', {"username":username})	 	
	
	query_string = ''
	for p in team_players: 
		query_string += 'Player:\"'+p+'\" '

	request_params = urllib.urlencode({'q':query_string,'fl':'Player Score Team tweets_negative tweets_positive Injured','sort':'Score desc','wt': 'json', 'indent': 'true','rows':50})
	
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
	context_tweets_players = display_dashboard_tweets_players(username, team_players)
	context_tweets_teams = display_dashboard_tweets_teams(username)
	context_next_match = display_dashboard_next_match(player_team_dict)

	context = {"team_players": feed_data, "myteam":context_tweets_myteam, "experts":context_tweets_experts, "players":context_tweets_players,"teams":context_tweets_teams,"username":username, "match":context_next_match}

	return render(request, 'air/display_dashboard.html', context)	    

def display_dashboard_tweets_myteam(team_players):
	query_string = ''
	blank = 1
	for p in team_players: 
		try:
			if query_string == '':
				query_string = 'tweet_type:1 AND ('
			if (p in map_screen_name):
				blank = 0
				query_string += 'screen_name:\"'+map_screen_name[p]+'\" '
		except:
			pass


	if query_string == '' or blank ==1:
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
	blank = 1
	for p in team_players: 
		try:
			if query_string == '':
				query_string = 'tweet_type:3 AND ('
			team = team_players[p]
			query_string += 'text:\"'+team+'\" '
			if (p in map_screen_name):
				blank = 0
				query_string += 'text:\"'+map_screen_name[p]+'\" '
		except:
			pass

		for n in p.split():
			query_string += 'text:\"'+n+'\" '

	if query_string == '' or blank == 1:
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

def display_dashboard_tweets_players(username, team_players):
	query_string = 'username:\"'+username+"\""
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]

	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	player_query = ''
	blank = 1

	for data in feed_data[0]:
		bias = feed_data[0][data]
		if ((data in map_playerBias) and bias >= 4 and map_playerBias[data] not in team_players):
			if player_query == '':
				player_query = 'tweet_type:1 AND ('
			if (map_playerBias[data] in map_screen_name):
				blank = 0
				player_query += 'screen_name:\"'+map_screen_name[map_playerBias[data]]+'\" '

	#print player_query
	if player_query=='' or blank ==1:
		return ""
	
	player_query += ')'			

	request_params = urllib.urlencode({'q':player_query,'sort':'created_at desc','wt': 'json', 'indent': 'true','rows':30})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	return feed_data

def display_dashboard_tweets_teams(username):
	query_string = 'username:\"'+username+"\""
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	team_query = ''
	blank = 1
	for data in feed_data[0]:
		bias = feed_data[0][data]
		if ((data in map_teamBias) and (bias >=4)):
			if team_query == '':
				team_query = 'tweet_type:2 AND ('
			if (map_teamBias[data] in map_screen_name):
				blank = 0
				team_query += 'screen_name:\"'+map_screen_name[map_teamBias[data]]+'\" '
	
	if team_query=='' or blank == 1:
		return ""

	team_query += ')'	

	#print team_query


	request_params = urllib.urlencode({'q':team_query,'sort':'created_at desc','wt': 'json', 'indent': 'true','rows':30})
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
	flag = 0
	for feed in feed_data:
		#print feed
		team_matchTime_dict[feed['team']] = feed['date']
		match_date = datetime.strptime(feed['date'], "%Y-%m-%dT%H:%M:%SZ")
		diff = (match_date-now)
		if (diff.total_seconds() < minDiff and diff.total_seconds() > 0 and feed['team'] in teams):
			flag = 1
			minTime = feed['date']
			minDate = match_date
			minDiff = diff.total_seconds()
			#print feed['date']

	if (flag == 0):
		return final_matchTime

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
	#print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	#print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	players_inTeam=decoded_json_content['response']['docs'][0]['team']

	tot_sal=0.0
	player_score=0.0
	player_score_stat=0.0
	player_sal=0.0
	for p_tm in players_inTeam:
		request_params = urllib.urlencode({'q':"Player:\""+p_tm+'\"','fl':'salary sentiment Score','wt': 'json', 'indent': 'true'})
		#print request_params
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		#print req
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		try:
			salary=decoded_json_content['response']['docs'][0]['salary']
		except:
			salary=0.0
		if p_tm != player.replace("\"",""):
			tot_sal=tot_sal+salary
		else:
			player_sal=salary
			pla_temp1=player.replace("\"","")
			pla_temp=pla_temp1.replace(" ","")
			pla_temp=pla_temp.replace(".","")
			pla_temp=pla_temp.replace("'","")
			pla_temp=pla_temp.replace("-","")
			pla_user=pla_temp.lower()
			stat_score=0.0
			sent_score=0.0
			stat_score=decoded_json_content['response']['docs'][0]['Score']
			sent_score=decoded_json_content['response']['docs'][0]['sentiment']
			request_params = urllib.urlencode({'q':'username:'+username,'fl':''+pla_user,'wt': 'json', 'indent': 'true'})
			req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
			content = req.read()
			decoded_json_content = json.loads(content.decode())
			bias_score=0.0
			bias=int(decoded_json_content['response']['docs'][0][pla_user])
			if bias>0.0:
				bias_score=(stat_score * (bias/25.0))
			player_score=sent_score+bias_score
			player_score_stat=stat_score

	money_left=50000-tot_sal

	request_params = urllib.urlencode({'q':"Player:"+player,'fl':'Position','wt': 'json', 'indent': 'true'})
	#print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	#print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	pos=decoded_json_content['response']['docs'][0]['Position']

	pos_query = ''
	for p in pos:
		pos_query+='Position:'+ p + ' '
	request_params = urllib.urlencode({'q':pos_query+"AND salary:[* TO "+str(money_left)+"]",'fl':'Player Team Injured','wt': 'json', 'indent': 'true','rows':'1000'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	#print req
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

	final_players = []
	for player1 in players:
		if player1 not in players_inTeam:
			#players.remove(player)
			final_players.append(player1)

	final_players_injured = []
	for player_i in players_injured:
		if player_i not in players_inTeam:
			#players.remove(player)
			final_players_injured.append(player_i)

	final_players_nomatch = []
	for player_nm in players_nomatch:
		if player_nm not in players_inTeam:
			#players.remove(player)
			final_players_nomatch.append(player_nm)

	return suggest_ranking(request, final_players, final_players_injured, final_players_nomatch, username, playertobeDel,player,player_sal,player_score,player_score_stat)

def suggestor_addPlayer(request):
	username="\""+request.GET['usr']+"\""
	#player="Aaron Brooks"
	#username="test"
	now = datetime.now()
	request_params = urllib.urlencode({'q':"username:"+username,'fl':'team','wt': 'json', 'indent': 'true'})
	#print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	#print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())

	#There will be no team for new user
	try:
		players_inTeam=decoded_json_content['response']['docs'][0]['team']
	except:
		players_inTeam=[]

	tot_sal=0.0
	for p_tm in players_inTeam:
		request_params = urllib.urlencode({'q':"Player:\""+p_tm+'\"','fl':'salary','wt': 'json', 'indent': 'true'})
		#print request_params
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		#print req
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		salary=decoded_json_content['response']['docs'][0]['salary']
		tot_sal=tot_sal+salary

	money_left=50000-tot_sal

	request_params = urllib.urlencode({'q':"salary:[* TO "+str(money_left)+"]",'fl':'Player Team Injured','wt': 'json', 'indent': 'true','rows':'1000'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	#print req
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

	final_players = []
	for player in players:
		#print player
		if player not in players_inTeam:
			#players.remove(player)
			final_players.append(player)

	final_players_injured = []
	for player_i in players_injured:
		if player_i not in players_inTeam:
			#players.remove(player)
			final_players_injured.append(player_i)
			
	final_players_nomatch = []
	for player_nm in players_nomatch:
		if player_nm not in players_inTeam:
			#players.remove(player)
			final_players_nomatch.append(player_nm)
	
	return suggest_ranking_addPlayer(request,final_players,final_players_injured,final_players_nomatch,username)


def suggest_ranking_addPlayer(request,players,players_injured,players_nomatch,username):
	full_thing=[]
	d=defaultdict(float)
	d_stat=defaultdict(float)
	suggest_ranking_inj(players_injured,players_nomatch,username,0.0,0.0)
	d_team={}
	d_sal={}
	d_pos={}
	d_tpos={}
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

		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score sentiment Team salary Position tweets_positive','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		try:
			sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		except:
			sent_score=0
		team=decoded_json_content['response']['docs'][0]['Team']
		position=decoded_json_content['response']['docs'][0]['Position']
		num_position=decoded_json_content['response']['docs'][0]['tweets_positive']*100
		d_tpos[player]=num_position
		show_p=""
		for p in position:
			show_p=show_p+p+" "
		d_pos[player]= show_p
		#score=score + (50.0 * (stat_score/100.0))
		bias_score=0.0
		if bias>0.0:
			bias_score= (stat_score * (bias/25.0))
		score=bias_score+sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		d_sal[player]=decoded_json_content['response']['docs'][0]['salary']
		#full_thing.append(d)
	listname = []
	count=0
	for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		count=count+1
		diction= {"Rank":count,"Player":key, "Score":value, "team_url":"/static/images/"+d_team[key]+".jpg","Salary":d_sal[key],"Position":d_pos[key],"Sent":+d_tpos[key]}
		listname.append(diction)
	with open('air/static/js/data2.json', 'wb') as outfile:
		json.dump(listname,outfile)

	listname2 = []
	count=0
	for key, value in sorted(d_stat.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		count=count+1
		diction= {"Rank":count,"Player":key, "Score":value,"team_url":"/static/images/"+d_team[key]+".jpg","Salary":d_sal[key],"Position":d_pos[key],"Sent":d_tpos[key]}
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
	tab_type = request.GET['tab']
	rank = request.GET['rank']
	#query_string = "username:\""+userTobeDel+"\""
	query_string1 = 'username:'+ub
	request_params1 = urllib.urlencode({'q':query_string1,'wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	feed = decoded_json_content1["response"]["docs"][0]
	#No team for new user
	try:
		team_players = feed["team"]
	except:
		team_players = []

	try:
		cur_evalScore = feed['cur_evalScore']
		max_evalScore = feed['max_evalScore']
	except:
		cur_evalScore = 0
		max_evalScore = 0

	#Do not add player if already in team
	if play not in team_players:
		#Adjust bias towards player
		my_data='[{"username":'+ub+',"team":{"add":'+player+'}'
		if (feed[map_biasPlayer[play]] < 5):
			my_data='[{"username":'+ub+',"team":{"add":'+player+'},"'+map_biasPlayer[play]+'":{"set":5}'
		else:
			my_data='[{"username":'+ub+',"team":{"add":'+player+'},"'+map_biasPlayer[play]+'":{"set":'+ str(1.1*feed[map_biasPlayer[play]])+'}'

		#Change weights of sentiment, bias and stats for user based on selection for replacing player
		if (tab_type=='S'):
			if (int(rank)>10):
				add_evalScore = 0.5
			else:
				add_evalScore = float(0.5*(11-int(rank)))
			my_data+=',"cur_evalScore":{"set":'+str(float(cur_evalScore)+add_evalScore)+'}'
			my_data+=',"max_evalScore":{"set":'+str(float(max_evalScore)+10)+'}'
			my_data+=',"sentiment":{"set":'+str(feed['sentiment']-0.5)+'},"bias":{"set":'+str(feed['bias']-0.5)+'},"stats":{"set":'+str(feed['stats']+1)+'}'
		elif (tab_type=='R'):
			if (int(rank)>10):
				add_evalScore = 0.5
			else:
				add_evalScore = float(0.5*(11-int(rank)))			
			my_data+=',"cur_evalScore":{"set":'+str(float(cur_evalScore)+add_evalScore)+'}'
			my_data+=',"max_evalScore":{"set":'+str(float(max_evalScore)+10)+'}'
			my_data+=',"sentiment":{"set":'+str(feed['sentiment']-0.5)+'},"bias":{"set":'+str(feed['bias']+1)+'},"stats":{"set":'+str(feed['stats']-0.5)+'}'
		elif (tab_type=='C'):
			if (int(rank)>10):
				add_evalScore = 1
			else:
				add_evalScore = float(11-int(rank))
			my_data+=',"cur_evalScore":{"set":'+str(float(cur_evalScore)+add_evalScore)+'}'
			my_data+=',"max_evalScore":{"set":'+str(float(max_evalScore)+10)+'}'
			#Decrease bias of all players above this player in the list
			with open('air/static/js/data2.json', 'r') as readjson:
				jdata = json.load(readjson)
				for data in jdata:
					if (int(data['Rank']) < int(rank)):
						print data['Player']
						my_data+=',"'+map_biasPlayer[data['Player']]+'":{"set":'+ str(0.9*feed[map_biasPlayer[data['Player']]])+'}'
					else:
						break			
		my_data+='}]'

		#print my_data


		req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
		req.add_header('Content-type', 'application/json')
		#print req.get_full_url()
		f = urllib2.urlopen(req)
		#print(f)
	return redirect_dashboard(request)


def suggest_ranking_inj(players_injured, players_nomatch, username,player_2bsal,player_2bscore):
	full_thing=[]
	d=defaultdict(float)
	d1=defaultdict(float)
	d_stat=defaultdict(float)
	d_team={}
	d_nom={}
	d_injtp={}
	d_comm={}
	d_injured={}
	d_sal={}
	d_profit={}
	d_pos={}
	d_tpos={}
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

		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score sentiment Position Team tweets_positive injured_url Injured salary','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		try:
			sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		except:
			sent_score = 0
		team=decoded_json_content['response']['docs'][0]['Team']
		position=decoded_json_content['response']['docs'][0]['Position']
		show_p=""
		for p in position:
			show_p=show_p+p+" "
		d_pos[player]= show_p

		num_position=decoded_json_content['response']['docs'][0]['tweets_positive']*100
		d_tpos[player]=num_position
		#score=score + (50.0 * (stat_score/100.0))
		bias_score=0.0
		if bias>0.0:
			bias_score= (stat_score* (bias/25.0))
		score=bias_score+sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		d_sal[player]=decoded_json_content['response']['docs'][0]['salary']
		d_injured[player]="NBAInjured.jpeg"
		if decoded_json_content['response']['docs'][0]['Injured'] == 1:
			d_injtp[player]="Game Time Decision"
		else:
			d_injtp[player]="OUT"
		try:
			d_comm[player]=decoded_json_content['response']['docs'][0]['injured_url']
		except:
			d_comm[player]=""
		if player in players_nomatch:
			d_nom[player]="NBAMatch.jpg"
			players_nomatch.remove(player)
		else:
			d_nom[player]="Match.png"
		if d[player]>player_2bscore and d_sal[player]<=player_2bsal:
			d_profit[player]="green.png"
		else:
			d_profit[player]="NBANotInjured.jpg"

	listname = []
	#count=0
	#for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=True):
	#	count=count+1
	#	diction= {"Rank":count,"Player":key, "CScore":value,"SScore":d_stat[key], "team_url":"/static/images/"+d_team[key]+".jpg" ,"Match":"/static/images/"+d_nom[key],"Injured":"/static/images/NBAInjured.jpeg","Injured_type":d_injtp[key],"Info":d_comm[key]}
	#	listname.append(diction)

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

		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score sentiment Team salary Position tweets_positive','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		try:
			sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		except:
			sent_score=0
		team=decoded_json_content['response']['docs'][0]['Team']
		position=decoded_json_content['response']['docs'][0]['Position']
		show_p=""
		for p in position:
			show_p=show_p+p+" "
		d_pos[player]= show_p
		num_position=decoded_json_content['response']['docs'][0]['tweets_positive']*100
		d_tpos[player]=num_position
		d_sal[player]=decoded_json_content['response']['docs'][0]['salary']
		#score=score + (50.0 * (stat_score/100.0))
		bias_score=0.0
		if bias>0.0:
			bias_score=(stat_score * (bias/25.0))
		score=bias_score + sent_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		d_injured[player]="NBANotInjured.jpg"
		d_nom[player]="NBAMatch.jpg"
		d_comm[player]=" "
		d_injtp[player]=" "
		if d[player]>player_2bscore and d_sal[player]<=player_2bsal:
			d_profit[player]="green.png"
		else:
			d_profit[player]="NBANotInjured.jpg"
		#full_thing.append(d)
	count=0
	for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		count=count+1
		diction= {"Rank":count,"Player":key, "CScore":value,"SScore":d_stat[key], "team_url":"/static/images/"+d_team[key]+".jpg" ,"Match":"/static/images/"+d_nom[key],"Injured":"/static/images/"+d_injured[key],"Injured_type":d_injtp[key],"Info":d_comm[key],"Salary":d_sal[key],
				  "Profit":"/static/images/"+d_profit[key],"Position":d_pos[key],"Sent":d_tpos[key]}
		listname.append(diction)
	with open('air/static/js/data4.json', 'wb') as outfile:
		json.dump(listname,outfile)

	return



def suggest_ranking(request, players, players_injured, players_nomatch, username, playertobeDel,player_2b,player_2bsal,player_2bscore,player_2bscore_stat):
	full_thing=[]
	d=defaultdict(float)
	d_stat=defaultdict(float)
	suggest_ranking_inj(players_injured,players_nomatch,username,player_2bsal,player_2bscore)
	d_team={}
	d_sal={}
	d_profit={}
	d_profit_stat={}
	d_pos={}
	d_tpos={}
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

		#print score

		score_only_stat=0.0
		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score Team sentiment salary Position tweets_positive','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		position=decoded_json_content['response']['docs'][0]['Position']
		show_p=""
		for p in position:
			show_p=show_p+p+" "
		d_pos[player]= show_p

		num_position=decoded_json_content['response']['docs'][0]['tweets_positive']*100
		d_tpos[player]=num_position
		bias_score=0.0
		if bias>0.0:
			bias_score=(stat_score * (bias/25.0))
		try:
			sent_score=decoded_json_content['response']['docs'][0]['sentiment']
		except:
			sent_score=0
		team=decoded_json_content['response']['docs'][0]['Team']
		#score=score + (50.0 * (stat_score/100.0))
		score=sent_score+bias_score
		score_only_stat=score_only_stat + (stat_score)

		#print score
		d[player]= score
		d_stat[player]=score_only_stat
		d_team[player]=team
		d_sal[player]=decoded_json_content['response']['docs'][0]['salary']
		if d[player]>player_2bscore and d_sal[player]<=player_2bsal:
			d_profit[player]="green.png"
		else:
			d_profit[player]="NBANotInjured.jpg"
		if d_stat[player]>player_2bscore_stat and d_sal[player]<=player_2bsal:
			d_profit_stat[player]="green.png"
		else:
			d_profit_stat[player]="NBANotInjured.jpg"
		#full_thing.append(d)
	listname = []
	count=0
	for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		count=count+1
		diction= {"Rank":count,"Player":key, "Score":value, "team_url":"/static/images/"+d_team[key]+".jpg","Salary":d_sal[key],"Profit":"/static/images/"+d_profit[key],"Position":d_pos[key],"Sent":d_tpos[key]}
		listname.append(diction)
	with open('air/static/js/data2.json', 'wb') as outfile:
		json.dump(listname,outfile)

	listname2 = []
	count=0
	for key, value in sorted(d_stat.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		count=count+1
		diction= {"Rank":count,"Player":key, "Score":value,"team_url":"/static/images/"+d_team[key]+".jpg","Salary":d_sal[key],"Profit":"/static/images/"+d_profit_stat[key],"Position":d_pos[key],"Sent":d_tpos[key]}
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
	injured_url = []
	position = []
	salary = []
	now = datetime.now()

	username = request.GET['usr']
	query_string1 = 'username:\"'+username+'\"'
	request_params1 = urllib.urlencode({'q':query_string1,'fl':'team','wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	

	#If a new user logs in, there is no team. Display blank dashboard
	try:
		team_players = decoded_json_content1["response"]["docs"][0]["team"]
	except:
		return render(request, 'air/replace_players.html', {"username":username})	

	
	query_string2 = ''
	for p in team_players: 
		query_string2 += 'Player:\"'+p+'\" '

	request_params2 = urllib.urlencode({'q':query_string2,'fl':'Player Team Score Injured injured_url Position salary','wt': 'json', 'indent': 'true', 'rows':100})
	req2 = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params2)
	
	content2 = req2.read()
	decoded_json_content2 = json.loads(content2.decode('utf-8'))
	json_response2 = decoded_json_content2["response"]
	feed_data2 = json_response2["docs"]
	feed_data2 = fix_unicode(feed_data2)
	
	player_team_dict = {}
	team_player_dict = {}
	player_score_dict = {}
	player_pos_dict = {}
	player_sal_dict = {}
	final_dict = OrderedDict()

	query_string3 = ''
	for f in feed_data2:
		player_team_dict[f['Team']] = f['Player']
		team_player_dict[f['Player']] = f['Team']
		player_score_dict[f['Player']] = f['Score']
		player_pos_dict[f['Player']] = f['Position']
		try:
			player_sal_dict[f['Player']] = f['salary']
		except:
			player_sal_dict[f['Player']] = 0
		
		if (f['Injured'] != 0 ):
			injured_players.append(f['Player'])
			final_dict[f['Player']] = f['Team']
			final_player.append(f['Player'])
			final_team.append(f['Team'])
			final_score.append(player_score_dict[f['Player']])
			reason.append("Injured")
			try:
				injured_url.append(f['injured_url'])
			except:
				injured_url.append("")				

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
					injured_url.append("")
					#print("No Matches in the next 7 days")
					


	for key,val in player_score_dict.iteritems():
		if ((key not in final_dict)):
			final_dict[key] = team_player_dict[key]	
			final_player.append(key)
			final_team.append(team_player_dict[key])
			final_score.append(player_score_dict[key])				
			reason.append("Score")
			injured_url.append("")
			
	for pl in final_player:
		position.append(player_pos_dict[pl])
		salary.append(player_sal_dict[pl])

	#final_json = json.dumps(final_dict)

	#context = {"team_players":final_dict.iteritems()}
	context = {"team_players":zip(final_player,final_team, final_score, reason, injured_url, position, salary),"username":username}
	
	#print final_dict
	return render(request, 'air/replace_players.html', context)

def deletePlayer(request):
	player="\""+request.GET['player']+"\""
	play=request.GET['player']
	del_p="\""+request.GET['playertobeDel']+"\""
	ub="\""+request.GET['usr']+"\""
	tab_type = request.GET['tab']
	rank = request.GET['rank']

	#query_string = "username:\""+userTobeDel+"\""
	query_string1 = 'username:'+ub
	request_params1 = urllib.urlencode({'q':query_string1,'wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	feed = decoded_json_content1["response"]["docs"][0]
	feed = fix_unicode(feed)
	team_players = feed["team"]
	

	try:
		cur_evalScore = feed['cur_evalScore']
		max_evalScore = feed['max_evalScore']
	except:
		cur_evalScore = 0
		max_evalScore = 0

	if play not in team_players:
		my_data='[{"username":'+ub+',"team":{"add":'+player+'}'
		if (feed[map_biasPlayer[play]] < 5):
			my_data='[{"username":'+ub+',"team":{"add":'+player+'},"'+map_biasPlayer[play]+'":{"set":5}'
		else:
			my_data='[{"username":'+ub+',"team":{"add":'+player+'},"'+map_biasPlayer[play]+'":{"set":'+ str(1.1*feed[map_biasPlayer[play]])+'}'		

		#Change weights of sentiment, bias and stats for user based on selection for replacing player
		if (tab_type=='S'):
			if (int(rank)>10):
				add_evalScore = 0.5
			else:
				add_evalScore = float(0.5*(11-int(rank)))

			my_data+=',"cur_evalScore":{"set":'+str(float(cur_evalScore)+add_evalScore)+'}'
			my_data+=',"max_evalScore":{"set":'+str(float(max_evalScore)+10)+'}'			
			my_data+=',"sentiment":{"set":'+str(feed['sentiment']-0.5)+'},"bias":{"set":'+str(feed['bias']-0.5)+'},"stats":{"set":'+str(feed['stats']+1)+'}'

		elif (tab_type=='R'):
			if (int(rank)>10):
				add_evalScore = 0.5
			else:
				add_evalScore = float(0.5*(11-int(rank)))

			my_data+=',"cur_evalScore":{"set":'+str(float(cur_evalScore)+add_evalScore)+'}'
			my_data+=',"max_evalScore":{"set":'+str(float(max_evalScore)+10)+'}'			
			my_data+=',"sentiment":{"set":'+str(feed['sentiment']-0.5)+'},"bias":{"set":'+str(feed['bias']+1)+'},"stats":{"set":'+str(feed['stats']-0.5)+'}'

		elif (tab_type=='C'):
			if (int(rank)>10):
				add_evalScore = 1
			else:
				add_evalScore = float(11-int(rank))
			my_data+=',"cur_evalScore":{"set":'+str(float(cur_evalScore)+add_evalScore)+'}'
			my_data+=',"max_evalScore":{"set":'+str(float(max_evalScore)+10)+'}'

			#Decrease bias of all players above this player in the list
			with open('air/static/js/data2.json', 'r') as readjson:
				jdata = json.load(readjson)
				for data in jdata:
					if (int(data['Rank']) < int(rank)):
						print data['Player']
						my_data+=',"'+map_biasPlayer[data['Player']]+'":{"set":'+ str(0.9*feed[map_biasPlayer[data['Player']]])+'}'
					else:
						break

		my_data+='}]'

		print my_data
		req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
		req.add_header('Content-type', 'application/json')
		#print req.get_full_url()
		f = urllib2.urlopen(req)
		#print(f)

	my_data='[{"username":'+ub+',"team":{"remove":'+del_p+'},"'+map_biasPlayer[play]+'":{"set":'+ str(0.8*feed[map_biasPlayer[play]]) +'}'

	#increase bias for the remaining players on team by 5%
	for p in team_players:
		if (p not in player):
			my_data+=',"'+map_biasPlayer[p]+'":{"set":'+ str(1.05*feed[map_biasPlayer[p]]) +'}'
	my_data+='}]'

	#print my_data
	req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
	req.add_header('Content-type', 'application/json')
	#print req.get_full_url()
	f = urllib2.urlopen(req)
	#print(f)
	ub=ub.replace("\"","")
	return redirect_dashboard(request)

def deleteSelectedPlayer(request):
	del_p="\""+request.GET['deleteSelectedPlayer']+"\""
	player = request.GET['deleteSelectedPlayer']
	ub="\""+request.GET['usr']+"\""
	#query_string = "username:\""+userTobeDel+"\""
	query_string1 = 'username:'+ub
	request_params1 = urllib.urlencode({'q':query_string1,'wt': 'json', 'indent': 'true'})
	req1 = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params1)
	content1 = req1.read()
	decoded_json_content1 = json.loads(content1.decode('utf-8'))
	feed = decoded_json_content1["response"]["docs"][0]
	feed = fix_unicode(feed)
	try:
		team_players = feed["team"]
	except:
		return redirect_dashboard(request)
	
	my_data='[{"username":'+ub+',"team":{"remove":'+del_p+'},"'+map_biasPlayer[player]+'":{"set":'+ str(0.8*feed[map_biasPlayer[player]]) +'}'

	#increase bias for the remaining players on team by 5%
	for p in team_players:
		if (p not in player):
			my_data+=',"'+map_biasPlayer[p]+'":{"set":'+ str(1.05*feed[map_biasPlayer[p]]) +'}'
	my_data+='}]'
	req = urllib2.Request(url='http://52.37.29.91:8983/solr/userData/update/json?commit=true', data=my_data)
	req.add_header('Content-type', 'application/json')
	#print req.get_full_url()
	f = urllib2.urlopen(req)
	#print(f)
	return redirect_dashboard(request)