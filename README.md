A very simple temperature logger.

Used together with a Telldus Duo

Started with: /etc/xdg/autostart/tempGUI.desktop
[Desktop Entry]
Type=Application
Name=tempGUI
Comment=temperatureLogg app
NoDisplay=false
Exec=/usr/bin/lxterminal -e /home/pi/PROJECTS/temperatureLogg/main.py
NotShowIn=GNOME;KDE;XFCE;

