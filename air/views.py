from django.shortcuts import render
import urllib
import urllib2
import json

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
            return display_dashboard(request.GET['usr'],request)

        else:
            print "fail"
	    return render(request, 'air/login.html', {})

def display_dashboard(username, request):
	#username = request.GET['username']
	#username = request
	query_string = 'username:\"'+username+'\"'
	request_params = urllib.urlencode({'q':query_string,'fl':'team','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/userData/select',request_params)
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	team_players = decoded_json_content["response"]["docs"][0]["team"]
	
	query_string = ''
	for p in team_players: 
		query_string += 'Player:\"'+p+'\" '
		print(p)

	request_params = urllib.urlencode({'q':query_string,'fl':'Player Score Team','wt': 'json', 'indent': 'true'})
	req = urllib2.urlopen('http://52.37.29.91:8983/solr/stats/select',request_params)
	
	content = req.read()
	decoded_json_content = json.loads(content.decode())
	json_response = decoded_json_content["response"]
	feed_data = json_response["docs"]
	print(feed_data[0]["Team"])
	context = {"data": feed_data}
	

	return render(request, 'air/display_dashboard.html', context)	    

