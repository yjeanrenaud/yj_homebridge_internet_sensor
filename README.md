# yj_homebridge_internet_sensor
A small python script to monitor the local internet connection and expose a HTTP server for [homebridge](https://github.com/homebridge/homebridge) and other smart home applications.
It checks the status of your internet connection by pinging one or several hosts repeatedly.

# prerequisites
This programme relies on python 3.
No special modules needed. 
# setup
out of my lazyness, you must simply change the values according to your needs within the py-file, where you specify the port for the local HTTP-server that puts out the status of your internet connection (`0` for bad, `1` for good) and an array of tuples with descriptions and and hosts to ping for. You may use full qualified domain names or IPv4  addresses, even IPv6 is possible.
```
pairsOfHosts = [
    ('router', '192.168.1.1'),
    ('cf dns', '1.1.1.1'),
    ('pocketpc.ch', 'pocketpc.ch')
]
port = 99 #any port available on your host running this script
```
you may also specify the port as argument to the script, e.g. 
`python3 yj_homebridge_internet_sensor.py 99`
# usage
just runn the script by 
`python3 yj_homebridge_internet_sensor.py` or, if you whish `chmod a+x`and then `.\yj_homebridge_internet_sensor.py`
you may also use cron to run it automatically at system start in a `screen` (install screen first via `sudo apt-get update && sudo apt-get install screen`
`$crontab -e`
and insert the following line at the end:
`@reboot screen -dmS yjhbinets python3 /FULL/PATH/TO/SCRIPT/yj_homebridge_internet_sensor.py`
obviously, you may also supply the script with the port for the HTTP server to be used as an envriomental argument here:
`@reboot screen -dmS yjhbinets python3 /FULL/PATH/TO/SCRIPT/yj_homebridge_internet_sensor.py 99`

# Apple HomeKit / Smart Home integration
If you want to use it in your Apple HomeKit smart home, use [homebridge](https://www.homebridge.org) and the [homebridge-http-contact-sensor plugin](https://github.com/cyakimov/homebridge-http-contact-sensor).
There, the config should look somehwat like this
```
{
    "accessory": "ContactSensor",
    "name": "Internet",
    "pollInterval": 120000,
    "_comment_": "2 mins in milliseonds",
    "statusUrl": "http://192.168.1.3:99"
}
```
where the `status-url` obiously contains the IP address (or the hostname) of the machine running this script and the port you speficied.
That's it! It's registered as a contact sensor within HomeKit thereafter. Therefore, you may use this to alert you on your iOS device when your home network is without connection to the internet via HomeKit. Of course, you may use this new contact sensor now also for other automatisations. But bear in mind, you may not trigger a Wifi socket to restart your router when your internet connection is down if it relies on the cloud.

# todos
- clean up the code
- get rid of some debug rubbish
