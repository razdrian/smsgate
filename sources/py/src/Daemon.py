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
# NAME: Daemon.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of Daemon class and workers methods

############################################################################################################################################

# imports
from Handlers import *
from SysManager import *
from Errors import *
from globalPara import *
from SerialCOM import *

import signal
import sys, os, time, atexit
import threading
import traceback


# workers of the three main threads
def emailWorker(email_event, email_kill):
    while not email_kill.isSet():
        email.lock.acquire()
        if sysManager.testGPRSping():
            try:
                UIDs = email.getEmailUIDs()
            finally:
                if email.lock.locked():
                    email.lock.release()
            if len(UIDs) != 0:  # if there is a new email
                email.lock.acquire()
                try:
                    # treats all the relieved sms at once
                    for email_uid in UIDs.split():
                        new_mail = email.getMail(email_uid)
                        if handlers.handleEmail(new_mail) != -1:
                            email.deleteMail(email_uid)
                        else:
                            Logger.error('System could not handle Email! It will try to handle it next iteration...')
                finally:
                    if email.lock.locked():
                        email.lock.release()
        else:
            if email.lock.release():
                email.lock.release()
            Logger.error('No Internet connection! This will be resolved by watchdog in a moment!')

        email_event.set()
        time.sleep(delays['email'])
        email_event.clear()


def smsWorker(sms_event, sms_kill):
    while not sms_kill.isSet():
        gsmModem.lock.acquire()
        gsmModem.refreshStat(True)
        if gsmModem.status:
            try:
                gsmModem.checkNwReg(5)
            except NwRegistrationError:
                Logger.error('GSM Module is not registered to network. We should wait4signal...')
            except:
                Logger.error('Unknown error while trying to querry GSM Module network registration...')
            else:
                gsmModem.refreshSMSno()
                index = gsmModem.noSMS
                if index != 0:
                    sms = gsmModem.getSMS(index)
                    if handlers.handleSMS(sms[1], sms[3]) != -1:
                        gsmModem.deleteSMS(index)
                    else:
                        Logger.error('System could not handle SMS! It will try to handle it next iteration...')
        else:
            Logger.info('gsmModem status is off! System will restart QM95')
            gsmModem.restart()


        if gsmModem.lock.locked():
            gsmModem.lock.release()
        sms_event.set()
        time.sleep(delays['sms'])
        sms_event.clear()


def fsWorker(fs_event, fs_kill):
    while not fs_kill.isSet():
        try:
            process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, error = process.communicate('find /var/smsgate/input/ -name \'*\'')
        except:
            Logger.error('Fatal error while opening input directory to search for .sms or .email!')
        finally:
            result = result.split('\n')
            if len(result) > 2:
                if handlers.handleFS(result[1]) != -1:  # always handle the first file is the returned list from FS
                    Logger.info('File %s will be now deleted ' % result[1])
                    try:
                        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        result, error = process.communicate('rm -rf %s' % result[1])
                    except:
                        Logger.error('Fatal error while trying to remove %s file' % result[1])
                    finally:
                        if error:
                            Logger.error('Could not remove %s file from FS!' % result[1])
                else:
                    Logger.error('System could not handle %s file! It will try to handle it next iteration...' % result[1])

        fs_event.set()
        time.sleep(delays['fs'])
        fs_event.clear()


def powerMngWorker(powerMng_event, powerMng_kill):
    timestamp = time.time()
    # TODO detect idle state of batt
    while not powerMng_kill.isSet():
        if not sysManager.getIntState():
            if sysManager.getPolState():
                if time.time() - timestamp < 65:
                    if sysManager.getState() != 'Charging':
                        sysManager.setState('Charging')
                    sysManager.incrementBattCap(time.time() - timestamp)
                    if sysManager.getBattCap() > defaultBattCap:
                        sysManager.setState('FullyCharged')
                else:
                    sysManager.setState('FullyCharged')
            else:
                if sysManager.getState() != 'Discharging':
                    sysManager.setState('Discharging')
                sysManager.decrementBattCap(time.time() - timestamp)
            sysManager.clearInt()
            timestamp = time.time()

        powerMng_event.set()
        time.sleep(delays['powerMng'])
        powerMng_event.clear()


def watchdogWorker(email_thread, sms_thread, fs_thread, powerMng_thread, events, kills):
    while not kills['watchdog'].isSet():
        if not email_thread.isAlive():
            Logger.info('Unfortunately the Email Thread is not alive! I will try to restart it righ now...')
            events['email'].clear()
            kills['email'].clear()
            try:
                email_thread.start()
                Logger.info('Email thread successfully restarted!')
            except:
                Logger.error('Unable to start the Email Thread.. Everything is lost right now')

        if not sms_thread.isAlive():
            Logger.info('Unfortunately the SMS Thread is not alive! I will try to restart it righ now...')
            events['sms'].clear()
            kills['sms'].clear()
            try:
                sms_thread.start()
                Logger.info('SMS thread successfully restarted!')
            except:
                Logger.error('Unable to start the SMS Thread.. Everything is lost right now')

        if not fs_thread.isAlive():
            Logger.info('Unfortunately the FS Thread is not alive! I will try to restart it righ now...')
            events['fs'].clear()
            kills['fs'].clear()
            try:
                fs_thread.start()
                Logger.info('FS thread successfully restarted!')
            except:
                Logger.error('Unable to start the FS Thread.. Everything is lost right now')

        if not powerMng_thread.isAlive():
            Logger.info('Unfortunately the powerMng Thread is not alive! I will try to restart it righ now...')
            events['powerMng'].clear()
            kills['powerMng'].clear()
            try:
                powerMng_thread.start()
                Logger.info('powerMng thread successfully restarted!')
            except:
                Logger.error('Unable to start the powerMng Thread.. Everything is lost right now')

        if not sysManager.testGPRSping():
            Logger.info('No internet connection now! PPP must pe dead! I will try to restart it right now...')
            try:
                if not sysManager.stop():
                    Logger.error('Could not turn off the PPP!')
                if not sysManager.start():
                    Logger.error('Could not turn on the PPP')
                time.sleep(8)
            except:
                Logger.info('Not able to restart PPP. Internet connection is lost right now...')
        events['watchdog'].set()
        time.sleep(delays['watchdog'])
        events['watchdog'].clear()


class Daemon:
    def __init__(self, pidfile, stdin='/dev/null', stdout='/home/pi/debug_out_files/stdout', stderr='/home/pi/debug_out_files/stderr'):

        self.events = {'email': threading.Event(), 'sms': threading.Event(), 'fs': threading.Event(),
                       'powerMng': threading.Event(), 'watchdog': threading.Event()}

        self.statusEvents = {'toFile': threading.Event(), 'toSMS': threading.Event(), 'toEmail': threading.Event()}

        self.kills = {'email': threading.Event(), 'sms': threading.Event(), 'fs': threading.Event(),
                      'powerMng': threading.Event(), 'watchdog': threading.Event()}

        self.email_thread = threading.Thread(name='email_thread', target=emailWorker,
                                             args=(self.events['email'], self.kills['email'],))
        self.sms_thread = threading.Thread(name='sms_thread', target=smsWorker,
                                           args=(self.events['sms'], self.kills['sms'],))
        self.fs_thread = threading.Thread(name='fs_thread', target=fsWorker,
                                          args=(self.events['fs'], self.kills['fs'],))

        self.powerMng_thread = threading.Thread(name='powerMng_thread', target=powerMngWorker,
                                                args=(self.events['powerMng'], self.kills['powerMng'],))
        self.watchdog_thread = threading.Thread(name='watchdog_thread', target=watchdogWorker,
                                                args=(self.email_thread, self.sms_thread, self.fs_thread,
                                                      self.powerMng_thread, self.events, self.kills,))

        # self.watchdog_thread= threading.Thread(name='watchdog_thread', target=self.watchdogWorker)

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

        self.isrunning = True

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit first parent
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")  # decouple from parent environment
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit from second parent
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        # sys.stdout.flush()
        # sys.stderr.flush()

        si = file(self.stdin, 'r')
        so = file(self.stdout, 'w')
        se = file(self.stderr, 'a+', 0)

        # os.dup2(fd, fd2)
        #   Duplicate file descriptor fd to fd2, closing the latter first if necessary.

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # set routine for exit executed backwards
        atexit.register(self.delPID)
        atexit.register(self.systemQuit)

        # write pidfile in fs
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delPID(self):
        os.remove(self.pidfile)

    def killThreads(self, signum, frame):
        # you first kill the watchdog beacause it's using the other resources
        self.kills['watchdog'].set()
        self.events['watchdog'].wait(delays['watchdog'] + deltaTimeOut)
        self.watchdog_thread.join(delays['watchdog'] + deltaTimeOut)

        self.kills['powerMng'].set()
        self.events['powerMng'].wait(delays['powerMng'] + deltaTimeOut)
        self.powerMng_thread.join(delays['powerMng'] + deltaTimeOut)

        self.kills['email'].set()
        self.events['email'].wait(delays['email'] + deltaTimeOut)
        self.email_thread.join(delays['email'] + deltaTimeOut)

        self.kills['sms'].set()
        self.events['sms'].wait(delays['sms'] + deltaTimeOut)
        self.sms_thread.join(delays['sms'] + deltaTimeOut)

        self.kills['fs'].set()
        self.events['fs'].wait(delays['fs'] + deltaTimeOut)
        self.fs_thread.join(delays['fs'] + deltaTimeOut)

        for event_name in self.events:
            self.events[event_name].clear()

        for kill_name in self.kills:
            self.kills[kill_name].clear()

        for statEv in self.statusEvents:
            self.statusEvents[statEv].clear()

        Logger.info('All the 5 threads were killed successfully!')
        self.isrunning = False

    def getPID(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except:
            pid = None
        return pid

    def start(self):  # s-a verificat deja ca pidul NU exista
        self.systemSetup()
        self.daemonize()

        try:
            self.email_thread.start()
            self.sms_thread.start()
            self.fs_thread.start()
            self.powerMng_thread.start()
            self.watchdog_thread.start()
        except:
            Logger.error('Error starting the 5 threads (email,sms,fs,powerMng,watchdog)!')
        self.run()

    def stop(self):  # vefificare ca exsita pid-ul s-a facut inainte
        pid = self.getPID()
        Logger.info('SIGTERM signal was sent right now.')
        # The pid file will be deletet in atexit(self.delPID)
        os.kill(pid, signal.SIGTERM)

    def getStatus(self, weight):
        if weight == 'Heavy':
            status = '-->Information about software application smsgate.py:\n'
            if self.isrunning:
                status += 'The smsgate.py daemon is still active and alive\n'
            else:
                status += 'The smsgate.py daemon is dead and gone...\n'

            status += '\n'
            for i in range(37):
                status += '_'
            status += '\n'
            status += '|' + 'Resource Name'.center(20) + '|' + 'State'.center(17) + '|' + '\n'
            if gsmModem.lock.locked():
                locker = 'Locked'
            else:
                locker = 'Released'
            status += '|' + 'gsmModem'.center(20) + '|' + locker.center(17) + '|' + '\n'
            if email.lock.locked():
                locker = 'Locked'
            else:
                locker = 'Released'
            status += '|' + 'Email'.center(20) + '|' + str(locker).center(17) + '|' + '\n'

            for i in range(37):
                status += '-'
            print ''
            status += '\n'
            status += '\n'
            for i in range(51):
                status += '_'
            status += '\n'
            status += '|' + 'Thread Name'.center(15) + '|' + 'Liveness'.center(15) + '|' + 'State'.center(
                17) + '|' + '\n'
            info = ['Email Thread', '', '']
            if self.email_thread.isAlive():
                info[1] = 'Alive'
                if self.events['email'].isSet():
                    info[2] = 'Idle'
                else:
                    info[2] = 'Working'
            else:
                info[1] = 'Dead'
                info[2] = 'X'
            status += '|' + info[0].center(15) + '|' + info[1].center(15) + '|' + info[2].center(17) + '|' + '\n'

            info = ['SMS Thread', '', '']
            if self.sms_thread.isAlive():
                info[1] = 'Alive'
                if self.events['sms'].isSet():
                    info[2] = 'Idle'
                else:
                    info[2] = 'Working'
            else:
                info[1] = 'Dead'
                info[2] = 'X'
            status += '|' + info[0].center(15) + '|' + info[1].center(15) + '|' + info[2].center(17) + '|' + '\n'

            info = ['FS Thread', '', '']
            if self.fs_thread.isAlive():
                info[1] = 'Alive'
                if self.events['fs'].isSet():
                    info[2] = 'Idle'
                else:
                    info[2] = 'Working'
            else:
                info[1] = 'Dead'
                info[2] = 'X'
            status += '|' + info[0].center(15) + '|' + info[1].center(15) + '|' + info[2].center(17) + '|' + '\n'

            info = ['powerMng Thread', '', '']
            if self.powerMng_thread.isAlive():
                info[1] = 'Alive'
                if self.events['powerMng'].isSet():
                    info[2] = 'Idle'
                else:
                    info[2] = 'Working'
            else:
                info[1] = 'Dead'
                info[2] = 'X'
            status += '|' + info[0].center(15) + '|' + info[1].center(15) + '|' + info[2].center(17) + '|' + '\n'

            info = ['watchdog Thread', '', '']
            if self.watchdog_thread.isAlive():
                info[1] = 'Alive'
                if self.events['watchdog'].isSet():
                    info[2] = 'Idle'
                else:
                    info[2] = 'Working'
            else:
                info[1] = 'Dead'
                info[2] = 'X'
            status += '|' + info[0].center(15) + '|' + info[1].center(15) + '|' + info[2].center(17) + '|' + '\n'
            for i in range(51):
                status += '-'

            status += '\n'

            status += '-->Information regarding power management:\n'
            if sysManager.getState() == 'Charging':
                chargingTime = sysManager.getChargingTime()
                status += 'On PowerLine '
                status += 'SMSGate\'s battery is currently charging LEVEL=%d%% EToC=%dh %dm \n' % (
                    sysManager.getBattCap() / defaultBattCap * 100, int(chargingTime / 60), int(chargingTime % 60))
            elif sysManager.getState() == 'Discharging':
                dischargingTime = sysManager.getDischargingTime()
                status += 'On Battery '
                status += 'SMSGate\'s battery is currently discharging LEVEL=%d%% EToD=%dh %dm \n' % (
                    sysManager.getBattCap() / defaultBattCap * 100, int(dischargingTime / 60), int(dischargingTime % 60))
            else:
                status += 'On PowerLine '
                status += 'SMSGate\'s battery is Fully Charged! \n'
            status += '\n'
            status += '-->Information about hardware gsmModem:\n'
            gsmModem.lock.acquire()
            try:
                if gsmModem.checkNwReg(5):
                    signal_stat = gsmModem.getSignalStat()
                    status += 'gsmModem is registered to network, GSM signal is %s/7 level, ' % signal_stat
                else:
                    status += 'gsmModem is not registered to network! '

                gsmModem.refreshStat(True)
                if gsmModem.status:
                    status += 'and its status is: alive\n\n'
                else:
                    status += 'and its status is: dead\n\n'

            finally:
                if gsmModem.lock.locked():
                    gsmModem.lock.release()
            return status
        elif weight == 'Light':
            signal_stat = ''
            notReg = False
            gsmModem.lock.acquire()
            try:
                if gsmModem.checkNwReg(5):
                    signal_stat = gsmModem.getSignalStat()
                else:
                    notReg = True
                gsmModem.refreshStat(True)
                if gsmModem.status:
                    QM95Sts = True
                else:
                    QM95Sts = False
            finally:
                if gsmModem.lock.locked():
                    gsmModem.lock.release()

            status = 'Resources: gsmModem is %s, signal: %s, status: %s and Email is %s.' % (
                'Locked' if gsmModem.lock.locked() else 'Released',
                str(signal_stat) + '/7' if not notReg else 'NOT registered, ',
                'On' if QM95Sts else 'Off',
                'Locked' if email.lock.locked() else 'Released')
            status += 'Threads: Email: %s,%s SMS: %s,%s FS: %s,%s powerMng: %s,%s watchdog: %s,%s. ' % (
                'Alive' if self.email_thread.isAlive() else 'X', 'Working' if self.events['email'].isSet() else 'Idle',
                'Alive' if self.sms_thread.isAlive() else 'X', 'Working' if self.events['sms'].isSet() else 'Idle',
                'Alive' if self.fs_thread.isAlive() else 'X', 'Working' if self.events['fs'].isSet() else 'Idle',
                'Alive' if self.powerMng_thread.isAlive() else 'X',
                'Working' if self.events['powerMng'].isSet() else 'Idle',
                'Alive' if self.watchdog_thread.isAlive() else 'X',
                'Working' if self.events['watchdog'].isSet() else 'Idle',)

            status += 'Power management:'
            if sysManager.getState() == 'Charging':
                chargingTime = sysManager.getChargingTime()
                status += 'On PowerLine, '
                status += 'batt is charging LEVEL=%d%% EToC=%dh %dm.' % (
                    sysManager.getBattCap() / defaultBattCap * 100, int(chargingTime / 60), int(chargingTime % 60))
            elif sysManager.getState() == 'Discharging':
                dischargingTime = sysManager.getDischargingTime()
                status += 'On Battery, '
                status += 'batt is currently discharging LEVEL=%d%% EToD=%dh %dm.' % (
                    sysManager.getBattCap() / defaultBattCap * 100, int(dischargingTime / 60), int(dischargingTime % 60))
            else:
                status += 'On PowerLine,'
                status += 'batt is Fully Charged!'

            return status

    def outputLiveStatus(self, signum, frame):
        if self.statusEvents['toFile'].isSet():
            status = self.getStatus('Heavy')
            # TODO save somehow the status var to file
            self.statusEvents['toFile'].clear()
        elif self.statusEvents['toEmail'].isSet():
            status = self.getStatus('Heavy')
            # TODO send somehow the status var to Email
            self.statusEvents['toEmail'].clear()
        elif self.statusEvents['toSMS'].isSet():
            status = self.getStatus('Light')
            gsmModem.lock.acquire()
            # TODO send somehow the status var to SMS
            if gsmModem.lock.locked():
                gsmModem.lock.release()
            self.statusEvents['toSMS'].clear()
        else:  # it came from CLI from sudo service statusgsm
            status = self.getStatus('Heavy')
            f = file('/var/smsgate/livestatus.txt', 'w')
            f.write(status)
            f.close()

    def systemSetup(self):
        Logger.info('SMSGate system is starting the Setup procedures right now')

        time.sleep(1)
        try:
            sysManager.hwSetup()
        except GPIOSetupError:
            Logger.error('GPIOSetupError while trying to setup the GPIO pins...')
        except:
            Logger.error('Unknown Error while trying to setup the GPIO pins...')
        else:
            Logger.info('GPIO pins were successfully setup.')

        time.sleep(1)
        try:
            serialCOM.startConnection()
        except SerialStartError:
            Logger.error('SerialStartError while trying to start serial communication...')
        except SerialSetupError:
            Logger.error('SerialSetupError while trying to start serial communication...')
        except:
            traceback.print_exc()
            Logger.error('Unknown error while trying to start serial communication...')
        else:
            Logger.info('Serial communication setup procedures completed successfully.')

        time.sleep(1)
        try:
            gsmModem.powerOn()
        except ModemAlreadyOnError:
            Logger.warning('GSM Modem is already powered on...')
        except ModemPowerOnError:
            Logger.error('GSM Modem was not powered on...')
        except:
            Logger.error('Unknown error while trying to start GSM Modem...')
        else:
            Logger.info('GSM Modem is now powered on.')


        time.sleep(1)

        #TODO try except here ASAP!!
        gsmModem.setup()
        gsmModem.deleteMulSMS('ALL')
	
        ok=True	
        while (ok):
            sysManager.startPPP()
            ok=not sysManager.testGPRSping()
            if(ok):
                Logger.error('GPRS initialization not completed... Retry in a few seconds seconds')

        Logger.info('GPRS initialization compelted.')

        # email.setup()
        # TODO phonebook.setup itself, i should setup it here and trat an error otherwise
        Logger.info('SMSGate system Setup procedures completed.P0EHALI')

    def systemQuit(self):
        Logger.info('SMSGate system is starting the Quit procedures right now')

        try:
            gsmModem.powerOff()
        except ModemAlreadyOffError:
            Logger.warning('GSM Modem is already powered off...')
        except ModemPowerOffError:
            Logger.error('GSM Modem was not powered off...')
        except:
            Logger.error('Unknown error while trying to stop GSM Modem...')
        else:
            Logger.info('GSM Modem is now powered off.')

        if (not sysManager.stopPPP()):
            Logger.error('GPRS final stop error ...')
        else:
            Logger.info('GPRS stop compelted!')

        try:
            serialCOM.stopConnection()
        except SerialStopError:
            Logger.error('SerialStopError while trying to stop serial communication...')
        except:
            Logger.error('Unknown Error while trying to stop serial communication...')
        else:
            Logger.info('Serial communication was successfully closed.')

        try:
            sysManager.hwRelease()
        except GPIOReleaseError:
            Logger.error('GPIOSetupError while trying to release the GPIO pins...')
        except:
            Logger.error('Unknown Error while trying to release the GPIO pins...')
        else:
            Logger.info('GPIO pins were successfully released.')

        Logger.info('SMSGate system Quit procedures completed.')

    def run(self):
        self.isrunning = True
        signal.signal(signal.SIGUSR1, self.outputLiveStatus)
        signal.signal(signal.SIGTERM, self.killThreads)

        try:
            while self.isrunning:
                time.sleep(5)
        finally:
            self.isrunning = False


#Class objects
daemon = Daemon('/var/smsgate/smsgate.pid')
