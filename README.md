# Raspberry Pi WiFi Repeater/Router and Flask Web Server GUI

To install the required dependencies, run
```
pip3 install -r requirements.txt
```

The web server is running continuously as a Linux service, so the webserver can be found at the router's IP address on port 80 on a local browser while connected to the local Pi network. For instance, if you execute the script included in the repo, it can be found at http://192.168.4.1.