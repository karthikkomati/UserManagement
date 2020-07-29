import json
import os

import db as connection
from flask import Flask, jsonify,request,redirect, url_for

from user import User


from flask_login import (
    LoginManager,
    current_user,
    #login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#os.environ['GOOGLE_CLIENT_ID'] = 
#os.environ['GOOGLE_CLIENT_SECRET'] = 

# Configuration
#print(os.environ.get("GOOGLE_CLIENT_SECRET", None))

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


users={}

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@login_manager.user_loader
def load_user(user_id):
    return connection.getCurrentUser(user_id)

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    print(request.base_url)
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/isLoggedIn")
def isLoggedIn():    
    return str(current_user.is_authenticated)

@app.route("/login/callback")
def loginCallback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

# Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    user = User(
        id_=unique_id, name=users_name, email=users_email
    )
    if not connection.getCurrentUser(unique_id):
        connection.addCurrentUser(unique_id,users_name,users_email)
    users[unique_id]= user
    login_user(user)
    return redirect(url_for("getAll"))

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return "logged out"


@app.route('/getAll')
def getAll():
    if current_user.is_authenticated:

        
        return connection.getAll()
    else:
        return "please login"



@app.route('/get')
def get():

    if current_user.is_authenticated:

        
        return connection.get(request.args.get('col'),request.args.get('val'))
    else:
        return "please login"
    


@app.route('/deleteUser')
def deleteUser():
    if current_user.is_authenticated:

        
        return connection.deleteUser(request.args.get('username'),)
    else:
        return "please login"



@app.route('/delete')
def delete():
    
    if current_user.is_authenticated:

        
        return connection.delete(request.args.get('col'),request.args.get('val'))
    else:
        return "please login"
    

@app.route('/update')
def update():
    if current_user.is_authenticated:

        
        return connection.update(request.args.get('col'),request.args.get('val'),request.args.get('username'))
    else:
        return "please login"


@app.route('/updateAll')
def updateAll():
    if current_user.is_authenticated:

        
        return connection.updateAll(request.args.get('firstname'),request.args.get('lastname'),request.args.get('newusername'),request.args.get('password'),request.args.get('email'),request.args.get('active'),request.args.get('username'))
    else:
        return "please login"
    


@app.route('/create')
def create():
    if current_user.is_authenticated:

        
        return connection.create(request.args.get('firstname'),request.args.get('lastname'),request.args.get('username'),request.args.get('password'),request.args.get('email'),request.args.get('active'))
    else:
        return "please login"

@app.route('/usernameContains')
def usernameContains():
    if current_user.is_authenticated:

        
        return connection.usernameContains(request.args.get('word'))
    else:
        return "please login"


@app.route('/getActiveUsers')
def getActiveUsers():
    if current_user.is_authenticated:

        
        return connection.getActiveUsers()
    else:
        return "please login"

@app.route('/getInactiveUsers')
def getInactiveUsers():
    if current_user.is_authenticated:

        
        return connection.getInactiveUsers()
    else:
        return "please login"

@app.route('/getAllGroups')
def getAllGroups():
    if current_user.is_authenticated:

        
        return connection.getAllGroups()
    else:
        return "please login"


@app.route('/createGroup')
def createGroup():
    if current_user.is_authenticated:
        
        return connection.createGroup(request.args.get('name'))
    else:
        return "please login"
    



@app.route('/getAllFromGroup')
def getAllFromGroup():
    if current_user.is_authenticated:
        
        return connection.getAllFromGroup(request.args.get('name'))
    else:
        return "please login"


@app.route('/getAllUserGroups')
def getAllUserGroups():
    if current_user.is_authenticated:
        
        return connection.getAllUserGroups(request.args.get('username'))
    else:
        return "please login"

    

@app.route('/addUserToGroup')
def addUserToGroup():
    if current_user.is_authenticated:
        
        return connection.addUserToGroup(request.args.get('groupname'),request.args.get('username'),request.args.get('permission'))
    else:
        return "please login"



@app.route('/getPermissionInGroup')
def getPermissionInGroup():
    if current_user.is_authenticated:
        
        return connection.getPermissionInGroup(request.args.get('groupname'),request.args.get('permission'))
    else:
        return "please login"


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

#@app.errorhandler(500)
#def internal_error(error):
    
#    print(error)
#    return "Error: Invalid values entered"    
    
    
if __name__ == '__main__':
    app.run()

