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
