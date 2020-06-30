# Setup Raspberry Pi Router and Flask Web Server GUI

To install the required dependencies, run
```
pip3 install -r requirements.txt
```
The web server is running continuously as a Linux service, so the webserver can be found at <routerIPAddress>:8080 on a local browser while connected to the local Pi network. 

### Instructions for Converting Raspberry Pi to Access Point
Access point instructions adapted from:  
 https://raspberrypi.stackexchange.com/questions/89803/access-point-as-wifi-router-repeater-optional-with-bridge/89804#89804

#### Step 1: setup systemd-networkd
```
# deinstall classic networking
pi@raspberrypi:~ $ sudo -Es   # if not already done
root@raspberrypi:~ # apt --autoremove purge ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
root@raspberrypi:~ # apt-mark hold ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog raspberrypi-net-mods openresolv
root@raspberrypi:~ # rm -r /etc/network /etc/dhcp

# setup/enable systemd-resolved and systemd-networkd
root@raspberrypi:~ # apt --autoremove purge avahi-daemon
root@raspberrypi:~ # apt-mark hold avahi-daemon libnss-mdns
root@raspberrypi:~ # apt install libnss-resolve
root@raspberrypi:~ # ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
root@raspberrypi:~ # systemctl enable systemd-networkd.service systemd-resolved.service
```
#### Step 2: install hostapd for the access point
Note: Set ssid to be name of the new network being created, and wpa_passphrase to be the password for the new network being created.
```
rpi ~# vim /etc/hostapd/hostapd.conf
interface=ap0
driver=nl80211
ssid=pi-network
country_code=DE
hw_mode=g
channel=1
auth_algs=1
wpa=2
wpa_passphrase=password
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

rpi ~# chmod 600 /etc/hostapd/hostapd.conf
```
Edit the hostapd.service:
```
rpi ~# systemctl --full edit hostapd.service
```
Comment the "After=network.target" line as so:
```
#After=network.target
```
Save and quit vim. Next add interface ap0 to the hostapd.service with:
```
rpi ~# systemctl edit hostapd.service
```
In the empty editor insert these statements. Pay attention to the minus sign after equal =- on some statements. Save it and quit the editor:
```
[Unit]
Wants=wpa_supplicant@wlan0.service

[Service]
Restart=
Restart=no
ExecStartPre=/sbin/iw dev wlan0 interface add ap0 type __ap
ExecStopPost=-/sbin/iw dev ap0 del
```
The first Restart= is important and not a typo. This is used to clear the original Restart=yes in the main unit (not seen here in the drop in file) before setting it to Restart=no again.

#### Step 3: setup wpa_supplicant for client connection
Create this file with your settings for country=, ssid= and psk= and enable it (Note: this should be the network the Raspberry Pi is being tethered to):
```
rpi ~# vim /etc/wpa_supplicant/wpa_supplicant-wlan0.conf 
country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="TestNet"
    psk="realyNotMyPassword"
    key_mgmt=WPA-PSK   # see ref (4)
}

rpi ~# chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
rpi ~# systemctl disable wpa_supplicant.service
rpi ~# systemctl enable wpa_supplicant@wlan0.service
rpi ~# rfkill unblock 0
```
Extend wpa_supplicant with:
```
rpi ~# systemctl edit wpa_supplicant@wlan0.service
```
In the empty editor insert these statements. Save it and quit the editor:
```
[Unit]
BindsTo=hostapd.service
After=hostapd.service
```
#### Step 4: setup static interfaces
Create these files:
```
rpi ~# vim /etc/systemd/network/08-wlan0.network 
[Match]
Name=wlan0
[Network]
DNSSEC=no
# If you need a static ip address, then toggle commenting next four lines (example)
DHCP=yes
#Address=192.168.50.60/24
#Gateway=192.168.50.1
#DNS=84.200.69.80 1.1.1.1
```
```
rpi ~# vim /etc/systemd/network/12-ap0.network 
[Match]
Name=ap0
[Network]
DNSSEC=no
IPMasquerade=yes
Address=192.168.4.1/24
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
```
Then reboot. Then your router/repeater should be visible to your devices!  
Next, clone this repo to install a Flask-powered web server to edit the network configurations.


