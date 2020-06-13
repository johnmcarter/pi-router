# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session
import subprocess
import os

# create the application object
app = Flask(__name__)
app.secret_key = "super secret key"
app.config["DEBUG"] = True
username = 'pi'
password = 'pennylane'

# use decorators to link the function to a url
@app.route("/", methods=["GET", "POST"])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        config_file = open("/etc/hostapd/hostapd.conf", "r")
        credentials = config_file.readlines()
        #credentials = check_output(['./get_network_credentials.sh']).decode('utf-8')
        return render_template("index.html", credentials=credentials)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != username or request.form['password'] != password:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    filename = "/etc/hostapd/hostapd.conf"
    config_file = open(filename, "r")
    credentials = config_file.readlines()
    current_ssid = credentials[2].strip("\n").split("ssid=")[1]
    current_password = credentials[8].strip("\n").split("wpa_passphrase=")[1]
    print("Current SSID:", current_ssid)
    print("Current Password:", current_password)

    if request.method == "POST":
        setting = request.form.get('setting')
        new_val = request.form.get('new_value')
        if setting == "ssid" and new_val != None:
            subprocess.call(['sed', '-i', 's/ssid=%s/ssid=%s/' % (current_ssid, new_val),
                 filename])
        elif setting == "password" and new_val != None:
            new_val = request.form.get('new_value')
            
    # Display new settings
    config_file = open(filename, "r")
    credentials = config_file.readlines()
    new_ssid = credentials[2].strip("\n").split("ssid=")[1]
    new_password = credentials[8].strip("\n").split("wpa_passphrase=")[1]
    print("New SSID:", new_ssid)
    print("New Password:", new_password)
    return render_template('edit.html', credentials=credentials)


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)