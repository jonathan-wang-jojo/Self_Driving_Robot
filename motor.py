import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)
#Pins 18 22 24 GPIO 24 25 8
class Motor:
  def __init__(self, pin, enablepin):
    GPIO.setup(pin[0], GPIO.OUT)
    GPIO.setup(pin[1], GPIO.OUT)
    GPIO.setup(enablepin, GPIO.OUT)
    self.__pins = (GPIO.PWM(pin[0], 100), GPIO.PWM(pin[1], 100))
    self.__pins[0].start(0)
    self.__pins[1].start(0)
    self.__ena = enablepin

  def __Enable(self, truthy):
    if(truthy):
      GPIO.output(self.__ena, GPIO.HIGH)
    elif(not truthy):
      GPIO.output(self.__ena, GPIO.OUT)

  def Run(self, power):
    self.__Enable(True)
    self.__pins[0].ChangeDutyCycle(0)
    self.__pins[1].start(power)

  def Reverse(self, power):
    self.__Enable(True)
    self.__pins[1].ChangeDutyCycle(0)
    self.__pins[0].start(power)
  def Brake(self):
    self.__pins[1].stop()
    self.__pins[0].stop()
    self.__Enable(False)

  def __del__(self):
    self.__pins[0].stop()
    self.__pins[1].stop()
    self.__Enable(False)
