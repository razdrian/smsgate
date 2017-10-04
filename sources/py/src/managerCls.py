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
# NAME: powerMngCls.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of PowerMng class

############################################################################################################################################

from globalPara import *
from userDefErrs import *
import RPi.GPIO as GPIO
import time
import subprocess

class Manager:
    def __init__(self):
        self.state = 'FullyCharged'
        self.queue=[]

    def hwSetup(self):

        global GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        try:
            GPIO.setup(INT, GPIO.IN)
            GPIO.setup(POL, GPIO.IN)
            GPIO.setup(CLR, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(STATUS, GPIO.IN)
            GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
        except:
            raise GPIOSetupError
        GPIO.setwarnings(True)

    def hwRelease(self):
        try:
            GPIO.cleanup()
        except:
            raise GPIOReleaseError

    def setState(self, newState):
        self.state = newState
        self.resetQueue()

    def resetQueue(self):
        self.queue=[]

    def getState(self):
        return self.state

    def resetBattCap(self):
        f = open('/var/smsgate/battCap.txt', 'w')
        f.write(str(defaultBattCap))
        f.close()

    def getBattCap(self):
        f = open('/var/smsgate/battCap.txt', 'r')
        battCap = float(f.read())
        f.close()
        return battCap

    def incrementBattCap(self, time):
        f = open('/var/smsgate/battCap.txt', 'r')
        battCap = float(f.read())
        f.close()
        battCap += defaultIntValue
        f = open('/var/smsgate/battCap.txt', 'w')
        f.write(str(battCap))
        f.close()
        self.queue.insert(0,time)
        if len(self.queue) > 20:
            self.queue.pop()

    def startPPP(self):
        #process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #result, error = process.communicate('sudo '+'route '+'del '+'default ')
	process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	result, error = process.communicate('sudo '+'pon '+'d-u3G')
	time.sleep(3)
        if error:
            return False
        else:
            return True
    def stopPPP(self):
        #process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #result, error = process.communicate('sudo '+'poff '+'d-u3G')
	#time.sleep(3)
        #if error:
        #   return False
        #else:
        return True

    def testGPRSping(self):
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = process.communicate('ping ' + '-w ' + '1 ' + '-W ' + '3 ' + '8.8.8.8')
        if result:
            return True
        elif error:
            return False

    def getChargingTime(self):
        """

        :return: ChargingTime in minutes
        """
        remainingToAdd=defaultBattCap-self.getBattCap() #value in mA
        intToAdd=remainingToAdd/defaultIntValue         #value in INTs
        totalTime=intToAdd*float(sum(self.queue)/len(self.queue))
        return totalTime/60

    def getDischargingTime(self):
        """

        :return: DischargingTime in minutes
        """
        remainingToSubb=self.getBattCap()-defaultBattLow
        intToSubb=remainingToSubb/defaultIntValue
        totalTime=intToSubb*float(sum(self.queue)/len(self.queue))
        return totalTime/60

    def decrementBattCap(self,time):
        f = open('/var/smsgate/battCap.txt', 'r')
        battCap = float(f.read())
        f.close()
        battCap -= defaultIntValue
        f = open('/var/smsgate/battCap.txt', 'w')
        f.write(str(battCap))
        f.close()
        self.queue.insert(0,time)
        if len(self.queue) > 20:
            self.queue.pop()

    def clearInt(self):
        GPIO.output(CLR, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(CLR, GPIO.HIGH)

    def getIntState(self):
        return GPIO.input(INT)

    def getPolState(self):
        return GPIO.input(POL)
