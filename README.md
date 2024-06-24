# A very simple temperature logger

Used together with a Telldus Duo running on a Raspberry Pi 4 with a 7" screen

# Started with: 
/etc/xdg/autostart/tempGUI.desktop   

[Desktop Entry]   
Type=Application   
Name=tempGUI   
Comment=temperatureLogg app   
NoDisplay=false   
Exec=/usr/bin/lxterminal -e /home/pi/PROJECTS/temperatureLogg/main.py   
NotShowIn=GNOME;KDE;XFCE;   
