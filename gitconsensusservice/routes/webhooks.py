from gitconsensusservice import app
from flask import abort, request
import hmac
from hashlib import sha1
from ipaddress import ip_address, ip_network
import json
import logging
import requests


@app.route('/githook', methods=['POST'])
def githook():

    # Restrict to only Github IP Addresses unless in Debug mode
    if 'DEBUG' not in app.config or not app.config['DEBUG']:
        trusted_proxies = {'127.0.0.1'}  # define your own set
        route = request.access_route + [request.remote_addr]
        remote_addr = next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)
        ip_remote_address = ip_address(remote_addr)
        whitelist = requests.get('https://api.github.com/meta').json()['hooks']
        for valid_ip in whitelist:
            if ip_remote_address in ip_network(valid_ip):
                break
        else:
            logging.warning('Github webhook must come from a Github IP Address')
            abort(403)

    # If secret is set use it to validate message.
    if 'GITHUB_WEBHOOK_SECRET' in app.config and app.config['GITHUB_WEBHOOK_SECRET']:
        secret = app.config.get['GITHUB_WEBHOOK_SECRET']
        header_signature = request.headers.get('X-Hub-Signature')
        if header_signature is None:
            logging.warning('Github webhook received without expected authentication signature')
            abort(403)

        sha_type, signature = header_signature.split('=')
        if sha_type != 'sha1':
            logging.warning('Github webhook sent with invalide authentication algorithm')
            abort(501)

        mac = hmac.new(str(secret), msg=request.data, digestmod='sha1')
        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            logging.warning('Github webhook sent without valid signature')
            abort(403)

    if 'X-Github-Event' not in request.headers:
        logging.warning('Github webhook is missing event header')
        abort(400)

    event = request.headers.get('X-GitHub-Event')
    payload = request.get_json()

    if event == 'ping':
        return json.dumps({'msg': 'pong'})
