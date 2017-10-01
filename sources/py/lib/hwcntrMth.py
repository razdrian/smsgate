############################################################################################################################################
# COPYRIGHT (C) 2016 Razvan Petre
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

# This library is based on code developed by Dragos Iosub, Bucharest 2015. http://itbrainpower.net,original code link below:
# http://itbrainpower.net/micro-GSM-shield-module-cuGSM/GSM-micro-shield-board-module-RaspberryPI-Arduino-c-uGSM-features-code-examples
#
# NAME: hwcntrMth.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of Hardware control methods for GSMclass

############################################################################################################################################

import RPi.GPIO as GPIO
from gsmserialLib import *
from userDefErrs import *
from time import sleep


def refreshStat(self, mode):
    """
    refresh the status variable, memebr of the class

    :param self:
        *GSMModem object
        *mode:
            **True -> refresh the status using STATUS GPIO
            **False -> refresh the modem using AT command
    :raise:
        *GPIOinputError
        *SerialSetupError
    """
    if mode:
        try:
            self.status = GPIO.input(STATUS)
        except:
            self.status = False
            raise GPIOinputError
    else:
        try:
            gsmModuleWrite("+++\r\n")
            gsmModuleWrite(chr(0x1B) + "\r\n")
            gsmModuleWrite("AT\r\n")
            gsmModuleWrite("ATE1\r\n")
            gsmModuleWrite("ATV1\r\n")
            clearSInput()
            clearInput()
        except:
            raise SerialSetupError
        try:
            sendATcommand("AT", ["OK", "ERROR"], 1)
        except:
            self.status=False
            return
        else:
            self.status=True


def powerOn(self):
    """
    if the modem is alreay up, the method raises ModemAlreadyOnError
    if it is not up, tries to power it up

    :param
        *self: GSMModem object
    :raise:
        *GPIOoutputError
        *GPIOinputError
        *SerialSetupError
        *ModemAlreadyOnError
        *ModemPowerOnError

    """
    self.refreshStat(True)
    if self.status:
        raise ModemAlreadyOnError
    else:
        try:
            GPIO.output(POWER, GPIO.LOW)
            sleep(0.2)
            GPIO.output(POWER, GPIO.HIGH)
            sleep(0.5)
            GPIO.output(POWER, GPIO.LOW)
            sleep(0.2)
        except:
            raise GPIOoutputError
    sleep(1)
    self.refreshStat(True)
    if not self.status:
        raise ModemPowerOnError


def powerOff(self):
    """
    if the modem is alreay down, the method raises ModemAlreadyOffError
    if it is not down, tries to power it off
    :param self:
        *GSMModem object
    :raise:
        *GPIOinputError
        *SerialSetupError
        *ModemAlreadyOffError
        *ModemPowerOffError
    """

    self.refreshStat(True)
    if not self.status:
        raise ModemAlreadyOffError
    else:
        try:
            sendATcommand("AT+QPOWD", ["OK", "ERROR"], 1)
        except:
            self.status=True
            return
        else:
            self.status=False
    sleep(1)
    self.refreshStat(True)
    if self.status:
        raise ModemPowerOffError


def restart(self):
    """
    restart the modem using powerOff() and powerOn() methods
    :param
        *self: GSMModem object
    :raise:
        *GPIOinputError
        *GPIOoutputError
        *SerialSetupError
        *ModemAlreadyOffError
        *ModemPowerOffError
    """
    self.powerOff()
    sleep(1)
    self.powerOn()


def reset(self):
    """
    reset the modem using the RESET GPIO pin connection
    :param
        *self: GSMModem object
    :raise:
        *GPIOoutputError
    """
    try:
        GPIO.output(RESET, GPIO.LOW)
        sleep(1)
        GPIO.output(RESET, GPIO.HIGH)
        sleep(5)
    except:
        raise GPIOoutputError


def hwSetup(self):
    """
    set up the GPIO pins STATUS POWER and RESET as I/O and gives them the initial value of HIGH
    :param self:
        *GSMModem object
    :raise
        *GPIOSetupError
    """
    global GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    try:
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
    except:
        GPIO.cleanup()
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
        raise GPIOSetupError
    GPIO.setwarnings(True)


def hwRelease(self):
    """
    release all the GPIO used from GSMModem
    :param
        *self: GSMModem object
    :raise:
        *GPIOReleaseError
    """
    try:
        GPIO.cleanup()
    except:
        raise GPIOReleaseError
