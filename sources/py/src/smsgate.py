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
# NAME: smsgate.py
# PROJECT: SMSGate
# DESCRIPTION: This module has the main function of the whole application

############################################################################################################################################

# !/usr/bin/python
from Daemon import *


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            if daemon.getPID():
                print 'smsgate daemon is already running!Use stop before start'
                sys.exit(1)
            else:
                daemon.start()
        elif 'stop' == sys.argv[1]:
            if not daemon.getPID():
                print 'NO smsgate daemon is running!Use start before stop'
                sys.exit(1)
            else:
                daemon.stop()
        elif 'status' == sys.argv[1]:
            if not daemon.getPID():
                print 'NO smsgate daemon is running!Use start before status'
                sys.exit(1)
            else:
                os.kill(daemon.getPID(), signal.SIGUSR1)
                time.sleep(10)

        elif 'help' == sys.argv[1]:
            print "usage: %s start|stop|restart|status|help" % sys.argv[0]
        else:
            print "Unknown command. See help for more info"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status|help" % sys.argv[0]
        sys.exit(2)
