import time
import serial
import binascii

ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=4800,
	parity=serial.PARITY_EVEN,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.SEVENBITS,
	timeout=1
)
ser.isOpen()
index=0
weight=[]
status=""
newPacket=False
while 1:
	try:
		val = ser.read(1)
		print val
		if hex(ord(val)) == "0x2":
			packet      = ser.read(9)
			readAgain   = False
			for char in packet:
				if hex(ord(char)) == "0x3" or hex(ord(char)) == "0x2" or hex(ord(char)) == "0x1a":
					readAgain = True
			if readAgain == False:
				weight  = packet[3:9]
				for char in weight:
					if char.isalpha() == True:
						return "hardware_failure"
				status  = packet[1]
				isMinus = bin(ord(status))[4] == "1"
				isStandstill = bin(ord(status))[7] == "1"
				exitReading = True
				if isMinus == True:
					return int("-" + weight)
				else:
					return int(weight)
	except ValueError:
		print "error"
