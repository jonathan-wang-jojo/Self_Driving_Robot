from motor import Motor
import RPi.GPIO as GPIO
import time


class Robot:
  def __init__(self):
    GPIO.setwarnings(False)
    self.__leftMotor = Motor((22,27),4)
    self.__rightMotor = Motor((24,23),25)
    
  def Forward(self, run):
    self.__leftMotor.Run(50)
    self.__rightMotor.Run(43)
    time.sleep(run)
    self.Brake()

  def Reverse(self, run):
    self.__leftMotor.Reverse(48.3)
    self.__rightMotor.Reverse(50)# left motor 48.3 right 50 
    time.sleep(run)
    self.Brake()

  def Turn(self, Left, run):
    if (Left == False):
      self.__rightMotor.Reverse(45)
      self.__leftMotor.Run(45)
      time.sleep(run)
      self.Brake() 
    else:
      self.__rightMotor.Run(45)
      self.__leftMotor.Reverse(45) # left turn values 45 45 and 0.66
      time.sleep(run)
      self.Brake()
    
  def Brake(self):
    self.__rightMotor.Brake()
    self.__leftMotor.Brake()

  def AutoRun(self):
    self.Forward(4.7)
    self.Turn(False, 0.82)
    self.Forward(5)
    self.Reverse(2)
    self.Turn(False, 0.83)
    self.Forward(4.7)
    self.Turn(True, 1.63)

  def __del__(self):
    GPIO.setmode(GPIO.BCM)
    del self.__leftMotor
    del self.__rightMotor
    GPIO.cleanup()
