#!/usr/bin/python

import ST7735
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import RPi.GPIO as GPIO
import time


class Display:
  def __init__(self):
    self.disp=ST7735.ST7735(
      port=0,
      cs=0,
      rst=24,
      dc=25,
      backlight=23,
      rotation=90,
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

    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    self.fontSmall = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

    self.ip='?.?.?.?'
    self.id='????????'
    self.lat=0
    self.lng=0
    self.alt=0

  def update(self):
    self.draw.rectangle((0, 0, self.disp.width, self.disp.height), fill=(0, 0, 255))
    self.draw.text((10,0),f"{self.id}",font=self.font,fill=(0,0,0))
    self.draw.text((20,25),f"{self.lat}",font=self.font,fill=(0,0,0))
    self.draw.text((20,45),f"{self.lng}",font=self.font,fill=(0,0,0))
    self.draw.text((20,70),f"{self.alt}m",font=self.font,fill=(0,0,0))
    self.draw.text((5,110),f"IP {self.ip}",font=self.fontSmall,fill=(0,0,0))
    self.disp.display(self.img)

  def close(self):
    self.disp.reset();
    GPIO.output(23, GPIO.LOW)
