#!/usr/bin/ipython -i

from time import sleep
import ow
import RPi.GPIO as GPIO

from ina219 import INA219

relp = 4

b01B = 
b02B = 
b03B = 
b04B = 
b05B = 
b06B = 
b07B = 
b08B = 
b09B = 
b10B = 
b11B = 
b12B = 
b13B = 

b13L = 20

devA = "3a-00000027df7e"
devB = "3a-000000345822"
devC = "3a-0000003458ac"

oost = '\x00'
ofst = '\x01'
fost = '\x02'
ffst = '\x03'

dt = 0.50

ow.init('localhost:4304')

mysensors = ow.Sensor("/uncached").sensorList()

GPIO.setmode(GPIO.BCM)
GPIO.setup(relp, GPIO.OUT)
GPIO.setup(b13L, GPIO.OUT)
GPIO.output(relp, True)
GPIO.output(b13L, True)

ina = INA219(shunt_ohms=0.025, max_expected_amps=12.0, address=0x40)
ina.configure(voltage_range=ina.RANGE_32V, gain=ina.GAIN_AUTO, 
	bus_adc=ina.ADC_128SAMP, shunt_adc=ina.ADC_128SAMP)

s1 = ow.Sensor("/3A.AC5834000000")
s2 = ow.Sensor("/3A.AC5834000000")

def switchState(_dev, _state):
    f = open(opath + _dev + "/output", 'wb')
    f.write(_state)
    f.close()

class powerMeter:
    def __init__(self):
        self.oldcur = ina.current()

    def show(self):
        sleep(0.30)
        curcur = ina.current()
        print( '%.3f'%ina.voltage() + ' V   ' 
                + '%.1f'%curcur 
                + " mA   (diff " 
                + '%.1f'%(curcur-self.oldcur) 
                + " mA)" )
        self.oldcur = curcur

class bus:
    def __init__()

class valve:
    def __init__(self, _pio_handle, _button, _light, ):
        self._res = 1500


#while True:
#for i in range(0,5):
#    GPIO.output(relp, True)
#    for s in mysensors:
        #s.PIO_A = str( int( not bool( s.PIO_A ) ) )
        #s.PIO_B = str( int( not bool( s.PIO_B ) ) )
#        s.PIO_A = '1'
#        s.PIO_B = '0'
#        sleep(dt)
#        s.PIO_A = '0'
#        s.PIO_B = '1'
#        sleep(dt)
#        print("swap " + s.address )
#    sleep(dt)
#    GPIO.output(relp, False)
#    sleep(dt)

dt = 0.1

pm = powerMeter()

for i in range(0,30):
    pm.show()
    GPIO.output(relp, True)
    print "bus    on "
    pm.show()

    sleep(5)

    for s in mysensors:
        s.PIO_A = '1'
        pm.show()
        sleep(dt)
        s.PIO_B = '1'
        pm.show()
        sleep(dt)

    sleep(1.0)
    print "valves on "
    sleep(1.0)
    
    for s in mysensors:
        s.PIO_A = '0'
        pm.show()
        sleep(dt)
        s.PIO_B = '0'
        pm.show()
        sleep(dt)
    print "valves off"
    GPIO.output(relp, False)
    print "bus    off"
    pm.show()
    sleep(dt)


