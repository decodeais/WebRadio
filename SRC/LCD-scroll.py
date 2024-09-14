from RPLCD.i2c import CharLCD
from time import sleep
import os
from mpd import MPDClient, ConnectionError
from datetime import datetime
import time
import os
import RPi.GPIO as GPIO

# Konfiguration der GPIO-Pins
BUTTON_PINS = {
    14: 'prev',       # B1
    15: 'toggle',     # B2
    16: 'playlist',   # Neue Taste für Playlist-Auswahl
    18: 'next',       # B3
    23: 'radio',      # B4
    24: 'music',      # B5
    25: 'random'      # B6
}


# Benutzerdefinierte Zeichen definieren
play_icon = [
    0b10000,
    0b11000,
    0b11100,
    0b11110,
    0b11110,
    0b11100,
    0b11000,
    0b10000
]

pause_icon = [
    0b11011,
    0b11011,
    0b11011,
    0b11011,
    0b11011,
    0b11011,
    0b11011,
    0b11011
]

stop_icon = [
    0b00000,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b00000
]

random_icon = [
    0b00010,
    0b10111,
    0b01010,
    0b01000,
    0b01000,
    0b01010,
    0b10111,
    0b00010
]
volume_icon = [
    0b00000,
    0b00000,
    0b00001,
    0b00011,
    0b00111,
    0b01111,
    0b11111,
    0b00000
]




DEFAULT_PLAYLIST_FILE = "/home/pi/default_playlist.txt"
LONG_PRESS_DURATION = 1.0  # Dauer in Sekunden für langes Drücken

# MPD-Client einrichten
client = MPDClient()
client.timeout = 60
client.idletimeout = None

def wait_for_mpd(host='localhost', port=6600, timeout=60):
    client = MPDClient()
    start_time = time.time()

    while True:
        try:
            client.connect(host, port)
            print("MPD-Dienst ist gestartet.")
            client.close()
            client.disconnect()
            break  # Verlasse die Schleife, wenn die Verbindung erfolgreich war
        except ConnectionError:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(f"MPD-Dienst konnte nicht innerhalb von {timeout} Sekunden erreicht werden.")
                break
            print("Warte auf den Start des MPD-Dienstes...")
            time.sleep(0.5)  # Warte 5 Sekunden, bevor ein neuer Versuch gestartet wird

def connect_client():
    try:
        client.connect("localhost", 6600)
    except Exception as e:
        print(f"MPD connection error: {e}")
        time.sleep(5)  # Warten, bevor ein neuer Verbindungsversuch gestartet wird
        connect_client()

def reconnect_client():
    try:
        client.close()
        client.disconnect()
    except:
        pass
    finally:
        connect_client()

def handle_button_press(channel):
    global playlist_mode, current_playlist_index, line_2, line_3, saved_default, playlist_started
    #if saved_default: sleep(2)
    button_press_start_time[channel] = time.time()
    press_duration = 0
    # Polling, um die Dauer des Tastendrucks zu messen
    while GPIO.input(channel) == GPIO.LOW and press_duration < LONG_PRESS_DURATION:
        time.sleep(0.01)  # Kurze Verzögerung
        press_duration = time.time() - button_press_start_time[channel]
        print(f"duration: {press_duration}")
    if press_duration >= LONG_PRESS_DURATION:
        if channel == 24 and playlist_mode:  # Langer Druck im Playlist-Modus
            if playlists:
                line_3 = "Standard gespeichert"
                default_playlist = playlists[current_playlist_index]
                with open(DEFAULT_PLAYLIST_FILE, "w") as file:
                    file.write(default_playlist)
               # playlist_mode = False
                saved_default = True
                print(f"Die ausgewählte Playlist '{default_playlist}' wurde als Standard-Playlist gespeichert.")
                
    else:
        if playlist_mode:
            if channel == 16:  # Playlist mode beenden
                playlist_mode = False
                print("Playlist-Auswahlmodus deaktiviert.")
            elif channel == 14:  # B1 - prev
                current_playlist_index = (current_playlist_index - 1) % len(playlists)
                line_2 =playlists[current_playlist_index]
                print(f"Ausgewählte Playlist: {playlists[current_playlist_index]}")
            elif channel == 18:  # B3 - next
                current_playlist_index = (current_playlist_index + 1) % len(playlists)
                line_2 = playlists[current_playlist_index]
                print(f"Ausgewählte Playlist: {playlists[current_playlist_index]}")
            elif channel == 15:  # B2 - toggle play/stop oder Playlist bestätigen
                try:
                    client.clear()
                    client.load(playlists[current_playlist_index])
                    client.play()
                    playlist_started = True
                    #playlist_mode = False
                    line_3 = "Playlist gestartet"
                    print(f"Playlist {playlists[current_playlist_index]} wird abgespielt.")
                except Exception as e:
                    print(f"Fehler beim Bestätigen der default Musik Playlist: {e}")
                    reconnect_client()
        else:
            if channel == 14:  # B1 - prev
                try:
                    client.previous()
                    print("prev Taste ")
                except Exception as e:
                    print(f"Fehler beim betätigen der prev Taste: {e}")
                    reconnect_client()
            
            elif channel == 15:  # B2 - toggle play/stop
                try:
                    client.pause()
                    print("play/pause Taste ")
                except Exception as e:    
                    print(f"Fehler beim betätigen der play/pause Taste: {e}")
                    reconnect_client()
            elif channel == 16:  # Neue Taste - Playlist auswählen
                playlist_mode = True

                print("Playlist-Auswahlmodus aktiviert.")
                if playlists:
                    line_2 =playlists[current_playlist_index]
                    print(f"Erste Playlist: {playlists[current_playlist_index]}")
                else:
                    print("Keine Playlists verfügbar.")
            elif channel == 18:  # B3 - next
                try:
                    print("next Taste ")
                    client.next()
                except Exception as e:
                    print(f"Fehler beim betätigen der next Taste: {e}")
                    reconnect_client()
                    
            elif channel == 23:  # B4 - Radio
                try:
                    print("Radio Taste ")
                  #  sleep(1)
                    client.clear()
                    client.load("MyRadio")
                    client.consume(0)
                    client.play()
                except Exception as e:
                    print(f"Fehler beim betätigen der Radio Taste: {e}")
                    reconnect_client()    
            elif channel == 24:  # B5 - Music
                if os.path.exists(DEFAULT_PLAYLIST_FILE):
                    try:
                        with open(DEFAULT_PLAYLIST_FILE, "r") as file:
                            default_playlist = file.read().strip()
                        if default_playlist in playlists:
                            try:
                                print("Musik Taste")
                                client.clear()
                                client.load(default_playlist)
                                client.consume(0)
                                client.play()
                                print(f"Playlist {default_playlist} wird abgespielt.")
                            except Exception as e:
                                print(f"Fehler beim Umschalten auf default Musik Playlist: {e}")
                                reconnect_client()
                        else:
                            try:
                                print("Standard-Playlist ist nicht verfügbar, lade 'MyMusic'.")
                                client.clear()
                                client.load("MyMusic")
                                client.consume(0)
                                client.play()
                            except Exception as e:
                                print(f"Fehler beim Umschalten auf Fallback MyMusic: {e}")
                                reconnect_client()
                    except Exception as e:
                        try:
                            print(f"Fehler beim Laden der Standard-Playlist: {e}")
                            client.clear()
                            client.load("MyMusic")
                            client.consume(0)
                            client.play()
                            print("Fehler beim Laden der Standard-Playlist, lade 'MyMusic'.")
                        except Exception as e:
                            print(f"Fehler beim Umschalten der auf Fallback da Datei fehlt: {e}")
                            reconnect_client()
                else:
                    print("Keine Standard-Playlist gefunden, lade 'MyMusic'.")
                    try:
                        client.clear()
                        client.load("MyMusic")
                        client.consume(0)
                        client.play()
                    except Exception as e:
                        print(f"Fehler beim Umschalten der Zufallswiedergabe: {e}")
                        reconnect_client()
            elif channel == 25:  # B6 - Random
                try:
                    status = client.status()
                    random = status.get('random') == '1'
                    if random: 
                        client.random(0)
                        print("random off")
                    else: 
                        client.random(1)
                        print("random on")
                except Exception as e:
                    print(f"Fehler beim Umschalten der Zufallswiedergabe: {e}")
                    reconnect_client()
            else:
                print(f"Unbekannter GPIO-Pin: {channel}")

def scroll_texts(lcd, client, cols, scroll_delay=0.25):
    # Scrollt die Texte gleichzeitig, kürzere Texte pausieren, bis der längste fertig gescrollt ist.
    line_0 = line_1 = line_2 =""
    try:
        status = client.status()
        current_song = client.currentsong()
    except ConnectionError:
        return  # Verbindung verloren, zurückkehren

    elapsed = status.get('elapsed','')
    elapsed_time = format_time(elapsed)  # Vergangene Zei

  #  random = status.get('random') == '1'                  # Überprüfen, ob 'random' aktiviert ist
    
    time = current_song.get('time', '')
    total_time = format_time(time)  # Titel länge
    
    
    # Album, Titel und Künstler extrahieren
    artist = current_song.get('artist', '')
    album = current_song.get('album', '')
    title = current_song.get('title', '')
    name = current_song.get('name', '')    

    prev_artist, prev_album, prev_title, prev_name = artist, album, title, name

    max_length = max(len(artist), len(album), len(title), len(name))
    
    wait_begin=10
    wait_end=10
    max_i = max_length - cols + 1 + wait_end+wait_begin
    
    for n in range(max_i):
        if n>wait_begin:
            i = n - wait_begin
        else:
            i = 0

        current_song = client.currentsong()
        artist = current_song.get('artist', '')
        album = current_song.get('album', '')
        title = current_song.get('title', '')
        name = current_song.get('name', '')  
        track = current_song.get('track', '')
        
        status = client.status()
        elapsed = status.get('elapsed','')
        volume = status.get('volume','')
        state = status.get('state','')
        random = status.get('random') == '1'                  # Überprüfen, ob 'random' aktiviert ist
    
        elapsed_time = format_time(elapsed)  # Vergangene Zeit 
    
       

        # Holen des aktuellen Datums und der Uhrzeit
        now = datetime.now()
        date_time_string = now.strftime("%d.%m.%Y %H:%M:%S")

        # Informationen ausgeben 

        if artist:  line_0 = artist
        else:       line_0 = date_time_string   
        if name:    line_1 = name
        if album:   line_1 = album
        if track:   line_2 = f"{track}: {title}"
        else:       line_2 = title


        if len(line_0) > cols + i - 1 or n == 0:
            lcd.cursor_pos = (0, 0)
            lcd.write_string(line_0[i:i + cols].ljust(cols))
            print(line_0)

        if len(line_1) > cols + i - 1 or n == 0: 
            lcd.cursor_pos = (1, 0)
            lcd.write_string(line_1[i:i + cols].ljust(cols))
            print(line_1)
            
        if len(line_2) > cols + i - 1 or n == 0:
            lcd.cursor_pos = (2, 0)
            lcd.write_string(line_2[i:i + cols].ljust(cols))
            print(line_2)

        lcd.cursor_pos = (3, 0)
        lcd.write_string(f'\x04{volume.rjust(3)}')
        lcd.cursor_pos = (3, 4)
        
        if random:
            lcd.write_string('\x03 ')
        else:
            lcd.write_string('  ')
        
        lcd.cursor_pos = (3, 6)
        if time :
            lcd.write_string(f'{elapsed_time}/{total_time}')
        else:
            lcd.write_string(f'{elapsed_time}        ')
            
        lcd.cursor_pos = (3, 19)
        lcd.write_string({'play': '\x00', 'pause': '\x01', 'stop': '\x02'}.get(state.lower(), ''))

        if (artist, album, title, name) != (prev_artist, prev_album, prev_title, prev_name) or playlist_mode:
            return
        prev_artist, prev_album, prev_title, prev_name = artist, album, title, name
        sleep(scroll_delay)
        


def format_time(time_string):
    try:
        total_seconds = int(float(time_string))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"
    except ValueError:
        return "00:00"
        
line_2 = ""    
line_3 = ""
saved_default = False
playlist_started = False

def main():
    global playlist_mode, current_playlist_index, playlists, button_press_start_time, line_2, line_3
    global saved_default, playlist_started
    GPIO.cleanup()  # Freigeben aller GPIO-Pins zu Beginn
    playlist_mode = False
    current_playlist_index = 0
    button_press_start_time = {}

    # GPIO einrichten
    GPIO.setmode(GPIO.BCM)
    
    for pin in BUTTON_PINS.keys():
        try:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=handle_button_press, bouncetime=300)
        except RuntimeError as e:
            print(f"Fehler bei der Konfiguration von GPIO {pin}: {e}")

    # LCD einrichten
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=20, rows=4, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)
    # Benutzerdefinierte Zeichen auf den LCD hochladen
    lcd.create_char(0, play_icon)
    lcd.create_char(1, pause_icon)
    lcd.create_char(2, stop_icon)
    lcd.create_char(3, random_icon)
    lcd.create_char(4, volume_icon)

    # Warten auf MPD-Dienst
    wait_for_mpd()
    
    connect_client()
    prev_playlist_mode = False
    

    try:
        playlists = client.listplaylists()
        playlists = [pl['playlist'] for pl in playlists]
        line_3 = "                    "
        while True:
            print(f"playlist_mode:{playlist_mode}/saved_default:{saved_default}/playlist_started:{playlist_started}")
            if playlist_mode:
                
                # lcd.clear() - Falls benötigt, um den Bildschirm zu löschen
                #line_3 = "                    "
                lcd.cursor_pos = (0, 0)
                lcd.write_string("choose playlist      ")
                lcd.cursor_pos = (1, 0)
                lcd.write_string("                     ")
                lcd.cursor_pos = (2, 0)
                lcd.write_string(line_2.ljust(20))
                lcd.cursor_pos = (3, 0)
                lcd.write_string(line_3)
                if saved_default or playlist_started:
                    print("playlist loop ended")
                    lcd.cursor_pos = (3, 0)
                    lcd.write_string(line_3)
                  #  sleep(2)
                    print("sleep")
                #else:
                if not saved_default and not playlist_started:
                    line_3 = "                    "
                    start_time = time.time()
                elapsed_time = time.time() - start_time
                print(elapsed_time)
                if  elapsed_time > 3: 
                    playlist_mode = False  # Zurücksetzen nach Ausführung
                    saved_default = False
                    playlist_started = False
                    line_3 = "                    "
                           
            
            else: 
                
                scroll_texts(lcd, client, 20)
            sleep(0.2)  # Kurz warten, bevor der nächste Schleifendurchgang beginnt

    except KeyboardInterrupt:
        print("Programm wird beendet...")

    except KeyboardInterrupt:
        print("Programm wird beendet...")
    finally:
        GPIO.cleanup()  # GPIO-Pins beim Beenden des Programms freigeben
        client.close()
        client.disconnect()

if __name__ == "__main__":
    main()
