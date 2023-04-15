from machine import *
import socket
import math
import utime
import network
import time
import dht
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("HP-PRINT-69420","totallylegitprinter")
 
 
#Pin Mapping
#GPIO 10 - DHT11
#GPIO 26 - Photoresistor
#GPIO 11 - RGB LED - Red
#GPIO 12 - RGB LED - Green
#GPIO 13 - RGB LED - Blue
#GPIO 6  - White LED


class Stuff:
    def __init__(self):      
        self.temp = 69
        self.hum = 42
        self.light = 86
        
        
    def read(cls):
        sensor = dht.DHT11(Pin(10))
        sensor.measure()
        cls.temp = sensor.temperature()
        cls.temp = (cls.temp * 9/5) + 32 #Convert from C to F
        cls.hum = sensor.humidity()
        cls.temp = '%.2f'%cls.temp
        cls.hum = '%.0f'%cls.hum
        
        photoRes = ADC(Pin(26))
        cls.light = photoRes.read_u16()
        cls.light = round(cls.light/65535*100,2)
        
        return cls


# rgb led
red=machine.Pin(13,machine.Pin.OUT)
green=machine.Pin(14,machine.Pin.OUT)
blue=machine.Pin(15,machine.Pin.OUT)

white=machine.Pin(6,machine.Pin.OUT)
 
# Wait for connect or fail
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)
 
# Temperature Sensor
#sensor_temp = machine.ADC(4)
#conversion_factor = 3.3 / (65535)
 
#def temperature():
#    sensor.measure()
#    temp = sensor.temperature()
#    hum = sensor.humidity()
    
#    return 
#    temperature_value = sensor_temp.read_u16() * conversion_factor 
#    temperature_Celcius = 27 - (temperature_value - 0.706)/0.00172169/ 8 
#    print(temperature_Celcius)
#    utime.sleep(2)
#    return temperature_Celcius
 
def webpage(values):
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
            
            <meta http-equiv="refresh" content="10">
            <p align = "center">Temperature is {values.temp}°F</p>
            <p align = "center">Humidity is {values.hum}%</p>
            <p align = "center">Brightness at {values.light}%</p>
            </body>
            </html>
            """
    return html
 
def serve(connection):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        print(request)
        

        values = Stuff()
        values = Stuff.read(values)
        #value='%.2f'%temperature()    
        html=webpage(values)
    
        client.send(html)
        client.close()
        
        print("Temp is %f.", float(values.temp))
        
        if float(values.temp) > 75:
            print("Red")
            red.value(1)
            green.value(0)
            blue.value(0)
        elif float(values.temp) < 65:
            print("Blue")
            red.value(0)
            green.value(0)
            blue.value(1)
        else:
            print("Green")
            red.value(0)
            green.value(1)
            blue.value(0)
        
        if int(values.light) > 17:
            white.value(0)
        else:
            white.value(1)
 
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return(connection)
 
 
try:
    if ip is not None:
        connection=open_socket(ip)
        serve(connection)
except KeyboardInterrupt:
    machine.reset()