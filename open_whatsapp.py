from time import sleep
from WhatsApp import WhatsApp


firefox_profile_path = 'some path'
gecko_path = 'some path'

    
whatsapp = WhatsApp(firefox_profile_path, gecko_path)

while True:
    try:
        sleep(0.1)
    except KeyboardInterrupt:
        print('quitting whatsapp')
        break

whatsapp.__del__()
