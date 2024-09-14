from RPLCD.i2c import CharLCD
# LCD mit passender I2C-Adresse initialisieren (bitte Adresse anpassen)
lcd = CharLCD('PCF8574', 0x27)
# Display löschen
lcd.clear()
# Optional: Display ausschalten
lcd.backlight_enabled = False
