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

#
class SerialStartError(Exception):
    def __init__(self):
        pass

class SerialStopError(Exception):
    def __init__(self):
        pass

class SerialSetupError(Exception):
    def __init__(self):
        pass

class SerialRecError(Exception):
    def __init__(self):
        pass

class SerialCommWriteError(Exception):
    def __init__(self):
        pass

class SerialCommReadError(Exception):
    def __init__(self):
        pass

class SerialCommFatalError(Exception):
    def __init__(self):
        pass

class SerialReadLineError(Exception):
    def __init__(self):
        pass

class GPIOinputError(Exception):
    def __init__(self):
        pass

class GPIOoutputError(Exception):
    def __init__(self):
        pass

class ModemAlreadyOnError(Exception):
    def __init__(self):
        pass

class ModemAlreadyOffError(Exception):
    def __init__(self):
        pass

class ModemPowerOnError(Exception):
    def __init__(self):
        pass

class ModemPowerOffError(Exception):
    def __init__(self):
        pass

class GPIOSetupError(Exception):
    def __init__(self):
        pass

class GPIOReleaseError(Exception):
    def __init__(self):
        pass

class RequestedPinError(Exception):
    def __init__(self):
        pass

class GSMModuleSetupError(Exception):
    def __init__(self):
        pass

class IMEIQuerryError(Exception):
    def __init__(self):
        pass

class IMSIQuerryError(Exception):
    def __init__(self):
        pass

class SMSNumberQuerryError(Exception):
    def __init__(self):
        pass

class SignalLevelQuerryError(Exception):
    def __init__(self):
        pass

class NwRegistrationError(Exception):
    def __init__(self):
        pass

class GsmModuleWriteError(Exception):
    def __init__(self):
        pass

class GsmModuleReadError(Exception):
    def __init__(self):
        pass

class SendSMSError(Exception):
    def __init__(self):
        pass

class DeleteSMSError(Exception):
    def __init__(self):
        pass

class DeleteMultipleSMSError(Exception):
    def __init__(self):
        pass
