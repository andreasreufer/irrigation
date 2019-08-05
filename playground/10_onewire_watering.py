#!/usr/bin/ipython -i

from time import sleep
import ow
import RPi.GPIO as GPIO

import waterHelpers

from waterHelpers import PowerMeter, Leds, OneWireGPIO

import atexit

# setting up one-wire
ow.init('localhost:4304')

# bus power relay
relp = 4
b13L = 20
b12B = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(b13L, GPIO.OUT)
GPIO.output(b13L, True)


class WateringZone:
    def __init__(self, _gpio):
    	return

class Barrel:
    def __init__(self, _gpio_pump, _gpio_valve):
    	return


class OnewireWatering:
	def __init__(self):
		self._pm  = waterHelpers.PowerMeter()
		self._leds = waterHelpers.Leds()

		self._gpios = {}
		self._buttonCallbacks = {}

		ow.init('localhost:4304')
		self._sensors = ow.Sensor("/uncached").sensorList()

		self._buspower = False
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(relp, GPIO.OUT)

		self._regButton(16, self.togglePower)
		self._leds.regCallback(11, self.powerState)

		self._regButton(19, self.stop)


	# synchronize valve states and LEDs
	def _sync(self):
		# sync all valves
		for _gpio in self._gpios.values():
			_gpio.sync()

		# sync all LEDs
		self._leds.sync()
		return

	def _buttonHandler(self, _pin):
		print("interrupt on pin " + str(_pin))
		if _pin in self._buttonCallbacks:
			self._buttonCallbacks[_pin]()

		self._sync()

	def _regButton(self, _pin, _func):
		GPIO.setup(_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(_pin, GPIO.RISING, self._buttonHandler, bouncetime=500)
		self._buttonCallbacks[_pin] = _func

	def addGPIO(self, _name, _owaddr, _attr, _button = -1, _led = -1):
		curGPIO = OneWireGPIO(_owaddr, _attr, self._pm)
		#self._gpios[_name] = OneWireGPIO(_owaddr, _attr, self._pm)

		# wire LED to valve
		self._leds.regCallback(_led, curGPIO.state)

		# wire button to valve
		self._regButton(_button, curGPIO.toggle)

		# store GPIO object
		self._gpios[_name] = curGPIO

	def powerOn(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(relp, GPIO.OUT)
		GPIO.output(relp, True)

		self._buspower = True
		self._leds.sync()
		self._pm.show()

	def powerOff(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(relp, GPIO.OUT)
		GPIO.output(relp, False)

		self._buspower = False
		self._leds.sync()
		self._pm.show()

	def powerState(self):
		return self._buspower

	def togglePower(self):
		if self._buspower:
			self.powerOff()
		else:
			self.powerOn()

	def transfer(self,_source, _sink):
		return

	def stop(self):
		print("STOP!!! STOP!!! STOP!!!")
		self._leds.on(10)

		self.powerOff()
		self._leds.on(10)

		for _gpio in self._gpios.values():
			_gpio.off()
			self._leds.sync()
			self._leds.on(10)
	
		self._leds.off(10)

Watering = OnewireWatering()


# pump 1   3A.FE3034000000
# valve 1  3A.7EDF27000000
# valve 2  3A.AC5834000000
# valve 3  3A.225834000000
# pump 2   3A.983134000000
Watering.addGPIO("p1", "/3A.FE3034000000","PIO_B",18,7)
Watering.addGPIO("p2", "/3A.983134000000","PIO_B",12,8)

Watering.addGPIO("t1", "/3A.FE3034000000","PIO_A",17,6)
Watering.addGPIO("t2", "/3A.983134000000","PIO_A",13,9)

Watering.addGPIO("v1", "/3A.7EDF27000000","PIO_A",27,0)
Watering.addGPIO("v2", "/3A.7EDF27000000","PIO_B",22,1)
Watering.addGPIO("v3", "/3A.AC5834000000","PIO_A",23,2)
Watering.addGPIO("v4", "/3A.AC5834000000","PIO_B",24,3)
Watering.addGPIO("v5", "/3A.225834000000","PIO_A",5,4)
Watering.addGPIO("v6", "/3A.225834000000","PIO_B",6,5)



#t1 = Valve("/3A.FE3034000000","PIO_A")
#m1 = Valve("/3A.FE3034000000","PIO_B")

#v1 = Valve("/3A.7EDF27000000","PIO_A",pm)
#v2 = Valve("/3A.7EDF27000000","PIO_B",pm)
#v3 = Valve("/3A.AC5834000000","PIO_A",pm)
#v4 = Valve("/3A.AC5834000000","PIO_B",pm)
#v5 = Valve("/3A.225834000000","PIO_A",pm)
#v6 = Valve("/3A.225834000000","PIO_B",pm)

#t2 = Valve("/3A.983134000000","PIO_A",pm)
#m2 = Valve("/3A.983134000000","PIO_B",pm)

#valvesall = [v1,v2,v3,v4,v5,v6]

def getSensors():
    return ow.Sensor("/uncached").sensorList()

mysensors = getSensors()

def clean_up():
    GPIO.cleanup()
    print("bye!")
atexit.register(clean_up)

