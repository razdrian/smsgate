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
# NAME: handCls.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of the Handlers class

############################################################################################################################################
"""
Example of input info from different flows from SMS gate's point of view:
* Received Mail format:
    Single sender:   Subject: #0724289644#6FA32E
    Multiple sender: Subject: #0724289644#0724289644#6FA32E
    Group sender:    Subject:#Admin#6FA32E
    last 6 Hexa digits are a key defined in global_Parameters to prevent spam
                     Body: This is an e-mail send from RPi to your Phone! (nu more than 160 ch. or only the first 160 will be sent)

* Received SMS format:
    The format of the SMS MUST be the following: <command>#<recipient1>#<recipient2>#<recipient3>#<Mail Subject>#<Content>
        -> recipient1 or any other recipient can be either ANY email address or a group from phonebook
        -> recipient2, recipient3 and so on are THE ONLY OPTIONAL
        -> if No mail subject is needed YOU MUST leave it empty eg. eml#admin##No subject email
    IF you want to send an e-mail:
        single recipient: eml$#raz.adrian95@gmail.com#Emmergency from Petre#I have no internet conn. Call me ASAP!
        multiple recipients: eml#raz.adrian95@gmail.com#raspberry.iot95@gmail.com#Bad day#I have lost my toothbrush!
        group recipients: eml#Admin#EMMERCENCY#The power went off!

    IF you want to execute a command:
        single command: cmd#backup_sql.sh
        multiple commands: cmd#backup_sql.sh#restart_server.sh (executed in this order)

    IF you want to save to file:
        s2f#sputnik#This text will be saved in output_path dir with the name sputnik

* Inputted FileSys:
    IF you want to send an e-mail:
        The file MUST be saved in input_path with the format <file>.email  eg. sql_error.email
            single recipient:
                Destination: raz.adrian95@gmail.com
            multiple recipients:
                Destination: raz.adrian95@gmail.com,raspberry.iot95@gmail.com
            group recipients:
                Destination: Admin
            Subject: My Sql has stopped
            Text: Today at around 9PM the mySQL server has stopped and cowardly refused to start!

    IF you want to send a SMS:
        The file MUST be saved in input_path with the format <file>.sms  eg. apache_error.sms
            sigle recipient:
                Destination: 0724289644
            multiple recipients:
                Destination: 0724289644,0724289644
            group recipients:
                Destination: Users
            Text: Today the apache server died but was resurrected!
"""

from globalPara import *
from peopleCls import *
from emailCls import *
from daemonCls import *
from gsmCls import *
import subprocess


class Handlers:
    """
     only from known numbers ----> SMS ------>   * sendEmail                       ----> send to anyone you like an e-mail
                                                 * executeCommand                  ----> execute if command is in command_path
                                                 * saveToFile (in output_path FS)  ----> save content in output_path
     only specific subj. format -> Email ---->   * sendSMS                         ----> send to anyone if the Sub. format is correct
     only specific FS format ----> FileSys -->   * sendEmail                       ----> only to emails in the phonebook
                                                 * sendSMS                         ----> only to phone No.s in the phonebook
    If the number is not known or the fromat of the SMS/FS/email ----------------------> log warning
    """

    def __init__(self, people, email, modem):
        self.people = people
        self.email = email
        self.modem = modem

    def validMailAddr(self, address):
        """
        Checks if a Mail address is VALID meaning:
            - No special Email chars in it, I{spec_EMLchars} defined in global_Parameters
            - Has a domain registered in I{allowed_domains}, global_Parameters list
        @param address: email address to be checked if valid or not
        @return: True is email address is valid or False if not
        """
        address = address.strip()
        if address.find('@') == -1:
            return False
        address = address.split('@')
        if len(address) != 2:
            return False
        if not address[1] in allowed_domains:
            return False
        for special_char in spec_EMLchars:
            if address[0].find(special_char) != -1:
                return False
        return True

    def validPhoneNo(self, phoneno):
        """
        checks if a phone number is VALID meaning it has exactly 10 chars ALL being digits

        @param phoneno: phone number is classic format eg.0724289644
        @return: True if phone number is valid and False if not
        """

        phoneno = phoneno.strip()
        if len(phoneno) != 10:
            return False
        if not phoneno.isdigit():
            return False
        return True

    def validFileName(self, filename):
        """
        Checks if a filename is VALID meaning:
            - No special File Sys chars in it, I{spec_FSchars} defined in global_Parameters
        @param filename: the file name to be checked
        @return: True if file name is valid and False if not
        """
        for special_char in spec_FSchars:
            if filename.find(special_char) != -1:
                return False
        return True

    def handleSMS(self, sender_no, sms):
        """
        From a received SMS there there are 3 possible directions: sendEmail, executeCommand or saveToFile

        @param sender_no: Sender's phone in international format or classic!!! eg. +40724289644 or 0724289644
        @param sms: SMS message to be handled
        @return: -1 if could not sendMail ONLY due to connection and 1 if succeed (also if one mail had bad format)
        """
        checked_email = []
        sender_no = sender_no.strip()
        if sender_no[0] == '+':
            sender_no = sender_no[2:]

        if self.people.checkPhoneNo(sender_no):
            raw_sms = sms
            sms = sms.split('#')

            if sms[0].strip().lower() == 'eml':
                if len(sms) < 4:  # must be at least 4 : <command>#<sender_name>#<Subject>#<Body>
                    Logger.warning('Wrong eml action SMS format from %s!' % sender_no)
                    return
                sender_name = self.people.getName(sender_no)
                for recipient in sms[1:len(sms) - 2]:  # iterate in recipients attributes of the SMS
                    recipient = recipient.strip().lower()
                    if recipient in self.people.getGroups():  # if recipient is a group
                        Logger.info('Sending email to all the people in %s group' %recipient)
                        to_list = self.people.getGroupConts(recipient, 'Email')
                        for toMail in to_list:
                            if not toMail in checked_email:
                                self.email.lock.acquire()
                                if self.email.testSMTPping():
                                    try:
                                        if self.email.sendMail(sender_name, toMail, sms[len(sms) - 2].strip(),
                                                               sms[len(sms) - 1]) == -1:
                                            if self.email.lock.locked():
                                                self.email.lock.release()
                                            return -1
                                    finally:
                                        if self.email.lock.locked():
                                            self.email.lock.release()
                                    checked_email.append(toMail)
                                else:
                                    Logger.error('Server in unreachable! watchdog will restart ppp connection in a moment...')
                                    if self.email.lock.locked():
                                        self.email.lock.release()
                                    return -1

                    elif self.validMailAddr(recipient):  # if recipient is a valid Mail address
                        if not recipient in checked_email:
                            self.email.lock.acquire()
                            if self.email.testSMTPping():
                                try:
                                    if self.email.sendMail(sender_name, recipient, sms[len(sms) - 2].strip(),
                                                           sms[len(sms) - 1]):
                                        if self.email.lock.locked():
                                            self.email.lock.release()
                                        return -1
                                finally:
                                    if self.email.lock.locked():
                                        self.email.lock.release()
                                checked_email.append(recipient)
                            else:
                                Logger.error('Server in unreachable! watchdog will restart ppp connection in a moment...')
                                if self.email.lock.locked():
                                    self.email.lock.release()

                    else:
                        Logger.warning('%s is not a valid E-mail address or gropup name!' % recipient)
                return 1


            elif sms[0].strip().lower() == 'cmd':
                if len(sms) < 2:  # must be at least 2 : <command>#<script1>
                    Logger.warning('Wrong cmd action SMS format from %s!' % sender_no)
                    return
                for script in sms[1:]:
                    script = script.strip()
                    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    result = process.communicate('find ' + commands_path + ' -name ' + script)
                    if result[0]:
                        Logger.info('Command %s was found and will be executed now' % script)
                        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        result = process.communicate(result[0])
                        Logger.info('Command %s executed. Result is: %s' %(script, result))
                    else:
                        Logger.warning('Command %s was NOT found!' % script)
                return 1

            elif sms[0].strip().lower() == 's2f':
                if len(sms) != 3:  # must be exactly 3 : <command>#<output_file_name>#<text>
                    Logger.warning('Wrong s2f action SMS format from %s!' % sender_no)
                    return
                file_name = sms[1].strip()
                if self.validFileName(file_name):
                    body = sms[2]
                    command1 = 'touch ' + txt_out_path
                    command2 = 'echo \"' + body + "\" > " + txt_out_path + file_name
                    process = subprocess.Popen("{}; {}".format(command1, command2), stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                               close_fds=True)
                    result, error = process.communicate()
                    if result or error:
                        Logger.warning('Error creating new file in %s folder' % txt_out_path)
                    else:
                        Logger.info('Succes creating %s file!' % file_name)
                        return 1
                else:
                    Logger.warning('%s is not a valid file name!' % file_name)

            elif sms[0].strip().lower() == 'ord':
                    if sms[1].strip().lower() == 'getsts':
                        #TODO send to sender an sms with the status ('Light') of the system
                        pass
                    elif sms[1].strip().lower() == 's2fsts':
                        #TODO save to file current status of the system
                        pass
                    elif sms[1].strip().lower() == 's2flog':
                        #TODO save to file logging of current day of the system
                        pass
                    else:
                        Logger.warning('Unknown ord From: %s Content: %s' % (sender_no, raw_sms))
			return 1
            else:
                Logger.warning('Unknown SMS content From: %s Content: %s' % (sender_no, raw_sms))
		return 1

        else:
            Logger.warning('Unauthorized SMS message From: %s Content: %s' % (sender_no, sms))

    def handleEmail(self, email):
        """
        The email parameter is a dictionary in the format returned by Email getMail() method
            - 'From'    : Name and e-mail address of the sender eg. Petre Adrian Razvan <raz.adrian95@gmail.com>
            - 'To'      : The receiver's mail  eg.raspberry.iot95@gmail.com
            - 'Subject' : The Subject of the mail
            - 'Body' : The body of the mail / the payload

        The application is restricted with only one possible direction for email, which is sendSMS

        @param email: the email to be handled
        @return: -1 if failure due to QuectelM95 connection and 1 if succeded (also if BAD address/format number)
        """

        checked_numbers = []
        subject = email['Subject'].split('#')
        if subject[-1].strip().upper() != email_key or len(subject) < 3:
            Logger.warning('Wrong subject format for email. From: %s Subject: %s Body: %s' % (
                email['From'], email['Subject'], email['Body']))
        else:
            if subject[0].strip().lower() == 'sms':
                for recipient in subject[1:- 1]:  # iterate in recipients attributes of the mail
                    recipient = recipient.strip().lower()
                    if recipient in self.people.getGroups():  # if recipient is a group
                        for toNum in self.people.getGroupConts(recipient, 'PhoneNo'):
                            if not toNum in checked_numbers:
                                Logger.info("Sending '%s' SMS to %s in group %s" % (email['Body'][:-1], toNum, recipient))
                                self.modem.lock.acquire()
                                try:
                                    if self.modem.sendSMS(toNum, '129', email['Body']) == 1:
                                        return -1
                                finally:
                                    if self.modem.lock.locked():
                                        self.modem.lock.release()
                                checked_numbers.append(toNum)
                    elif self.validPhoneNo(recipient):  # if recipient is a valid PhoneNo
                        if not recipient in checked_numbers:
                            Logger.info("Sending '%s' SMS to %s " % (email['Body'][:-1], recipient))
                            self.modem.lock.acquire()
                            try:
                                if self.modem.sendSMS(recipient, '129', email['Body']) == 1:
                                    return -1
                            finally:
                                if self.modem.lock.locked():
                                    self.modem.lock.release()
                            checked_numbers.append(recipient)
                    else:
                        Logger.warning('%s is not a valid phone number or group!' % recipient)
                return 1

            elif subject[0].strip().lower() == 'cmd':
                if len(subject) < 3:  # must be at least 3 : cmd#<script1>#email_key
                    Logger.warning('Wrong cmd action Email format from %s!' % email['From'])
                    return
                for script in subject[1:-1]:
                    script = script.strip()
                    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    result = process.communicate('find ' + commands_path + ' -name ' + script)
                    if result[0]:
                        Logger.info('Command %s was found and will be executed now' % script)
                        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        result = process.communicate(result[0])
                        Logger.info('Command %s executed. Result is: %s' %(script, result))
                    else:
                        Logger.warning('Command %s was NOT found!' % script)
                return 1

            elif subject[0].strip().lower() == 's2f':
                if len(subject) != 3:  # must be exactly 3 : <command>#<output_file_name>#email_key
                    Logger.warning('Wrong s2f action Email format from %s!' % email['From'])
                    return
                file_name = subject[1].strip()
                if self.validFileName(file_name):
                    body = email['Body']
                    command1 = 'touch ' + txt_out_path
                    command2 = 'echo \"' + body + "\" > " + txt_out_path + file_name
                    process = subprocess.Popen("{}; {}".format(command1, command2), stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                               close_fds=True)
                    result, error = process.communicate()
                    if result or error:
                        Logger.warning('Error creating new file in %s folder' % txt_out_path)
                    else:
                        Logger.info('Succes creating %s file!' % file_name)
                        return 1
                else:
                    Logger.warning('%s is not a valid file name!' % file_name)

            elif subject[0].strip().lower() == 'ord':
                if subject[1].strip().lower() == 'getsts':
                    #TODO send to sender an email with the status ('Heavy') of the system
                    pass
                elif subject[1].strip().lower() == 's2fsts':
                    #TODO save to file current status of the system
                    pass
                elif subject[1].strip().lower() == 's2flog':
                    #TODO save to file logging of current day of the system
                    pass
                else:
                    Logger.warning('Unknown ord From: %s Subject: %s' % (email['From'], email['Subject']))
            else:
                Logger.warning('Unknown Email content From: %s Content: %s Body: %s' % (email['From'], email['Subject'], email['Body']))

    def handleFS(self, path):
        """
        TODO To CHANGE HERE! ....

        This handle will check input_path (global_Parameter) and if there is a new file will parse and delete it

        The two possible direction from here are sendEmail or sendSMS

        files stored in input_path having the sendSMS direction must have the name *.sms eg: apache_error.sms

        files stored in input_path having the sendEmail direction must have the name *.email eg: mysql_error.mail

        @return: -1 if failure due to QuectelM95 Connection or RPiemail Connection and 1 if succeed
        """
        checked_emails = []
        checked_numbers = []
        if '.sms' in path:
            try:
                f = open(path, 'r')
                raw_file = f.read()
            except:
                Logger.error('Unable to open/read file/from file %s' %path)
                return -1
            finally:
                if raw_file.find('To:') == -1 or raw_file.find('Body:') == -1:
                    Logger.error('%s file has no corresponding tags [To:,Body:]!' % path)
                else:
                    recipients = raw_file[3:raw_file.find('Body:')]
                    recipients = recipients.replace('\n', '').strip()
                    body = raw_file[raw_file.find('Body:') + 5:]
                    body = body.strip()
                    if len(body) > default_SMSsize:
                        Logger.warning('File %s has Body too large, only %s chars will be considered' %(path, default_SMSsize))
                        body = body[0:default_SMSsize]
                    recipients = recipients.split('#')
                    for recipient in recipients:  # iterate in recipients attributes of file
                        recipient = recipient.strip().lower()
                        if recipient in self.people.getGroups():  # if recipient is a group
                            to_list = self.people.getGroupConts(recipient, 'PhoneNo')
                            for toNum in to_list:
                                if not toNum in checked_numbers:
                                    Logger.info("Sending '%s' SMS to %s in group %s" % (body, toNum, recipient))
                                    self.modem.lock.acquire()
                                    try:
                                        if self.modem.sendSMS(toNum, '129', body) == 1:
                                            if self.modem.lock.locked():
                                                self.modem.lock.release()
                                            return -1
                                    except:
                                        return -1
                                    finally:
                                        if self.modem.lock.locked():
                                            self.modem.lock.release()
                                    checked_numbers.append(toNum)
                        elif self.people.checkPhoneNo(recipient):  # if recipient is a valid PhoneNo
                            if not recipient in checked_numbers:
                                Logger.info("Sending '%s' SMS to %s " % (body, recipient))
                                self.modem.lock.acquire()
                                try:
                                    if self.modem.sendSMS(recipient, '129', body) == 1:
                                        if self.modem.lock.locked():
                                            self.modem.lock.release()
                                        return -1
                                except:
                                    return -1
                                finally:
                                    if self.modem.lock.locked():
                                        self.modem.lock.release()
                                checked_numbers.append(recipient)
                        elif self.validPhoneNo(recipient):
                            Logger.warning('Could not send SMS to unauthorized phone number %s' % recipient)
                        else:
                            Logger.warning('%s is not a valid phone number or gropup name!' % recipient)
                    return 1

        elif '.eml' in path:
            try:
                f = open(path, 'r')
                raw_file = f.read()
            except:
                Logger.error('Unable to open/read file/from file %s' %path)
                return -1
            finally:
                if raw_file.find('To:') == -1 or raw_file.find('From:') == -1 or raw_file.find('Subject:') == -1 or raw_file.find('Body:') == -1:
                    Logger.error('%s file has no corresponding tags [To:,From:,Subject:,Body:]!' % path)
                else:
                    recipients = raw_file[3:raw_file.find('From:')]
                    recipients = recipients.replace('\n', '').strip()
                    sender_name = raw_file[raw_file.find('From:') + 5:raw_file.find('Subject:')]
                    sender_name = sender_name.replace('\n', '').strip()
                    subject = raw_file[raw_file.find('Subject:') + 8:raw_file.find('Body:')]
                    subject = subject.replace('\n', '').strip()
                    body = raw_file[raw_file.find('Body:') + 5:].strip()
                    recipients = recipients.split('#')
                    for recipient in recipients:  # iterate in recipients attributes of file
                        recipient = recipient.strip().lower()
                        if recipient in self.people.getGroups():  # if recipient is a group
                            Logger.info('Sending email to all the people in %s group' %recipient)
                            to_list = self.people.getGroupCont(recipient, 'Email')
                            for toMail in to_list:
                                if not toMail in checked_emails:
                                    self.email.lock.acquire()
                                    if self.email.testSMTPping():
                                        try:
                                            if self.email.sendMail(sender_name, toMail, subject, body) == -1:
                                                if self.email.lock.locked():
                                                    self.email.lock.release()
                                                return -1
                                        except:
                                            return -1
                                        finally:
                                            if self.email.lock.locked():
                                                self.email.lock.release()
                                        checked_emails.append(toMail)
                                    else:
                                        Logger.error('Server in unreachable! watchdog will restart ppp connection in a moment...')
                                        if self.email.lock.locked():
                                            self.email.lock.release()

                        elif self.people.checkEmail(recipient):  # if recipient is a valid Email address
                            if not recipient in checked_emails:
                                self.email.lock.acquire()
                                if self.email.testSMTPping():
                                    try:
                                        if self.email.sendMail(sender_name, recipient, subject, body) == -1:
                                            if self.email.lock.locked():
                                                self.email.lock.release()
                                            return -1
                                    except:
                                        return -1
                                    finally:
                                        if self.email.lock.locked():
                                            self.email.lock.release()
                                    checked_emails.append(recipient)
                                else:
                                    Logger.error('Server in unreachable! watchdog will restart ppp connection in a moment...')
                                    if self.email.lock.locked():
                                        self.email.lock.release()

                        elif self.validMailAddr(recipient):
                            Logger.warning('Could not send email to unauthorized email address %s' % recipient)
                        else:
                            Logger.warning('%s is not a valid E-mail address or gropup name!' % recipient)
                    return 1

        else:
            Logger.error("%s has a wrong FS extension! Only *.sms and *.mail are allowed!" % path)
