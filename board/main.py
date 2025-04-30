# main.py -- put your code here!
import pyb, uasyncio, utime
from heartbeat import Heartbeat
from sys import print_exception
from max31865 import PT1000
from thermostat import _PWM, Thermostat, PID

print('-- Booting uPyPL board --')

class Valve():

	def __init__(self, pin):
		self.pin = pin
	
	def state(self):
		return self.pin.value()

	def open(self):
		self.pin.value(1)
		pyb.LED(3).on()

	def close(self):
		self.pin.value(0)

	def toggle(self):
		self.pin.value(1 - self.pin.value())
        
class PyPL():

	def __init__(self, cycle = 0.01, separators = '\r;', status_cycle = 0.1, DEBUG = False):
  		self.DEBUG = DEBUG
  		self.heartbeat = Heartbeat()
  		self.serial = pyb.USB_VCP()
  		self.cycle = cycle
  		self.clock = 0
  		self.rbuf = ''
  		self.sep1, self.sep2 = separators
  		self.instructions = []
  		self.status_cycle = status_cycle
  		self.rtc = pyb.RTC()
        
        #Definition des pins pour les vannes et les capteurs
  		Y12 = pyb.Pin('Y12', pyb.Pin.OUT)   
  		Y4 = pyb.Pin('Y4', pyb.Pin.OUT)
  		X8 = pyb.Pin('X8', pyb.Pin.OUT)
  		X7 = pyb.Pin('X7', pyb.Pin.OUT)
  		X19 = pyb.Pin('X19', pyb.Pin.OUT)
  		X20 = pyb.Pin('X20', pyb.Pin.OUT)
          
        #Vannes
  		self.V1 = Valve(Y12)
  		self.V2 = Valve(X7)
  		self.V3 = Valve(X8)
  		self.V4 = Valve(Y4)
        
        #Capteurs de température
  		self.spi = pyb.SPI(2, mode = pyb.SPI.MASTER, baudrate = 10**7, phase = 1)
  		self.T1 = PT1000(self.spi, X19)
  		self.T2 = PT1000(self.spi, X20)
          
        #PID de température
#   		self.PWM = _PWM('Y3')
        
#   		self.PID_1 = PID(self.T1.read(),	self.PWM.output, set_point = 40,
# 			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1)
  		
#   		self.PID_2 = PID(self.T2.read(),	self.PWM.output, set_point = 40,
# 	        Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1)
          
#   		self.TS1 = Thermostat(self.PID_1)
#   		self.TS2 = Thermostat(self.PID_2)

        #Fonctions d'envoi de la température 
	def send(self, txt):
		self.serial.write(txt + self.sep1)
          
	def send_temp(self):
		self.send('temp'
			+ self.sep2 + ('T1=n' if self.T1.read() is None else ('T1=f%.2f' % self.T1.read()))
			+ self.sep2 + ('T2=n' if self.T2.read() is None else ('T2=f%.2f' % self.T2.read())))

	async def temp_loop(self):
		while True:
			await uasyncio.sleep(self.status_cycle)
			self.send_temp()
                 
	async def loop(self):
		while True:
			self.clock = (self.clock + 1) % 100
			await uasyncio.sleep(self.cycle)

			# print debug info
			if self.DEBUG and self.clock == 0:
				self.echo('Stepper position: %.0f' % self.stepper.position)

			# read instructions from serial
			while self.serial.any():
				self.rbuf += self.serial.read().decode()
			if self.rbuf:
				self.instructions += self.rbuf.split(self.sep1)
				self.rbuf = self.instructions.pop()

			# process instructions
			while self.instructions:
				i = self.instructions.pop(0)
				if len(i):
					if i[0] == '@':
						eval(i[1:])
	
	def start(self):
		with open('errorlog.txt', 'w') as f:
			f.write('STARTING THE LOOP')
		uasyncio.create_task(self.temp_loop())
		uasyncio.run(self.loop())
		

if __name__ == '__main__':

	pyb.LED(2).on()
	try:
		pypl = PyPL(DEBUG = False)	
		pyb.LED(2).off()
		pypl.start()
	except Exception as e:
		print_exception(e, open('errorlog.txt', 'w'))
		pyb.LED(2).off()
		pyb.LED(3).off()
		while True:
			pyb.LED(1).toggle()
			utime.sleep(.2)
