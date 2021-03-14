from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, send_from_directory
from gitconsensusservice import app
import gitconsensusservice.routes.webhooks


@app.route('/')
def index():
    return redirect('https://www.gitconsensus.com/')


accepted_events = [
    'pull_request'
]

pr_events = [
    'pull_request',
    'pull_request_review_comment',

]


@app.route('/githook')
def githook():
    if request.method == 'GET':
        return 'OK'

    event_type = request.headers.get('X-GitHub-Event')

    if event_type == "ping":
        return json.dumps({'msg': 'Hi!'})

    payload = json.loads(request.data)
    install_id = payload['installation']['id']

    if event_type == 'installation':
        if payload['action'] != 'deleted'
            consensus.process_installation(install_id)
        return 'OK'

    if event_type == 'installation_repositories':
        for repository in payload['repositories_added']:
            repo_owner = repository['full_name'].split('/')[0]
            consensus.process_repository.delay(install_id, repo_owner, repository['name'])
        return 'OK'

    # Ignore bots to prevent response loops.
    if payload['sender']['type'] == 'Bot':
        return 'OK'

    repo_name = payload['repository']['name']
    repo_owner = payload['repository']['owner']['name']


    if event_type == 'pull_request':
        pr = payload['pull_request']
        if payload['action'] == 'closed' and not pr['merged']:
            # Clean up labels if PR was closed by a human (since bots are rejected above)
            consensus.remove_pull_request_labels.delay(install_id, repo_owner, repo_name, pr['number'])
        else:
            # Process pull request on any other action.
            consensus.process_pull_request.delay(install_id, repo_owner, repo_name, pr['number'])
        return 'OK'

    if event_type == 'repository':
        if payload['action'] != 'deleted':
            consensus.process_repository.delay(install_id, repo_owner, repo_name)
        return 'OK'

    if event_type == 'issue_comment':
        if payload['action'] != 'deleted':
            consensus.process_pull_request.delay(install_id, repo_owner, repo_name, payload['issue']['number'])
        return 'OK'

    if event_type == 'repository_import':
        if payload['action'] == 'success':
            consensus.process_repository.delay(install_id, repo_owner, repo_name)
        return 'OK'


    return 'OK'
