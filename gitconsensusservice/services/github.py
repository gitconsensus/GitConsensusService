from datetime import datetime, timedelta
import jwt
import os
import re
import requests
import time
from gitconsensus.repository import Repository
from gitconsensusservice import app
import github3


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

    nextpage = get_link_from_response(response)
    if nextpage:
        nextresults = request(nextpage)
        retobj += nextresults
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
        if exptime > testtime:
            return tokens[installation_id]['token']

    url = "installations/%s/access_tokens" % (installation_id,)
    tokens[installation_id] = request(url, 'POST')
    return tokens[installation_id]['token']


def get_installation_repositories(installation_id, url=False):
    if not url:
        url = 'https://api.github.com/installation/repositories'
    res = installation_request(installation_id, url)
    repodata = res.json()
    repos = [repo['full_name'] for repo in repodata['repositories']]
    nextpage = get_link_from_response(res)
    if nextpage:
        repos += get_installation_repositories(installation_id, nextpage)
    return repos


def installation_request(installation_id, url):
    client = get_github3_client(installation_id)
    headers = {'Accept': 'application/vnd.github.machine-man-preview+json'}
    res = client._get(url, headers=headers)
    res.raise_for_status()
    return res


def list_prs(installation_id, user, repo):
    repository = get_repository(installation_id, user, repo).repository
    prs = repository.iter_pulls(state="open")
    return [pr.number for pr in prs]


def get_repository(install_id, username, repository_name):
    client = get_github3_client(install_id)
    return Repository(username, repository_name, client)


def get_github3_client(installation_id):
    token = get_installation_token(installation_id)
    return github3.login(token=token)


def get_link_from_response(response):
    if 'Link' in response.headers:
        regex = r"\<https://api.github.com/([^>]*)\>; rel=\"([a-z]*)\""
        groups = re.findall(regex, response.headers['Link'])
        for group in groups:
            if group[1] == 'next':
                return group[1]
    return False
