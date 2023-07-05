cd ~pi/ciapasonde
if [ ! -p sondepipe ]
then
  mkfifo sondepipe
fi
if [ ! -p logpipe ]
then
  mkfifo logpipe
fi
rtl_tcp -d 0 -a 127.0.0.1 -p 1234 -g 0 -b 20 -P 0 &
~pi/dxlAPRS/out/sdrtst -c sdr_config.txt -t 127.0.0.1:1234 -r 25000 -k -v -s sondepipe &
~pi/dxlAPRS/out/sondeudp -f 25000 -l 128 -c 0 -o sondepipe -I MYCALL-11 -v -n 0 -S 3 -u 127.0.0.1:4000 >> logpipe &
./ciapasonde.py >>log.txt &
