# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash
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

@app.route('/reboot', methods=['GET', 'POST'])
def reboot():
    subprocess.call(['shutdown', '-r', 'now'])

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)