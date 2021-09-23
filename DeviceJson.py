import time
import serial
#from serial import SerialException
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
from random import randint

config = {}
config['port'] = ""
config['oldWeight'] = 0
config['lastError'] = False
def is_number(s):
    if s is None or s == "hardware_failure":
        return False
    error = False
    try:
        float(s)
        return True
    except ValueError as e:
        # print e
        error = True

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError) as e:
        # print e
        error = True
    return False

def getIP(url):
    query = urlparse(url).query
    try:
        query_components = dict(qc.split("=") for qc in query.split("&"))
        ip = query_components["ip"]
        if len(ip) == 0:
            return 'ip_missing'
        return ip
    except ValueError as e:
        # print e
        return False

def getSerialPort():
    if config['port'] != "":
        return config['port']
    port = '/dev/ttyUSB'
    attempts = 0;
    for index in range(0,5):
        portTest = port + str(index)
        try:
            ser = serial.Serial(
                port=portTest,
                baudrate=4800,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.SEVENBITS,
                timeout=1
            )

            while 1:
                if hex(ord(ser.read(1))) == "0x3":
                    ser.close()
                    config['port'] = portTest
                    return portTest
                    break
            ser.close()
        except ValueError as e:
            # print e
            attempts += 1
        except Exception:
            attempts += 1
    if attempts >= 5:
        return False

def getSerialWeight():
    port = getSerialPort()
    return get1612Weight(port)
def get1612Weight(port):
    if port == False:
        return 'check_usb_connection'
    ser = serial.Serial(
		port=port,
		baudrate=4800,
		parity=serial.PARITY_EVEN,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.SEVENBITS,
        timeout=1
	)
    ser.isOpen()
    exitReading = False
    isMinus=False
    isStandstill=False
    isError=False
    while exitReading == False:
        try:
            val = ser.read(1)
            print(val)
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
        except ValueError as e:
            print(e)
            return "hardware_failure"
def getNetworkWeight(ip):
    return 'not_implemented'

def getWeight(url):
    data = {}
    ip = getIP(url)
    if ip == False:
        result = getSerialWeight()
        if is_number(result) == True:
            data['weight'] = result
            config['oldWeight'] = result
            config['lastError'] = False
        elif result is None and config['lastError'] is False:
            data['weight'] = config['oldWeight']
        else:
            if result is None:
                result = "hardware_failure"
            data['error'] = result
            config['lastError'] = True
    elif ip == 'ip_missing':
        data['error'] = ip
    else:
        result = getNetworkWeight(ip)
        if is_number(result) == True:
            data['weight'] = result
            config['oldWeight'] = result
        elif result is None:
            data['weight'] = config['oldWeight']
        else:
            data['error'] = result
    return json.dumps(data)


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(getWeight(self.path))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("error")

def run(server_class=HTTPServer, handler_class=S, port=1612):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
