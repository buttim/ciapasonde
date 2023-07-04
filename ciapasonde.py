#!/usr/bin/python

import time
import serial
import threading
import logging
from display import Display
from buzzer import Buzzer

ver='CIAPA-0.0'
type='RS41'
freq=403.7
bat=0
batv=0
mute=False

id=''
lat=0
lng=0
alt=0
vel=0
clb=0
volt=0
snr=0

def btMessage():
    if id=='':
        return f'0/{type}/{freq}/{snr}/{bat}/{batv}/{1 if mute else 0}/{ver}/o\r\n'
    else:
        sign=0
        afc=0
        bk=0
        bktime=0
        if lat==0 and lng==0:
            return f'2/{type}/{freq}/{id}/S{snr}/{bat}/{afc}/{batv}/{1 if mute else 0}/0/0/0/{ver}/o\r\n'
        else:
            return f'1/{type}/{freq}/{id}/{lat}/{lng}/{alt}/{vel}/{snr}/{bat}/{afc}/{bk}/{bktime}/{batv}/{1 if mute else 0}/0/0/0/{ver}/o\r\n'

def process(s):
    global freq
    global type
    global mute
    
    s=s.strip()
    if not s.startswith('o{'):
        return ''
    if not s.endswith('}o'):
        return ''
    s=s[2:-2]
    a=s.split('/')
    for cmd in a:
        c=cmd.split('=')
        if len(c)!=2:
            logging.warning('malformed command "'+cmd+'"')
        else:
            if c[0]=='tipo':
                pass    # TODO
            elif c[0]=='f':
                try:
                    freq=float(c[1])
                    with open('sdr_config.txt','w') as file:
                        file.write(f'f {freq} 10 0 70 12000\n')
                    logging.info('New frequency: '+str(freq))
                except:
                    logging.warning('bad argument for f command ('+c[1]+')')
            elif c[0]=='mute':
                mute=c[1]=='1'
                logging.info(f'Mute: {mute}')
            else:
                logging.warning(f'Unrecognized command "{c[0]}"')
    return ''
    
def threadFunc():
  connected=False
  while True:
    try:
        with serial.Serial("/dev/rfcomm0",115200,timeout=1) as ser:
          logging.info('Serial connected')
          connected=True
          ser.timeout=1
          while True:
            line=ser.readline()
            if line:
                s=line.decode('utf-8').strip()
                logging.info('Received: '+s)
                s=process(s)
                if s!='':
                    ser.write(s.encode('utf-8'))
            else:
              time.sleep(1)
            ser.write(btMessage().encode('utf-8'))
    except serial.SerialException:
      if connected:
        connected=False
        logging.info("Serial disconnected")
      time.sleep(1)

disp=Display()
disp.update()

logging.basicConfig(format="%(asctime)s: %(message)s",level=logging.INFO,datefmt="%H:%M:%S")
thread=threading.Thread(target=threadFunc,daemon=True)
thread.start()

buzzer=Buzzer(12)

try:
    with open('logpipe','r') as fifo:
      logging.info('Ciapasonde started')
      for line in fifo:
        try:
          a=line.split()
          id=a[1]
          frame=a[2]
          lat=a[5]
          lng=a[6]
          alt=a[7].replace('m','')
          vel=a[8].replace('km/h','')
          clb=a[10].replace('m/s','')
          v=a[12]
          snr=a[13].replace('dBm','')
          logging.info(f'id={id} frame={frame} lat={lat} lng={lng} alt={alt} vel={vel} clb={clb} v={v} snr={snr}')
          disp.lat=lat
          disp.lng=lng
          disp.id=id
          disp.alt=alt
          disp.update()
          if not mute:
            buzzer.beep()
        except:
          logging.info('errore analisi: '+line.strip())
except KeyboardInterrupt:
    logging.info('Ciapasonde stopped')