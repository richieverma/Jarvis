from django.shortcuts import render
import urllib
import urllib2
import json
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
                return display_dashboard(request.GET['usr'],request)
            else:
                return render(request, 'air/login.html', {})

        else:
            print "fail"
	    return render(request, 'air/suggestor.html', {})

def display_dashboard(username, request):
	#username = request.GET['username']
	#username = request
	query_string = 'username:\"'+username+'\"'
	request_params = urllib.urlencode({'q':query_string,'fl':'team','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	team_players = decoded_json_content["response"]["docs"][0]["team"]
	
	query_string = ''
	for p in team_players: 
		query_string += 'Player:\"'+p+'\" '

	request_params = urllib.urlencode({'q':query_string,'fl':'Player Score Team','wt': 'json', 'indent': 'true'})
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

	context = {"team_players": feed_data, "myteam":context_tweets_myteam, "experts":context_tweets_experts, "players":context_tweets_players}

	return render(request, 'air/display_dashboard.html', context)	    

def display_dashboard_tweets_myteam(team_players):
	query_string = ''
	for p in team_players: 
		if query_string == '':
			query_string = 'tweet_type:1 AND ('
		query_string += 'screen_name:\"'+map_screen_name[p]+'\" '

	if query_string == '':
		return ''
			
	query_string += ')'
	
	#print(query_string)

	request_params = urllib.urlencode({'q':query_string,'sort':'created_at desc','wt': 'json', 'indent': 'true'})
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
		if query_string == '':
			query_string = 'tweet_type:3 AND ('
		team = team_players[p]
		query_string += 'text:\"'+map_screen_name[p]+'\" '
		query_string += 'text:\"'+team+'\" '

		for n in p.split():
			query_string += 'text:\"'+n+'\" '

	if query_string == '':
		return ''
	query_string += ')'
	
	#print(query_string)

	request_params = urllib.urlencode({'q':query_string,'sort':'created_at desc','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)
	return feed_data

def display_dashboard_tweets_players(username):
	query_string = 'username:\"'+username+"\""
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode('utf-8'))
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	feed_data = fix_unicode(feed_data)

	player_query = ''
	for data in feed_data[0]:
		bias = feed_data[0][data]
		if ((data in map_playerBias) and (bias >=4)):
			if player_query == '':
				player_query = 'tweet_type:1 AND ('
			player_query += 'screen_name:\"'+map_screen_name[map_playerBias[data]]+'\" '

	#print player_query
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
	request_params = urllib.urlencode({'q':query_string,'wt': 'json', 'indent': 'true'})
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
	#player=request.GET['player']
	#username=request.GET['usr']
	player="Aaron Brooks"
	username="test"
	request_params = urllib.urlencode({'q':"username:"+username,'fl':'team','wt': 'json', 'indent': 'true'})
	print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	players_inTeam=decoded_json_content['response']['docs'][0]['team']

	request_params = urllib.urlencode({'q':"Player:\""+player+"\"",'fl':'Position','wt': 'json', 'indent': 'true'})
	print request_params
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	pos=decoded_json_content['response']['docs'][0]['Position']

	request_params = urllib.urlencode({'q':"Position:"+pos[0],'fl':'Player','wt': 'json', 'indent': 'true','rows':'1000'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	print req
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	numing=decoded_json_content['response']['numFound']
	players=[]
	for i in range(0,numing-1):
		players.append(decoded_json_content['response']['docs'][i]['Player'])

	for player in players:
		if player in players_inTeam:
			players.remove(player)

	return suggest_ranking(request,players,username)



def suggest_ranking(request,players,username):
	full_thing=[]
	d=defaultdict(float)
	for player in players:
		sa_wt= 25.0
		request_params = urllib.urlencode({'q':'text:\"'+player+'\" AND tweet_score:1','fl':'id','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		num_pos = float(decoded_json_content['response']['numFound'])
		print num_pos

		request_params = urllib.urlencode({'q':'text:\"'+player+'\" AND tweet_score:\"-1\"','fl':'id','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		num_neg = float(decoded_json_content['response']['numFound'])
		print num_neg

		request_params = urllib.urlencode({'q':'text:\"'+player+"\"",'fl':'id','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/tweets/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		num_tot = float(decoded_json_content['response']['numFound'])
		if num_pos>0.0:
			score=sa_wt*(num_pos/num_tot)
		else:
			score=0.0
		print score

		if num_neg>0.0:
			score=score-(sa_wt*(num_neg/num_tot))
		print score
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
		print score


		request_params = urllib.urlencode({'q':'Player:\"'+player+'\"','fl':'Score','wt': 'json', 'indent': 'true'})
		req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
		content = req.read()
		decoded_json_content = json.loads(content.decode())
		stat_score=decoded_json_content['response']['docs'][0]['Score']
		score=score + (50 * (stat_score/100))

		print score
		d[player]= score
		#full_thing.append(d)
	listname = []
	for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		diction= {"Player":key, "Score":value}
		listname.append(diction)
	with open('air/static/js/data2.json', 'wb') as outfile:
		json.dump(listname,outfile)

	return render(request, 'air/suggestor.html', {})








