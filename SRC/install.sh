# Schreiben des Displays und Tastaturabfrage
cp LCD-scroll.py /home/pi/LCD-scroll.py

# Löschen des Displayinhalts
cp shutdown_service.py /home/pi/shutdown_service.py

# Kopieren der Einstellungen für die Services
sudo cp LCD.service /etc/systemd/system/LCD.service
sudo cp shutdown_script.service /etc/systemd/system/shutdown_script.service

# Services aktivieren
sudo systemctl daemon-reload
sudo systemctl enable LCD.service
sudo systemctl enable shutdown_script.service

# Konfiguration für das Ein-/Ausschalten über Taster
sudo sh -c 'echo "gpio=27=op,dl" >> /boot/config.txt'
sudo sh -c 'echo "dtoverlay=gpio-shutdown,gpio_pin=17,active_low=\"y\"" >> /boot/config.txt'


# Raspberry Pi 40-Pin GPIO Header
#
#  LCD  (+)           3V3  (1)   (2)   5V
#  LCD (SDA)        GPIO2  (3)   (4)   5V
#  LCD (SCL)        GPIO3  (5)   (6)   GND
#                   GPIO4  (7)   (8)   GPIO14        Button1 (prev)
#  LCD (Gnd)          GND  (9)   (10)  GPIO15        Button2 (toggle)
#  Vol (SW)        GPIO17  (11)  (12)  GPIO18        Button3 (next)
#  Button (disable)GPIO27  (13)  (14)  GND           Button  (Gnd)
#                  GPIO22  (15)  (16)  GPIO23        Button4 (radio)
#  Vol (+)            3V3  (17)  (18)  GPIO24        Button5 (music)
#                  GPIO10  (19)  (20)  GND
#                   GPIO9  (21)  (22)  GPIO25        Button6 (random)
#                  GPIO11  (23)  (24)  GPIO8
#  Vol (Gnd)          GND  (25)  (26)  GPIO7
#                   GPIO0  (27)  (28)  GPIO1
#  Vol (DT)         GPIO5  (29)  (30)  GND
#  Vol (CLK)        GPIO6  (31)  (32)  GPIO12
#                  GPIO13  (33)  (34)  GND
#                  GPIO19  (35)  (36)  GPIO16        Button7 (playlist)
#                  GPIO26  (37)  (38)  GPIO20
#                     GND  (39)  (40)  GPIO21

# LED (On) an GPIO 17
# Run Testpad
#

#