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
# NAME: gsmCls.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of the GSMModem class

############################################################################################################################################

from hwcntrMth import *
from basicMth import *
from smsMth import *
import threading


class GSMModem:
    """
    GSM_Modem class describing the c-uGSM modem with methods to control it

    There are only declarations of methods in this .py file and their definition is in another lib file according to their category:
        - I{HwControl_methods.py} -> Hardware Control Methods for QuectelM95 Modem
        - I{Basic_methods.py} -> Basic Methods
        -I{SMS_methods.py} -> SMS Methods for sending and retrieving SMS
    """
    status = 0  # 1 if modem is running, 0 if it is off
    activeSIM = 0  # 0 if the active SIM is the top one, 1 if active SIM is bottom
    noSMS = 0
    totSMS = 0

    def __init__(self):
        self.lock = threading.Lock()
        pass
    # def checkNwReg (self):
    #     print 'e in ckech nw reg in clasa'
    #     return True

    # HwControl methods
    powerOn = classmethod(powerOn)
    powerOff = classmethod(powerOff)
    restart = classmethod(restart)
    reset = classmethod(reset)
    hwSetup = classmethod(hwSetup)
    hwRelease = classmethod(hwRelease)
    refreshStat = classmethod(refreshStat)

    # Basic methods
    getIMEI = classmethod(getIMEI)
    getIMSI = classmethod(getIMSI)
    getActiveSIM = classmethod(getActiveSIM)
    getSignalStat = classmethod(getSignalStat)

    setActiveSIM = classmethod(setActiveSIM)

    checkNwReg = classmethod(checkNwReg)
    setup = classmethod(setup)

    # SMS methods
    gettotSMS = classmethod(gettotSMS)
    getnoSMS = classmethod(getnoSMS)
    getSMS = classmethod(getSMS)

    refreshSMSno = classmethod(refreshSMSno)
    sendSMS = classmethod(sendSMS)
    deleteSMS = classmethod(deleteSMS)
    deleteMulSMS = classmethod(deleteMulSMS)

