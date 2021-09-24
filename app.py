'''
John Carter
Created: 2021/04/26 19:57:43
Last modified: 2021/09/23 22:02:18
Flask server for Pi-Router User Interface
'''

from flask import (Flask, g, render_template, redirect, url_for, 
                   request, session, flash)
from passlib.hash import pbkdf2_sha256
import subprocess
import os
import glob
import re

# Connect to user database
from db import Database
DATABASE_PATH = 'users.db'

app = Flask(__name__)
app.secret_key = "super secret key"

login_message = "Authentication required for this action"
CONF_FILE = "/etc/hostapd/hostapd.conf"


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
        credentials = get_credentials()
        devices = get_connected_devices()
        
        return render_template("index.html", name=name, 
                               credentials=credentials, 
                               devices=devices, images=update_images())
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
        credentials = get_credentials()
        if request.method == "POST":
            setting = request.form.get('setting')
            new_val = request.form.get('new_value')
            
            # Get current values
            if setting == "ssid":
                current_val = credentials[1].strip("\n").split("=")[1]
            elif setting == "password": 
                current_val = credentials[7].strip("\n").split("wpa_passphrase=")[1]

            # Update the desired setting and display changes
            if new_val:
                success_string = update_setting(setting, current_val, new_val)
                credentials = get_credentials()
                return render_template('edit.html', credentials=credentials, change=success_string)
                
        return render_template('edit.html', credentials=credentials)
    else:
        return render_template('login.html', message=login_message) 


@app.route('/network_health', methods=['GET', 'POST'])
def network_health():
    if 'user' in session:
        return render_template("network_health.html", images=update_images())
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


def update_images():
    # Copy newest graphs from malware detection repo and get list of names
    subprocess.call('cp -r /home/pi/malware_detection/figures/classification/5s/. static/img/malware_detection', shell=True)
    images = glob.glob("static/img/malware_detection/*")

    return images


def update_setting(setting, current_val, new_val):
    # Update a network setting
    rc = subprocess.call(['/usr/bin/sed', '-i', f's/{setting}={current_val}/{setting}={new_val}/', CONF_FILE])
    if rc == 0:
        return f"Success! Your {setting} was changed from {current_val} to {new_val}."
    else:
        return "Update process failed."
    
    return feedback


def get_connected_devices():
    # Get connected devices
    devices = []
    for device in os.popen('/usr/sbin/arp -a'): 
        device = device.split()
        device_name = device[0]
        IP = re.sub('[()]', '', device[1])
        MAC = device[3]
        interface = device[-1]
        devices.append([device_name, IP, MAC, interface]) 

    return devices


def get_credentials():
    # Get network settings
    config_file = open(CONF_FILE, "r")

    return config_file.readlines()


if __name__ == '__main__':
    app.run(host='0.0.0.0')