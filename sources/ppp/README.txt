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
# NAME: README.txt
# PROJECT: SMSGate
# DESCRIPTION: This README contains information about how to set up ppp connection using c-uGSM

############################################################################################################################################

copy the files:
    cp /smsgate/sources/ppp/pears/* /etc/ppp/pears
    cp /smsgate/sources/ppp/bin/* $HOME/bin

edit:
    $HOME/bin/startPPP and chose your shield model (a-gsm, c-uGSM or d-3G)
    $HOME/bin/stopPPP, same as above

    /etc/ppp/pears/a-gsm or /etc/ppp/pears/c-uGSM or /etc/ppp/pears/d-3G 
    and
	-> chose between SERIAL or USB connectivity (SERIAL for SMSGate system)
	-> change "internet" to a real APN name (eg. live.vodafone.com for Vodafone Romania



./startPPP will start the wireless communication. ifconfig, route -n and cat /etc/resolv.conf will provide to you additional information
new default route (via PPP0) will be efective! if you DON'T need this edit the pear file... 

./stopPPP will stop the wireless communication and restore the default route. ifconfig, route -n and cat /etc/resolv.conf...



