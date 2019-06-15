from rrb2 import *
rr = RRB2()

import os
import thread

# Imports for our networking framework, Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from datetime import datetime
from time import sleep

# The serial library is used for communicating with the Arduino (This may be changed to I2C in future revisions)
import serial

# Import the libraries for the picamera, and define the resolution and framerate for stills and videos
import picamera
cam = picamera.PiCamera()
still_resolution = (1920, 1080)
still_framerate = 75
video_resolution = (1280, 720)
video_framerate = 60

# Check if we need to create directories for the pictures and videos
if not os.path.exists("pictures"):
        os.mkdir("pictures")
if not os.path.exists("videos"):
        os.mkdir("videos")

# Open and begin the log - this is used for debugging purposes
log = open("log.txt", "w")
log.write("BEGINING OF LOG" + "\n")
log.write("DATE.........................DATA/INFO/CONNECTION STATUS" + "\n")

# Define the rec_status variable, which is used to keep track of when video is being recorded
rec_status = 0

# Define, connect, and flush the serial port, this will reset the Arduino
port = "/dev/ttyACM0"
serial = serial.Serial(port,9600)
serial.flushInput()

# TODO: Build a failsafe in case the Arduino fails to respond. This involves pressing the reset button and resetting the serial connection

# Methods for taking pictures, starting/stopping videos. These are all used by the threads
def takePicture():
	log.write("Setting camera settings for a STILL" + "\n")
    	cam.resolution = still_resolution
	cam.framerate = still_framerate
	cam.start_preview()
    	sleep(2)
    	still_file_name = "pictures/" + str(datetime.now()) + ".jpg"
    	cam.capture(still_file_name)
    	log.write("Captured and saved still" + "\n")
    	cam.stop_preview()

def startRecording():
	cam.resolution = (1280, 720)
	cam.framerate = 60
    	cam.start_preview()
    	video_file_name = "videos/" + str(datetime.now()) + ".h264"
    	cam.start_recording(video_file_name)
    	time.sleep(1)

def stopRecording():
	cam.stop_recording()
    	cam.stop_preview()

# This reads the incoming data from the client and takes pictures or starts/stops recording video is needed
def cameraFunction(cameraValues):
	global rec_status
	if cameraValues[4]:
		thread.start_new_thread(takePicture, ())
    	if cameraValues[5]:
    		if rec_status:
    			thread.start_new_thread(stopRecording, ())
			rec_status = 0
    		else:
    			thread.start_new_thread(startRecording, ())
			rec_status = 1

# This method gathers all the data to be sent to the client and puts it into a dictionary
def getDataToSend():
	global rec_status
	serial.write("g")			# As in "go", this tells the Arduino to send the data value over
	xRaw = serial.readline()
	serial.write("g")
	yRaw = serial.readline()
	serial.write("g")
	zRaw = serial.readline()
	distanceRaw = rr.get_distance()
	dataToProcess = {'x': xRaw, 'y': yRaw, 'z': zRaw, 'distance': distanceRaw, 'rec_status_r': rec_status}
	return dataToProcess

# This method processes the data previously collected into a dictionary with the appropiate types: a string for the key and a int for the value
def processDataToSend(dataToProcess):
	xProcessed = int(dataToProcess['x'])
	yProcessed = int(dataToProcess['y'])
	zProcessed = int(dataToProcess['z'])
	distanceProcessed = int(dataToProcess['distance'])
	dataToSend = {'xAxis': xProcessed, 'yAxis': yProcessed, 'zAxis': zProcessed, 'distance': distanceProcessed, 'recStatus': dataToProcess['rec_status_r']}
	return dataToSend

# This method takes the data sent by the client. It is sent in JSON format, which is parsed into a string by the on_message handler in the WebSocketHandler class, and then obtains the values putting them into a list of type int
def processDataRecieved(raw_data):
	values = [int(raw_data[0]), int(raw_data[2]), int(raw_data[4]), int(raw_data[6]), int(raw_data[8]), int(raw_data[10])]
	return values

# This updates the motors and will be removed later on
def setMotors(motorValues):
	log.write(str(datetime.now()) + " : " + "Motors have been updated" + "\n")
	

from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)

# This is the bit which handles the http request from the client, sending back the html file containing the client code
class IndexHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('index.html')

# This is the WebSocketHandler, defining what to when a connecting is opened or closed, and when a message is recieved from the client
class WebSocketHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print("Connected")
    log.write(str(datetime.now()) + " : " + "NEW CONNECTION" + "\n")
    log.write(str(datetime.now()) + " : " + "Getting raw data..." + "\n")
    rawData = getDataToSend()
    log.write(str(datetime.now()) + " : " + "Raw data: " + str(rawData) + "\n")
    log.write(str(datetime.now()) + " : " + "Processing raw data to send..." + "\n")
    processedData = processDataToSend(rawData)
    log.write(str(datetime.now()) + " : " + "Processed data: " + str(processedData) + "\n")
    log.write(str(datetime.now()) + " : " + "----------SPACER----------" + "\n")
    self.write_message(processedData)

  def on_message(self, message):
    rawDataRecieved = str(message)
    log.write(str(datetime.now()) + " : " + "Retrieved raw data from server: " + rawDataRecieved + "\n")
    processedDataRecieved = processDataRecieved(rawDataRecieved)
    log.write(str(datetime.now()) + " : " + "Processed data retrieved from server: " + str(processedDataRecieved) + "\n")
    setMotors(processedDataRecieved)
    log.write(str(datetime.now()) + " : " + "Applied new values to motors..." + "\n")
    cameraFunction(processedDataRecieved)
    log.write(str(datetime.now()) + " : " + "Taking pictures and starting/stopping video recording if requested by client..." + "\n")
    log.write(str(datetime.now()) + " : " + "Done managing data from server and updating systems" + "\n")
    log.write(str(datetime.now()) + " : " + "Getting raw data..." + "\n")
    rawData = getDataToSend()
    log.write(str(datetime.now()) + " : " + "Raw data: " + str(rawData) + "\n")
    log.write(str(datetime.now()) + " : " + "Processing raw data to send..." + "\n")
    processedData = processDataToSend(rawData)
    log.write(str(datetime.now()) + " : " + "Processed data: " + str(processedData) + "\n")
    log.write(str(datetime.now()) + " : " + "----------SPACER----------" + "\n")
    self.write_message(processedData)

  def on_close(self):
    print("Disconnected")
    rr.stop()
    log.write(str(datetime.now()) + " : " + "CONNECTION CLOSED" + "\n")

# This puts the index handler and the websocket handler into one application, and starts it. The port is typically 8080
if __name__ == "__main__":
  tornado.options.parse_command_line()
  app = tornado.web.Application(
      handlers=[
          (r"/", IndexHandler),
          (r"/ws", WebSocketHandler)
      ]
  )
  httpServer = tornado.httpserver.HTTPServer(app)
  httpServer.listen(options.port)
  print "Listening on port:", options.port
  tornado.ioloop.IOLoop.instance().start()