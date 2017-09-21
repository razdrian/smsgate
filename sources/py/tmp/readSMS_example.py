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
# NAME: c-uGSM-read-SMS.py
# PROJECT: SMS gate
# DESCRIPTION: This module contains only the definition of the GSM_Modem class

############################################################################################################################################


from gsmCls import *



QuectelM95=GSMModem()

startSerialCom()                        # open serial communication bw. RPi and c-uGSM shield (micro)

QuectelM95.hwControlSetup()
sleep(2)

QuectelM95.powerOn()
sleep(1)


QuectelM95.setup()


QuectelM95.refreshSMSno()
Logger.info("total SMS locations: "+str(QuectelM95.totSMS))
Logger.info("last SMS location: "+str(QuectelM95.noSMS))

QuectelM95.setSMSstorage('MT','MT','MT')
Logger.info("total SMS locations: "+str(QuectelM95.totSMS))
Logger.info("last SMS location: "+str(QuectelM95.noSMS))

for i in range (QuectelM95.noSMS):
    Logger.info("read/parse SMS stored @ location "+str(i+1))
    SMSmessage=QuectelM95.getSMS(i+1)
    Logger.info("SMS type: "+SMSmessage[0])
    Logger.info("Sender no.: "+SMSmessage[1])
    Logger.info("Date and time local: "+SMSmessage[2])
    Logger.info("Date and time UTC: "+ str(SMSmessage[2])[0:-3])
    Logger.info("Content:"+SMSmessage[3])



QuectelM95.deleteMultipleSMS('ALL')
QuectelM95.refreshSMSno()
Logger.info("total SMS locations: "+str(QuectelM95.totSMS))
Logger.info("last SMS location: "+str(QuectelM95.noSMS))

# stop SERIAL COMMUNICATION section start        
stopSerialCom()                             # close modem communication

QuectelM95.powerOff()



Logger.info("That's all folks!!")
