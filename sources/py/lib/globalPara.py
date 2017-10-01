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
# NAME: globalPara.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains all the global parameters for the SMSgate system

############################################################################################################################################

# hardware connection pins (all in GPIO BOARD mode numbering)
# for QuectelM95 Pins
POWER = 33
RESET = 35
STATUS = 31
serialSpeed = 115200
# for GPLeds (Y - Yellow and R - Red)
LEDY = 37
LEDR = 40
# for Coulomb counter
INT = 38
POL = 36
CLR = 32

# passwd and users
email_key = "6FA32E"
email_user = "raspberry.iot95"
email_pwd = "adripet!234%"

# constrints manager
spec_FSchars = ['.', ' ', '|', '\"', '@']
spec_EMLchars = [' ', '\'', '~']
allowed_domains = ['gmail.com', 'yahoo.com', 'amiq.com', 'stud.etti.upb.ro']

# global variables
delays = {'sms': 3, 'email': 3, 'fs': 3, 'powerMng': 1, 'watchdog': 3}
default_SMSsize = 155  # No of chars to which a mail/FS content will be trimmed before outputed via SMS
deltaTimeOut = 10  # delta time to wait before killing thread if not responding at stop command
ATcmdNOFRetry = 5  # number of retries before exiting application if response from QM95 is not received
readStringLen = 200  # maximul lenght of a response to a given command from QM95
defaultBattCap = 2200  # default battery capacity in mAh
defaultBattLow = 300  # default battery capacity in mAh low
defaultIntValue = 0.34  # value of one INT from CoulombCounter in mA

# program paths
input_path = '/var/smsgate/input/'
txt_out_path = '/var/smsgate/output/savedtxt/'
status_out_path = '/var/smsgate/output/savedsts/'
log_out_path = '/var/smsgate/output/savedlogs/'
log_path = '/var/smsgate/log/'
commands_path = '/var/smsgate/commands'
phonebook_path = '/var/smsgate/'

# definition and format for logging
import logging

Logger = logging
FORMAT = "%(asctime)s [%(filename)-15s:%(lineno)-3s - %(funcName)-15s] %(message)s"
Logger.basicConfig(filename='/var/smsgate/log/logging.txt', format=FORMAT, datefmt='%d/%m/%Y_%H:%M:%S',
                   level=logging.DEBUG)
#Logger.basicConfig(format=FORMAT, datefmt='%d/%m/%Y_%H:%M:%S',level=logging.DEBUG)
