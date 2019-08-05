from ina219 import INA219
import ExpanderPi as EPi

from time import sleep
import ow


# setting up the INA219
ina = INA219(shunt_ohms=0.025, max_expected_amps=12.0, address=0x40)
ina.configure(voltage_range=ina.RANGE_32V, gain=ina.GAIN_AUTO, 
	bus_adc=ina.ADC_128SAMP, shunt_adc=ina.ADC_128SAMP)

class PowerMeter:
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

class Leds:
	def __init__(self):
		self._io = EPi.IO()
		for i in range(1,13):
			self._io.set_pin_direction(i,0)

		self._ledmap = [4,3,2,1,12,11,6,5,10,9,8,7]
		self._led_callback = [self._falseDummy for i in range(12)]

	def on(self,_i):
		self._io.write_pin(self._ledmap[_i],1)

	def off(self,_i):
		self._io.write_pin(self._ledmap[_i],0)

	def set(self,_i,_state):
		self._io.write_pin(self._ledmap[_i],int(_state))

	def toggle(self,_i):
		_pin = self._ledmap[_i]
		self._io.write_pin(_pin, int(not bool(self._io.read_pin(_pin))))

	def regCallback(self,_i,_func):
		self._led_callback[_i] = _func

	def sync(self):
		for i in range(0,12):
			self.set(i,self._led_callback[i]())

	def _falseDummy(self):
		return False

class OneWireGPIO:
	def __init__(self, _address, _attr, _pm):
#	def __init__(self, _address, _attr):
		self._sensor = ow.Sensor(_address)
		self._attr = _attr
		self._pm = _pm

		self._fulladdress = _address + "/" + _attr

		# initialize as off
		self._commanded = False
		self._set(False)

		# amount of retries
		self._retries = 4

	def on(self):
		self._commanded = True
		self.sync()

	def off(self):
		self._commanded = False
		self.sync()

	def toggle(self):
		self._commanded = not self._commanded
		self.sync()

	def state(self):
		return self._commanded

	def _get(self):
		_val = self._sensor.__getattr__(self._attr)
		if _val == '1':
			return True
		else:
			return False

	def _set(self,_val):
		_valstr = '0'
		if _val:
		    _valstr = '1'

                # first attempt to set state
		self._sensor.__setattr__(self._attr,_valstr)
                
                # check if correct state has been set
		if self._get() == _val:
			return True
		else:
			retries = self._retries

			while(retries > 0):
				sleep(0.1)
				print("retry nr " + str(retries))
				self._sensor.__setattr__(self._attr,_valstr)
				sleep(0.1)
				if self._get() == _val:
				    return True
				sleep(0.3)
				retries -= 1
			print("setting valve failed")
			return False


	def sync(self):
		curstate = self._get()
		if self._commanded is not curstate:
			print("not in commanded state, setting to " + str(self._commanded))
			self._set(self._commanded)
			self._pm.show()