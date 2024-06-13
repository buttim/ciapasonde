#!/usr/bin/python

import ST7735, time, threading
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import RPi.GPIO as GPIO


HAT=0
if HAT:
  OFFSET_LEFT=2
  OFFSET_TOP=3
  RST=27
  DC=25
  BACKLIGHT=24
  ROTATION=90
  WIDTH=128
  HEIGHT=128
  BTN1=21
  BTN2=20
  BTN3=16
  PRESS=13 #joystick
  LEFT=5
  UP=6
  RIGHT=26
  DOWN=19
else:
  OFFSET_LEFT=0
  OFFSET_TOP=0
  RST=24
  DC=25
  BACKLIGHT=23
  ROTATION=270
  WIDTH=128
  HEIGHT=160
  BTN1=5
  BTN2=6
  BTN3=-1

button1=False
button2=False
button3=False

def onButton3(channel):
  global button3
  button3=True

def onButton2(channel):
  global button2
  button2=True

def onButton1(channel):
  global button1
  button1=True

def buttonInput():
  global button1, button2
  button1=False
  button2=False
  while not button1 and not button2:
    time.sleep(.2)
  return button1 

class Display:
  def __init__(self):
    self.disp=ST7735.ST7735(
      port=0,
      cs=0,
      rst=RST,
      dc=DC,
      backlight=BACKLIGHT,
      rotation=ROTATION,
      spi_speed_hz=4000000,
      invert=False,
      offset_left=OFFSET_LEFT,
      offset_top=OFFSET_TOP,
      width=WIDTH,
      height=HEIGHT
    )
    self.disp.begin()
    self.img = Image.new('RGB', (self.disp.width,self.disp.height), color=(0, 0, 255))

    self.draw = ImageDraw.Draw(self.img)

    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    self.fontSmall = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if BTN3>=0:
      GPIO.setup(BTN3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    button1=False
    button2=False
    button3=False

    GPIO.add_event_detect(BTN1, GPIO.FALLING, callback=onButton1, bouncetime=200)
    GPIO.add_event_detect(BTN2, GPIO.FALLING, callback=onButton2, bouncetime=200)
    if BTN3>=0:
      GPIO.add_event_detect(BTN3, GPIO.FALLING, callback=onButton3, bouncetime=200)

    self.ip='?.?.?.?'
    self.id='????????'
    self.btMac='????'
    self.type='RS41'
    self.freq=403.0
    self.lat=0
    self.lng=0
    self.alt=0
    self.connected=False
    self.lock=threading.Lock()
    self.asking=False

  def update(self):
    if self.asking: return
    self.lock.acquire()
    self.draw.rectangle((0, 0, self.disp.width, self.disp.height), fill=(0,255,255))
    self.draw.text((5,0),f"{self.id}",font=self.font,fill=(0,0,0))
    self.draw.text((5,20),f"{self.type}@{self.freq}",font=self.font,fill=(0,0,0))
    self.draw.text((5,40),f"{self.lat}",font=self.font,fill=(0,0,0))
    self.draw.text((5,55),f"{self.lng}",font=self.font,fill=(0,0,0))
    self.draw.text((5,75),f"{self.alt}m",font=self.font,fill=(0,0,0))
    self.draw.text((5,105),f"BT {self.btMac}",font=self.fontSmall,fill=(0,0,0))
    self.draw.text((5,115),f"IP {self.ip}  {'(BT)' if self.connected else ''}",font=self.fontSmall,fill=(0,0,0))
    try:
      self.disp.display(self.img)
    except:
      pass
    self.lock.release()
    
  def ask(self,prompt1,prompt2,txtButton1,txtButton2):
    global button1, button2

    self.asking=True
    self.draw.rectangle((0, 0, self.disp.width, self.disp.height), fill=(255, 255, 0))
    self.draw.text((5,45),prompt1,font=self.fontSmall,fill=(0,0,0))
    self.draw.text((5,65),prompt2,font=self.font,fill=(0,0,0))
    w=self.draw.textlength(txtButton1,self.font)
    h=16
    self.draw.text((self.disp.width-w-4,20-h/2),txtButton1,font=self.font,fill=(0,0,0))
    w=self.draw.textlength(txtButton2,self.font)
    h=16
    self.draw.text((self.disp.width-w-4,self.disp.height-20-h/2),txtButton2,font=self.font,fill=(0,0,0))
    self.disp.display(self.img)
    res = buttonInput()
    self.asking=False
    button1=False
    button2=False
    button3=False
    return res

  def testButton3(self):
    global button3
    res=button3
    button3=False
    return res

  def testButton2(self):
    global button2
    res=button2
    button2=False
    return res

  def close(self):
    self.disp.reset()
    GPIO.setup(BACKLIGHT,GPIO.OUT)
    GPIO.output(BACKLIGHT, GPIO.LOW)
