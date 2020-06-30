# Flask Web Server for Raspberry Pi Router

To install the required dependencies, run
```
pip3 install -r requirements.txt
```
The web server is running continuously as a Linux service, so the webserver can be found at 127.0.0.1:8080 on a local browser while connected to the local Pi network. 

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




