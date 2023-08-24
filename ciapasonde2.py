#!/usr/bin/python

import os, time, signal, serial, threading, logging, socket, math
from subprocess import *
from display import Display
from buzzer import Buzzer
from enum import Enum
from bt import startBTThread

class TipoSonda(Enum):
  RS41=1
  M20=2
  M10=3
  PIL=4
  DFM=5
  C50=6
  
def sondedumpType(t):
    if t==2 or t==3 or t==4: return 'm10'
    if t==5: return 'dfm'
    if t==6: return 'c50'
    return 'rs41'

def stop(signum, frame):
  disp.close()
  logging.info('Ciapasonde stopped')
  exit(0)

signal.signal(signal.SIGTERM, stop)

ver='CIAPA-2.0'
type=6
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
restart=False

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
 
def btMessage():
  global type, freq, snr, bat, batv, mute, ver, lat, lng, alt, vel, id
  if id=='':
    return f'0/{TipoSonda(type).name}/{freq}/{snr}/{bat}/{batv}/{1 if mute else 0}/{ver}/o\r\n'
  else:
    sign=0
    afc=0
    bk=0
    bktime=0
    if lat==0 and lng==0:
        id=''
        return f'2/{TipoSonda(type).name}/{freq}/{id}/S{snr}/{bat}/{afc}/{batv}/{1 if mute else 0}/0/0/0/{ver}/o\r\n'
    else:
        id=''
        return f'1/{TipoSonda(type).name}/{freq}/{id}/{lat}/{lng}/{alt}/{vel}/{snr}/{bat}/{afc}/{bk}/{bktime}/{batv}/{1 if mute else 0}/0/0/0/{ver}/o\r\n'

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
            #TODO writeSDRconfig()
          except:
            logging.warning('Bad argument for t command ('+c[1]+')')
        elif c[0]=='f':
          try:
            freq=float(c[1])
            logging.debug('New frequency: '+str(freq))
            disp.freq=str(freq)
            disp.update()
            restart=True
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
    if disp.testButton2():
      if disp.ask('Shutdown?','','yes','no'):
        os.system('sudo shutdown 0 &')
        disp.ask('','SHUTDOWN','','')
    try:
        with serial.Serial("/dev/rfcomm0",115200,timeout=1) as ser:
          logging.info('Serial connected')
          disp.connected=True
          disp.update()
          connected=True
          ser.timeout=1
          while True:
            if disp.testButton2():
              if disp.ask('Shutdown?','','yes','no'):
                os.system('sudo shutdown 0 &')
                disp.ask('','SHUTDOWN','','')
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
        time.sleep(.2)
        disp.ip=get_local_ip()
        disp.update()

disp=Display()
disp.freq=freq
disp.type=TipoSonda(type).name
disp.ip=get_local_ip()
disp.update()

logging.basicConfig(format="%(asctime)s: %(message)s",level=logging.INFO,datefmt="%H:%M:%S")
thread=threading.Thread(target=threadFunc,daemon=True)
thread.start()

buzzer=Buzzer(12)

startBTThread(disp)

try:
    while True:
        try:
            with open('freq.txt','r') as f:
                freq=float(f.read().rstrip())
        except:
            freq=405.95
        disp.freq=freq
        disp.update()
        logging.info(f'freq: {freq}')

        proc1=Popen(f"rtl_fm -f {freq}M | ffmpeg -f s16le -ar 24000 -ac 1 -i - -y fm.wav 2> /dev/null",shell=True)
        with Popen(["stdbuf","-o0","sondedump","-t",sondedumpType(type),"-f","#%S %l %o %a %c %f","fm.wav"],encoding='utf8',bufsize=0,stdout=PIPE) as proc:
            logging.info('Ciapasonde started')
            while not restart:
                line=proc.stdout.readline()
                if not line: break
                try:
                    logging.info(line)
                    a=line.split()
                    id=a[0].lstrip('#')
                    disp.id=id
                    frame=a[5]
                    lat=float(a[1][:-1])
                    lng=float(a[2][:-1])
                    alt=float(a[3].replace('m',''))
                    logging.info(f'id={id} frame={frame} lat={lat} lng={lng} alt={alt}')
                    if math.isnan(lat) or math.isnan(lng) or math.isnan(alt) or lat==0 or lng==0: continue
                    try:
                        disp.lat=lat
                        disp.lng=lng
                        disp.alt=alt
                        disp.update()
                    except Exception as ex:
                        pass
                    if not mute:
                        buzzer.beep()
                except Exception as ex:
                    logging.warning('errore analisi: '+str(ex)+'['+line.strip()+']')
                print(line.rstrip())
            proc1.kill()
            restart=False

except KeyboardInterrupt:
  stop(0,0)