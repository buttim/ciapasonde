#!/usr/bin/python

import time, signal, serial, threading, logging, socket
from display import Display
from buzzer import Buzzer
from enum import Enum


class TipoSonda(Enum):
  RS41=1
  M20=2
  M10=3
  PIL=4
  DFM=5
  C50=6

def stop(signum, frame):
  disp.close()
  logging.info('Ciapasonde stopped')
  exit(0)

signal.signal(signal.SIGTERM, stop)

ver='CIAPA-0.0'
type=1
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

def get_local_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    # doesn't even have to be reachable
    s.connect(('192.255.255.255', 1))
    IP = s.getsockname()[0]
  except:
    IP = '127.0.0.1'
  finally:
    s.close()
  return IP
 
def getSDRconfig(tipo,freq):
  if tipo==TipoSonda.DFM:
    return f'f {freq} 5 65 0 6000'
  elif tipo==TipoSonda.M10:
    #With M10 reception, it is essential to increase the sample rate for sdrtst and sondeudp to at least 20000Hz!
    return f'f {freq} 8 80 0 20000'
  else:
    return f'f {freq} 5 70 0 12000'


def btMessage():
  global type, freq, snr, bat, batv, mute, ver, lat, lng, alt, vel
  if id=='':
    return f'0/{TipoSonda(type).name}/{freq}/{snr}/{bat}/{batv}/{1 if mute else 0}/{ver}/o\r\n'
  else:
    sign=0
    afc=0
    bk=0
    bktime=0
    if lat==0 and lng==0:
      return f'2/{TipoSonda(type).name}/{freq}/{id}/S{snr}/{bat}/{afc}/{batv}/{1 if mute else 0}/0/0/0/{ver}/o\r\n'
    else:
      return f'1/{TipoSonda(type).name}/{freq}/{id}/{lat}/{lng}/{alt}/{vel}/{snr}/{bat}/{afc}/{bk}/{bktime}/{batv}/{1 if mute else 0}/0/0/0/{ver}/o\r\n'

def writeSDRconfig():
  global type, freq
  with open('sdr_config.txt','w') as file:
      file.write(f'#{TipoSonda(type).name}\r\n')
      file.write(getSDRconfig(type,freq)+'\r\n')


def readSDRconfig():
  global type, freq
  try:
    with open('sdr_config.txt','r') as file:
      s=file.readline().strip()
      type=TipoSonda[s[1:]].value
      s=file.readline().strip()
      freq=float(s.split(' ')[1])
  except:
    type=1
    freq=403.0

def process(s):
    global freq,type,mute,ver
    
    s=s.strip()
    if not s.startswith('o{'):
        return ''
    if not s.endswith('}o'):
        return ''
    s=s[2:-2]
    a=s.split('/')
    for cmd in a:
      if cmd=='?':
        return f'3/{TipoSonda(type).name}/{freq}/0/0/0/0/0/0/0/0/0/CIAPA/0/0/0/0/0/0/0/0/{ver}/o\r\n'
      c=cmd.split('=')
      if len(c)!=2:
          logging.warning('Malformed command "'+cmd+'"')
      else:
        if c[0]=='tipo':
          try:
            type=int(c[1])
            disp.type=TipoSonda(type).name
            disp.update()
            logging.debug('New type: '+str(type))
            writeSDRconfig()
          except:
            logging.warning('Bad argument for t command ('+c[1]+')')
        elif c[0]=='f':
          try:
            freq=float(c[1])
            logging.debug('New frequency: '+str(freq))
            disp.freq=str(freq)
            disp.update()
            writeSDRconfig()
          except:
              logging.warning('Bad argument for f command ('+c[1]+')')
        elif c[0]=='mute':
          mute=c[1]=='1'
          logging.debug(f'Mute: {mute}')
        else:
          logging.warning(f'Unrecognized command "{c[0]}"')
    return ''
    
def threadFunc():
  connected=False
  while True:
    try:
        with serial.Serial("/dev/rfcomm0",115200,timeout=1) as ser:
          logging.info('Serial connected')
          disp.connected=True
          disp.update()
          connected=True
          ser.timeout=1
          while True:
            line=ser.readline()
            if line:
                s=line.decode('utf-8').strip()
                logging.debug('Received: '+s)
                s=process(s)
                if s!='':
                    ser.write(s.encode('utf-8'))
            else:
              time.sleep(1)
            ser.write(btMessage().encode('utf-8'))
    except serial.SerialException:
      if connected:
        connected=False
        disp.connected=False
        disp.update()
        logging.info("Serial disconnected")
      time.sleep(1)
      disp.ip=get_local_ip()
      disp.update()

readSDRconfig()

disp=Display()
disp.ip=get_local_ip()
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
        logging.warning('errore analisi: '+line.strip())
except KeyboardInterrupt:
  stop(0,0)
