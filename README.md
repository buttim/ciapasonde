<!-----

You have some errors, warnings, or alerts. If you are using reckless mode, turn it off to see inline alerts.
* ERRORs: 0
* WARNINGs: 0
* ALERTS: 1

Conversion time: 0.608 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β34
* Fri Jul 07 2023 01:31:45 GMT-0700 (PDT)
* Source doc: Ciapasonde
* This document has images: check for >>>>>  gd2md-html alert:  inline image link in generated source and store images to your server. NOTE: Images in exported zip file from Google Docs may not appear in  the same order as they do in your doc. Please check the images!

----->


<p style="color: red; font-weight: bold">>>>>>  gd2md-html alert:  ERRORs: 0; WARNINGs: 0; ALERTS: 1.</p>
<ul style="color: red; font-weight: bold"><li>See top comment block for details on ERRORs and WARNINGs. <li>In the converted Markdown or HTML, search for inline alerts that start with >>>>>  gd2md-html alert:  for specific instances that need correction.</ul>

<p style="color: red; font-weight: bold">Links to alert messages:</p><a href="#gdcalert1">alert1</a>

<p style="color: red; font-weight: bold">>>>>> PLEASE check and correct alert issues and delete this message and the inline alerts.<hr></p>



# Ciapasonde


## Configurazione Bluetooth

Modificare /etc/systemd/system/dbus-org.bluez.service

Trasformare:


```
ExecStart=/usr/lib/bluetooth/bluetoothd
```


in:


```
ExecStart=/usr/lib/bluetooth/bluetoothd -C
```


e aggiungere subito dopo


```
ExecStartPost=/usr/bin/sdptool add SP
```


In /etc/rc.local aggiungere prima di `exit 0`:


```
bluetoothctl discoverable-timeout 0
bluetoothctl discoverable on
sudo rfcomm watch hci0 &
sudo -u pi screen -S ciapa ~pi/ciapasonde/ciapasonde.py
```



## Software


```
    sudo apt install rtl-sdr git libx11-dev libxext-dev libpng-dev libjpeg-dev screen python3-pip libcairo2-dev libxt-dev libgirepository1.0-dev
    pip install st7735 pycairo PyGObject pyserial dbus-python
    git clone https://github.com/oe5hpm/dxlAPRS
    cd dxlAPRS/src
    make all
```



## Blacklist driver SDR

Creare /etc/modprobe.d/rtlsdr-blacklist.conf


```
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
blacklist dvb_usb_rtl2832u
blacklist dvb_usb_v2
blacklist dvb_core
```



## Installazione `ntmui `(opzionale - richiede monitor e tastiera)

[Installing Network Manager on Raspberry Pi OS - Pi My Life Up](https://pimylifeup.com/raspberry-pi-network-manager/)


## Connessione Raspberry TFT 1.8” 160x128 e buzzer

Abilitare SPI con sudo raspi-config (_3 Interface options / I4 SPI_)

                   3V3  (1) (2)  5V
                 GPIO2  (3) (4)  5V
                 GPIO3  (5) (6)  GND
                 GPIO4  (7) (8)  GPIO14
                   GND  (9) (10) GPIO15
                GPIO17 (11) (12) GPIO18
                GPIO27 (13) (14) GND
                GPIO22 (15) (16) GPIO23     LED
     VCC           3V3 (17) (18) GPIO24     RESET
     SDA        GPIO10 (19) (20) GND        GND
                 GPIO9 (21) (22) GPIO25     A0
     SCK        GPIO11 (23) (24) GPIO8      CS
                   GND (25) (26) GPIO7
                 GPIO0 (27) (28) GPIO1
                 GPIO5 (29) (30) GND
                 GPIO6 (31) (32) GPIO12     BUZZER+
                GPIO13 (33) (34) GND        BUZZER-
                GPIO19 (35) (36) GPIO16
                GPIO26 (37) (38) GPIO20
                   GND (39) (40) GPIO21

