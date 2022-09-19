from email import header
import json
import base64
import hashlib
import secrets
import urllib
from os import environ as env
from urllib.parse import quote_plus, urlencode, parse_qs, urlparse
import requests
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

END_POINT = 'https://{}'.format(env.get("AUTH0_DOMAIN"))
scope = ['email','offline_access','openid']

def url_encode(byte_data):
    return base64.urlsafe_b64encode(byte_data).decode('utf-8').replace('=', '')

def generate_challenge(a_verifier):
    return url_encode(hashlib.sha256(a_verifier.encode()).digest())

def get_pair_of_pkce():
    verifier = url_encode(secrets.token_bytes(32))
    challenge = generate_challenge(verifier).replace('=', '')
    return (verifier, challenge)

def get_auth2_url():
    url = END_POINT + '/authorize' + '?'
    session['state'] = url_encode(secrets.token_bytes(32))
    verifier, challenge = get_pair_of_pkce()
    session['code_verifier'] = verifier
    query_string = {
        'audience': env.get("AUDIENCE"),
        'response_type' : 'code',
        'client_id': env.get("AUTH0_CLIENT_ID"),
        'scope': ' '.join(scope),
        'state': session['state'],
        'redirect_uri': env.get("REDIRECT_URI"),
        'code_challenge_method': 'S256',
        'code_challenge': challenge,
        'prompt': 'login'
    }
    return url + urllib.parse.urlencode(query_string)

def get_auth2_token(code):
    url = END_POINT + '/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': env.get("AUTH0_CLIENT_ID"),
        'code': code,
        'code_verifier': session['code_verifier'],
        'redirect_uri': env.get("REDIRECT_URI")
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, headers=headers,data=data)
    response_json = response.json()
    print(response_json)

    session['user'] = {}
    session['user']['access_token'] = response_json['access_token']
    session['user']['refresh_token'] = response_json['refresh_token']
    session['user']['id_token'] = response_json['id_token']

def get_refresh_token():
    url = END_POINT + '/oauth/token'
    data = {
        'grant_type': 'refresh_token',
        'client_id': env.get("AUTH0_CLIENT_ID"),
        'refresh_token': session['user']['refresh_token'],
        'scope': ' '.join(scope)
    }
    print(data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, headers=headers,data=data)
    response_json = response.json()
    print(response_json)
    session['user'] = {}
    session['user']['access_token'] = response_json['access_token']
    session['user']['refresh_token'] = response_json['refresh_token']
    session['user']['id_token'] = response_json['id_token']

def get_user_info():
    url = END_POINT + '/userinfo'
    headers = {
        'Authorization': 'Bearer {}'.format(session['user']['access_token'])
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    return response.json()

@app.route("/login")
def login():
    url = get_auth2_url()
    return redirect(url)

@app.route("/callback", methods=["GET", "POST"])
def callback():
    url_parsed = urlparse(request.url)
    query_string = parse_qs(url_parsed.query)
    print(query_string)
    code = query_string['code'][0]
    # state = query_string['state'][0]
    get_auth2_token(code)
    return redirect("/")

@app.route("/refresh", methods=["GET"])
def refresh():
    get_refresh_token()
    return render_template("refresh.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/userinfo", methods=["GET"])
def userinfo():
    user_info = get_user_info()
    return render_template("userinfo.html", session=session.get('user'), pretty=json.dumps(user_info, indent=4))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
