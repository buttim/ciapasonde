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

