# John Carter
# Flask Server for Router Interface
# June 2020
from flask import (Flask, g, render_template, redirect, url_for, 
                   request, session, flash)
from passlib.hash import pbkdf2_sha256
import subprocess
import os

# Connect to user database
from db import Database
DATABASE_PATH = 'users.db'

app = Flask(__name__)
app.secret_key = "super secret key"

login_message = "Login required for this action"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = Database(DATABASE_PATH)
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET", "POST"])
def home():
    if 'user' in session:
        name = session['user']['name']
        config_file = open("/etc/hostapd/hostapd.conf", "r")
        credentials = config_file.readlines()
        return render_template("index.html", credentials=credentials, name=name)
    else:
        return render_template('login.html') 
    
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        typed_password = request.form.get('password')
        if name and username and typed_password:
            encrypted_password = pbkdf2_sha256.hash(typed_password)
            get_db().create_user(name, username, encrypted_password)
            return redirect('/login')
    return render_template('create_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        typed_password = request.form.get('password')
        if username and typed_password:
            user = get_db().get_user(username)
            if user:
                if pbkdf2_sha256.verify(typed_password, user['encrypted_password']):
                    session['user'] = user
                    return redirect('/')
                else:
                    message = "Incorrect password, please try again"
            else:
                message = "Unknown user, please try again"
        elif username and not typed_password:
            message = "Missing password, please try again"
        elif not username and typed_password:
            message = "Missing username, please try again"
    return render_template('login.html', message=message)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user' in session:
        filename = "/etc/hostapd/hostapd.conf"
        config_file = open(filename, "r")
        credentials = config_file.readlines()
        current_ssid = credentials[2].strip("\n").split("ssid=")[1]
        current_password = credentials[8].strip("\n").split("wpa_passphrase=")[1]

        if request.method == "POST":
            change = ''
            setting = request.form.get('setting')
            new_val = request.form.get('new_value')
            # Update the SSID by calling subprocess
            if setting == "ssid" and new_val != None:
                subprocess.call(['sed', '-i', 's/ssid=%s/ssid=%s/' % (current_ssid, new_val),
                    filename])
                change = "Success! ssid was changed from {} to {}".format(current_ssid, new_val)
            # Update the password by calling subprocess
            elif setting == "password" and new_val != None:
                subprocess.call(['sed', '-i', 's/wpa_passphrase=%s/wpa_passphrase=%s/' 
                % (current_password, new_val), filename])
                change = "Success! password was changed from {} to {}".format(current_password, new_val)
                
            # Display new settings
            config_file = open(filename, "r")
            credentials = config_file.readlines()
            new_ssid = credentials[2].strip("\n").split("ssid=")[1]
            new_password = credentials[8].strip("\n").split("wpa_passphrase=")[1]
    
            if change:
                return render_template('edit.html', credentials=credentials, change=change)

        return render_template('edit.html', credentials=credentials)
    else:
        return render_template('login.html', message=login_message) 

@app.route('/reboot', methods=['GET', 'POST'])
def reboot():
    if 'user' in session:
        subprocess.call(['shutdown', '-r', 'now'])
    else:
        return render_template('login.html', message=login_message) 
         
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)