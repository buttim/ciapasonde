#!/usr/bin/python

import time
import bluezutils
import traceback
import dbus
import dbus.service
import dbus.mainloop.glib
import RPi.GPIO as GPIO
from gi.repository import GLib
from display import Display


GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button1=False
button2=False

def onButton2(channel):
  global button2
  button2=True

def onButton1(channel):
  global button1
  button1=True

GPIO.add_event_detect(5, GPIO.FALLING, callback=onButton1, bouncetime=200)
GPIO.add_event_detect(6, GPIO.FALLING, callback=onButton2, bouncetime=200)


BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'

def buttonInput():
  global button1, button2
  button1=False
  button2=False
  while not button1 and not button2:
    time.sleep(2)
    print(".")
  print(button1,button2)
  return button1 

def ask(prompt1,prompt2,button1,button2):
  try:
    disp.ask(prompt1,prompt2,button1,button2)
    return buttonInput()
  except Exception as e:
    traceback.print_exc()
  
def set_trusted(path):
  props = dbus.Interface(bus.get_object("org.bluez", path),
          "org.freedesktop.DBus.Properties")
  props.Set("org.bluez.Device1", "Trusted", True)
    
class Agent(dbus.service.Object):
  exit_on_release = True

  def set_exit_on_release(self, exit_on_release):
    self.exit_on_release = exit_on_release

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="", out_signature="")
  def Release(self):
    print("Release")
    if self.exit_on_release:
      mainloop.quit()

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="os", out_signature="")
  def AuthorizeService(self, device, uuid):
    print("AuthorizeService (%s, %s)" % (device, uuid))
    authorize = ask("Authorize connection?","",'yes','no')
    if (authorize == "yes"):
      return
    raise Rejected("Connection rejected by user")

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="o", out_signature="s")
  def RequestPinCode(self, device):
    print("RequestPinCode (%s)" % (device))
    set_trusted(device)
    return ask("Enter PIN Code: ","",'yes','no')

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="o", out_signature="u")
  def RequestPasskey(self, device):
    #TODO
    print("RequestPasskey (%s)" % (device))
    set_trusted(device)
    passkey = ask("Enter passkey: ","",'yes','no')
    return dbus.UInt32(passkey)

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="ouq", out_signature="")
  def DisplayPasskey(self, device, passkey, entered):
    #TODO
    print("DisplayPasskey (%s, %06u entered %u)" %
            (device, passkey, entered))

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="os", out_signature="")
  def DisplayPinCode(self, device, pincode):
    print("DisplayPinCode (%s, %s)" % (device, pincode))

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="ou", out_signature="")
  def RequestConfirmation(self, device, passkey):
    print("RequestConfirmation (%s, %06d)" % (device, passkey))
    confirm = ask("Confirm passkey?",str(passkey),'yes','no')
    try:
      if confirm:
        print("OK")
        set_trusted(device)
        return
    except Exception:
      traceback.print_exc()
    disp.update()
    raise Rejected("Passkey doesn't match")

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="o", out_signature="")
  def RequestAuthorization(self, device):
    print("RequestAuthorization (%s)" % (device))
    auth = ask("Authorize?","",'yes','no')
    if (auth == "yes"):
      return
    raise Rejected("Pairing rejected")

  @dbus.service.method(AGENT_INTERFACE,
          in_signature="", out_signature="")
  def Cancel(self):
    #TODO
    print("Cancel")

disp=Display()
path = "/test/agent"
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

adapter_path = bluezutils.find_adapter('').object_path
adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path),
          "org.freedesktop.DBus.Properties")
adapter.Set("org.bluez.Adapter1", "Discoverable", True)         
mac=adapter.Get("org.bluez.Adapter1", "Address")
adapter.Set("org.bluez.Adapter1", "Alias",'CiapaSonde'+mac.replace(':',''))

agent = Agent(bus, path)
capability='KeyboardDisplay'

mainloop = GLib.MainLoop()

obj = bus.get_object(BUS_NAME, "/org/bluez");
manager = dbus.Interface(obj, "org.bluez.AgentManager1")
manager.RegisterAgent(path, capability)
manager.RequestDefaultAgent(path)
mainloop = GLib.MainLoop()
try:
  mainloop.run()
except KeyboardInterrupt:
  disp.close()
