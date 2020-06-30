# PiRover #

This is a simple project where you can control a small 2-WD robot controlled by a Raspberry Pi and Arduino via any device you want through your browser. It utilizes tornado, a Python web framework, by using simple HTTP requests to control the movement of the robot, and a websocket to send live readings from sensors on the robot (gyroscopes, ultrasonic sensors, etc.)

The hardware is a simple 2-WD chassis with a Raspberry Pi controlling the motors via a RasPiRobot Board V2, a Raspberry Pi camera module for taking videos and pictures, as well as an Arduino which reads some of the sensors and reports back to the Pi over a USB link.
