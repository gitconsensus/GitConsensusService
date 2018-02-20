from datetime import datetime, timedelta
import jwt
import os
import re
import requests
import time
from gitconsensusservice import app


def get_jwt():
    if not os.path.isfile(app.config['GITHUB_PRIVATE_KEY']):
        raise ValueError('Github Application Key not present')

    with open(app.config['GITHUB_PRIVATE_KEY'], 'r') as keyfile:
        private_key = keyfile.read()

    now = int(time.time())
    payload = {
        # issued at time
        "iat": now,
        # JWT expiration time (10 minute maximum)
        "exp": now + (10 * 60),
        # GitHub App's identifier
        "iss": app.config['GITHUB_APP_ID']
    }
    return jwt.encode(payload, private_key, algorithm='RS256').decode("utf-8")


def request(url, method='GET'):
    if method == 'GET':
        requestfunc = requests.get
    elif method == 'POST':
        requestfunc = requests.post
    apptoken = get_jwt()

    headers = {
        'Authorization': 'Bearer %s' % (apptoken,),
        'Accept': 'application/vnd.github.machine-man-preview+json'
    }
    response = requestfunc('https://api.github.com/%s' % (url,), headers=headers)
    response.raise_for_status()
    retobj = response.json()
    if 'Link' in response.headers:
        regex = r"\<https://api.github.com/([^>]*)\>; rel=\"([a-z]*)\""
        groups = re.findall(regex, response.headers['Link'])
        for group in groups:
            if group[1] == 'next':
                nextresults = request(group[1])
                retobj += nextresults
                break
    return retobj


def get_app():
    return request('app')


def get_installations():
    installs_url = 'app/installations'
    installations = request(installs_url)
    return [i['id'] for i in installations]


def get_installation(installation_id):
    return request('app/installations/%s' % (installation_id,))


tokens = {}


def get_installation_token(installation_id):
    if installation_id in tokens:
        expiration = tokens[installation_id]['expires_at']
        testtime = datetime.now() - timedelta(minutes=3)
        exptime = datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%SZ")
        if exptime < testtime:
            return tokens[installation_id]['token']

    url = "installations/%s/access_tokens" % (installation_id,)
    tokens[installation_id] = request(url, 'POST')
    return tokens[installation_id]['token']
