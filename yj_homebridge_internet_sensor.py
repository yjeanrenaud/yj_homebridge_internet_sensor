#!/usr/bin/env python3
# yj_homebridge_internet_sensor
# A small python script to monitor the local internet connection and expose a HTTP server for homebridge and other smart home applications
#see https://github.com/yjeanrenaud/yj_homebridge_internet_sensor/
##CONFIGURATION

pairsOfHosts = [
    ('router', '192.168.1.1'),
    ('cf dns', '1.1.1.1'),
    ('pocketpc.ch', 'pocketpc.ch')
] #as many pairs of descripions and hosts you want. fqdn or IP addresses required for the later. I ping my own router, the public dns of cloudflare and the host of pocketpc.ch, obviously

port = 99 #any port available on your host running this script

from pythonping import ping
import datetime, time
import subprocess
from time import sleep
from socket import gethostbyname 
from socket import gaierror

#stuff for the http server
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
#we need threading for regular polling and filling up the router_is_up var
import threading
# we need basename to know what this script file is called like
from os.path import basename
import os
#for the http-server
router_is_up = 0 # means Internet is not sane!
version='2.0.2'

def pingpong(name,host):
	name=str(name)
	host=str(host)
	global router_is_up
	
	try:
		answer=gethostbyname(host)
	except gaierror as e:
		print('failed to resolve '+host+': {}'.format(e))
		#make some sound and/or light
		alerting()
		#now restart the router via 433 MHz
		restart_router()
		#pause before CONTINUE
		print("\nnow wait five minutes before we continue...")
		time.sleep(300) #and yes, we can keep the thread busy and don't care for drift
		return

	# so now we should be able to reach it. either the name is in dns cache, dns is reachable or everything is fine. let's try out!
	response_list=ping(answer, verbose=False)
	#print(response_list.success)
	if name == answer:
			print(answer+" pinged at " + str(datetime.datetime.now()))
	else:
		print(name+" ("+answer+") pinged at " + str(datetime.datetime.now()))
	
	if response_list.packet_loss != 0.0:
		print ("we lost some packets to "+answer+"?!")
	if response_list.rtt_min_ms == 2000:
		print ("it took too long to "+answer)
	if response_list.rtt_min_ms == response_list.rtt_max_ms:
		print ("there is no variance to "+answer) 
	if response_list.rtt_min_ms == response_list.rtt_avg_ms:
		print ("there is no variance, "+answer+"too")
	if response_list.packet_loss != 0.0 or response_list.rtt_min_ms == 2000 or (response_list.rtt_min_ms == response_list.rtt_max_ms and response_list.rtt_min_ms == response_list.rtt_avg_ms):
		print("connection to the Internet 🌍 is lost!")
		print("\nnow wait five minutes before we continue...")
		time.sleep(300) #and yes, we can keep the thread busy and don't care for drift

	else:
		print("...with success.")
		router_is_up = 1 #set the variable for the HTTP server to OK
	#end of pingpong(name,host)

def check_router_thread(pairsOfHosts): ##function for the second thread
	while 1:
		for pair in pairs:
            pingpong(pair[0], pair[1])
		
		#pause before repeat all checks
		print("\nThe router 💻 is up and the connection to the Internet is sane.\nNow wait five minutes, before we check it all again...⏱")
		time.sleep(300) #and yes, we can keep the thread busy and don't care for drift
	#end of endless while
#end of check_router_thread

class server_handler(BaseHTTPRequestHandler):

	def _set_headers(self):
		#overwrite server info string. Only works for BaseHTTPRequestHandler, not SimpleHTTPRequestHandler
		self.server_version=str(basename(__file__))+'/'+version
		#'yj_homebridge_internet_sensor.py/2.0.2'
		self.sys_version=''
		self.send_response(200)
		self.send_header('Content-type', 'text/html; charset=utf-8')
		self.end_headers()
        
	def do_HEAD(self):
		self._set_headers()
		
	# GET sends back a message
	def do_GET(self):
		self._set_headers()
		global router_is_up
		if self.path != '/':
			self.send_error(404, "Object not found")
			return
		#check_router_thread()
		#self.wfile.write(bytes("<html><body><h1>"+str(router_is_up)+"</h1></body></html>",'utf-8')) #debug
		#self.wfile.write(router_is_up.to_bytes(2,'big'))
		self.wfile.write(bytes(str(router_is_up),'utf-8'))
	
	def do_POST(self):
		# refuse to receive any content
		self.send_response(400)
		self.end_headers()
		return
	
	def log_message(self, format, *args):
		return #to silent the log messages
#end class server_handler

class server_thread(threading.Thread):#oop ftw

	def __init__(self,port):
		threading.Thread.__init__(self)
		self.port = port
		self.daemon = True
		self.start()
		#print(self)
		
	def run(self):
		server_address = ('', self.port)
		server_version=str(basename(__file__))+'/'+version
		#'yj_homebridge_internet_sensor.py/2.0.2'
		httpd = HTTPServer(server_address, server_handler)
		print ('starting httpd on port %d...' % self.port)
		httpd.serve_forever()
	#end of run


if __name__ == "__main__":
	from sys import argv
	
	if len(argv) == 2:
		server_thread(int(argv[1])) #arg not named anymore
	else:
		server_thread(port)
	
	# start the thread for checking the router
	th2 = threading.Thread(target=check_router_thread,daemon=True)
	th2.start()
	while(1):
		sleep(1) # to keep the main routine busy.
#eof
