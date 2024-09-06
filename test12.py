import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

# Turn on the water pump
GPIO.output(26, GPIO.LOW)

'''
# Turn off the water pump
GPIO.output(26, GPIO.HIGH)
GPIO.cleanup()
'''