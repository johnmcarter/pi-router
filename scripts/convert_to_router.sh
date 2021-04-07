# John Carter
# Script to turn a Raspberry Pi into a Router/Repeater
# NOTE: Script must be run as sudo

grn=$'\e[1;32m'
end=$'\e[0m'

echo "[${grn}INFO${end}] Deinstall classic networking"
apt --autoremove purge ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
apt-mark hold ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog raspberrypi-net-mods openresolv
rm -r /etc/network /etc/dhcp

echo "[${grn}INFO${end}] Setup/enable systemd-resolved and systemd-networkd"
apt --autoremove purge avahi-daemon
apt-mark hold avahi-daemon libnss-mdns
apt install libnss-resolve
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
systemctl enable systemd-networkd.service systemd-resolved.service

echo "[${grn}INFO${end}] Install hostapd and start service"

cat > /etc/hostapd/hostapd.conf << EOF
driver=nl80211
ssid=RPiNet
country_code=DE
hw_mode=g
channel=1
auth_algs=1
wpa=2
wpa_passphrase=verySecretPassword
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

chmod 600 /etc/hostapd/hostapd.conf
systemctl --full edit hostapd.service

cat > hostapd.service << EOF
[Unit]
Wants=wpa_supplicant@wlan0.service

[Service]
Restart=
Restart=no
ExecStartPre=/sbin/iw dev wlan0 interface add ap0 type __ap
ExecStopPost=-/sbin/iw dev ap0 del
EOF

echo "[${grn}INFO${end}] Setup wpa_supplicant for client connection"
cat > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf << EOF
country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="TestNet"
    psk="realyNotMyPassword"
    key_mgmt=WPA-PSK   # see ref (4)
}
EOF

chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
systemctl disable wpa_supplicant.service
systemctl enable wpa_supplicant@wlan0.service
rfkill unblock 0

cat > wpa_supplicant@wlan0.service << EOF
[Unit]
BindsTo=hostapd.service
After=hostapd.service
EOF

echo "[${grn}INFO${end}] Setup static interfaces"
cat > /etc/systemd/network/08-wlan0.network << EOF
[Match]
Name=wlan0
[Network]
DNSSEC=no
# If you need a static ip address, then toggle commenting next four lines (example)
DHCP=yes
#Address=192.168.50.60/24
#Gateway=192.168.50.1
#DNS=84.200.69.80 1.1.1.1
EOF

cat > /etc/systemd/network/12-ap0.network << EOF
[Match]
Name=ap0
[Network]
DNSSEC=no
IPMasquerade=yes
Address=192.168.4.1/24
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
EOF

echo "[${grn}INFO${end}] Reboot"
reboot