import time
import threading
import RPi.GPIO as GPIO


class Buzzer:
	def __init__(self,pin):
		self.pin=pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
		self.buzzer = GPIO.PWM(pin, 1000)

	def stop(self):
		time.sleep(0.1)
		self.buzzer.stop()
		
	def beep(self):
		self.buzzer.start(50)
		self.thread=threading.Thread(target=self.stop)
		self.thread.start()
