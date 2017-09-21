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
# NAME: c-uGSM-send-SMS.py
# PROJECT: SMS gate
# DESCRIPTION: This module contains only the definition of the GSM_Modem class

############################################################################################################################################

message = "Hi!\r\nThis message has been sent from the c-uGSM v1.13 shield (micro) connected with my RPi board."
destinationNumber = "+40724289644"  # usually phone number with International prefix eg. +40 for Romania - in some networks you must use domestic numbers

from gsmCls import *

QuectelM95 = GSMModem()

startSerialCom()  # open serial communication bw. RPi and c-uGSM shield (micro)

QuectelM95.hwControlSetup()
sleep(2)

QuectelM95.powerOn()
sleep(1)

QuectelM95.setup()

# MAIN PROGRAM section start
Logger.info("try to send a SMS....")

# check AT command pdf for proper 129/145 parameter/number format usage
res = QuectelM95.sendSMS(destinationNumber, "145", message)  # international format numbers
if res == 0:
    Logger.info("SMS has been sent with succes")
# MAIN PROGRAM section end        


stopSerialCom()  # close modem communication

QuectelM95.powerOff()
