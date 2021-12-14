#!/bin/bash

# Author: John Carter
# Created: 2021/07/25 16:59:27
# Last modified: 2021/08/22 14:00:52
# Setup script to creater access point capabilities
# Tested on a Raspberry Pi 3 and a Raspberry Pi 4
# https://raspberrypi.stackexchange.com/questions/89803/access-point-as-wifi-router-repeater-optional-with-bridge/89804#89804

GRN=$'\e[1;32m'
RED=$'\e[1;31m'
END=$'\e[0m'


if (( EUID != 0 )); then
   echo "[${RED}ERROR${END}] This script must be run as root" 
   exit 1
fi

if [[ $# -ne 3 ]]; then
    echo "[${RED}ERROR${END}] USAGE: $0 <tethered network> <tethered network password> <pi-network password>" 
   exit 1
fi

echo "[${GRN}INFO${END}] Installing hostapd"
apt install hostapd

echo "[${GRN}INFO${END}] Deinstalling classic networking"
systemctl daemon-reload
systemctl disable --now ifupdown dhcpcd dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
apt --autoremove purge ifupdown dhcpcd dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
rm -r /etc/network /etc/dhcp

echo "[${GRN}INFO${END}] Setup/enable systemd-resolved and systemd-networkd"
systemctl disable --now avahi-daemon libnss-mdns
apt --autoremove purge avahi-daemon
apt install libnss-resolve
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
apt-mark hold avahi-daemon dhcpcd dhcpcd5 ifupdown isc-dhcp-client isc-dhcp-common libnss-mdns openresolv raspberrypi-net-mods rsyslog
systemctl enable systemd-networkd.service systemd-resolved.service

echo "[${GRN}INFO${END}] Creating hostapd conf file"

cat > /etc/hostapd/hostapd.conf <<EOF
driver=nl80211
ssid=pi-network
country_code=US
hw_mode=g
channel=1
auth_algs=1
wpa=2
wpa_passphrase=$3
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

chmod 600 /etc/hostapd/hostapd.conf

cat > /etc/systemd/system/accesspoint@.service <<EOF
[Unit]
Description=accesspoint with hostapd (interface-specific version)
Wants=wpa_supplicant@%i.service

[Service]
ExecStartPre=/sbin/iw dev %i interface add ap@%i type __ap
ExecStart=/usr/sbin/hostapd -i ap@%i /etc/hostapd/hostapd.conf
ExecStopPost=-/sbin/iw dev ap@%i del

[Install]
WantedBy=sys-subsystem-net-devices-%i.device
EOF

systemctl enable accesspoint@wlan0.service
rfkill unblock wlan


echo "[${GRN}INFO${END}] Creating WPA Supplicant conf file"
cat > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf <<EOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="$1"
    psk="$2"
    key_mgmt=WPA-PSK   # see ref (4)
}
EOF

chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
systemctl disable wpa_supplicant.service

cat > /etc/systemd/system/wpa_supplicant@wlan0.service <<EOF
[Unit]
Description=WPA supplicant daemon (interface-specific version)
Requires=sys-subsystem-net-devices-%i.device
After=sys-subsystem-net-devices-%i.device
Before=network.target
Wants=network.target
[Service]
Type=simple
ExecStart=/sbin/wpa_supplicant -c/etc/wpa_supplicant/wpa_supplicant-%I.conf -Dnl80211,wext -i%I

[Install]
Alias=multi-user.target.wants/wpa_supplicant@%i.service
EOF


echo "[${GRN}INFO${END}] Setting up static interfaces"
cat > /etc/systemd/network/08-wifi.network <<EOF
[Match]
Name=wl*
[Network]
LLMNR=no
MulticastDNS=yes
# If you need a static ip address, then toggle commenting next four lines (example)
DHCP=yes
#Address=192.168.50.60/24
#Gateway=192.168.50.1
#DNS=84.200.69.80 1.1.1.1
EOF

cat > /etc/systemd/network/12-ap.network <<EOF
[Match]
Name=ap@*
[Network]
LLMNR=no
MulticastDNS=yes
IPMasquerade=yes
Address=192.168.4.1/24
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
EOF

echo "[${GRN}INFO${END}] Setting up DNS using systemd"
cat > /etc/systemd/resolved.conf <<EOF
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
# Entries in this file show the compile time defaults.
# You can change settings by editing this file.
# Defaults can be restored by simply deleting this file.
#
# See resolved.conf(5) for details

[Resolve]
DNS=192.168.1.1
FallbackDNS=1.1.1.1 9.9.9.10 8.8.8.8 2606:4700:4700::1111 2620:fe::10 2001:4860$
#Domains=
#LLMNR=yes
#MulticastDNS=yes
DNSSEC=allow-downgrade
DNSSEC=no
#DNSOverTLS=no
#Cache=yes
#DNSStubListener=udp
EOF

echo "[${GRN}INFO${END}] Changing hostname to pirouter"
cat > /etc/hostname <<EOF
pirouter
EOF

echo "[${GRN}INFO${END}] Setup is finished. Reboot to see changes!"
