#!/usr/bin/python

import ST7735
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import RPi.GPIO as GPIO
import time


button1=False
button2=False

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
      rst=24,
      dc=25,
      backlight=23,
      rotation=270,
      spi_speed_hz=4000000,
      invert=False,
      offset_left=0,
      offset_top=0,
      width=128,
      height=160
    )
    self.disp.begin()
    self.img = Image.new('RGB', (self.disp.width,self.disp.height), color=(0, 255, 0))

    self.draw = ImageDraw.Draw(self.img)

    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    self.fontSmall = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    button1=False
    button2=False

    GPIO.add_event_detect(5, GPIO.FALLING, callback=onButton1, bouncetime=200)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=onButton2, bouncetime=200)

    self.ip='?.?.?.?'
    self.id='????????'
    self.type='RS41'
    self.freq=403.0
    self.lat=0
    self.lng=0
    self.alt=0
    self.connected=False
    self.asking=False

  def update(self):
    if self.asking: return
    self.draw.rectangle((0, 0, self.disp.width, self.disp.height), fill=(0, 0, 255))
    self.draw.text((5,0),f"{self.id}",font=self.font,fill=(0,0,0))
    self.draw.text((5,20),f"{self.type}@{self.freq}",font=self.font,fill=(0,0,0))
    self.draw.text((5,40),f"{self.lat}",font=self.font,fill=(0,0,0))
    self.draw.text((5,55),f"{self.lng}",font=self.font,fill=(0,0,0))
    self.draw.text((5,75),f"{self.alt}m",font=self.font,fill=(0,0,0))
    self.draw.text((5,115),f"IP {self.ip}     {'(BT)' if self.connected else ''}",font=self.fontSmall,fill=(0,0,0))
    self.disp.display(self.img)

  def ask(self,prompt1,prompt2,button1,button2):
    self.asking=True
    self.draw.rectangle((0, 0, self.disp.width, self.disp.height), fill=(0, 255, 255))
    self.draw.text((5,45),prompt1,font=self.fontSmall,fill=(0,0,0))
    self.draw.text((5,65),prompt2,font=self.font,fill=(0,0,0))
    w,h=self.draw.textsize(button1,self.font)
    self.draw.text((self.disp.width-w-4,20-h/2),button1,font=self.font,fill=(0,0,0))
    w,h=self.draw.textsize(button2,self.font)
    self.draw.text((self.disp.width-w-4,self.disp.height-20-h/2),button2,font=self.font,fill=(0,0,0))
    self.disp.display(self.img)
    res = buttonInput()
    self.asking=False
    return res

  def testButton2(self):
    global button2
    res=button2
    button2=False
    return res

  def close(self):
    self.disp.reset();
    GPIO.output(23, GPIO.LOW)
    GPIO.cleanup()
