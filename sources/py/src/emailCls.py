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
# NAME: emailCLs.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of Email class

############################################################################################################################################

import imaplib
import smtplib
import threading
from email.parser import Parser
from globalPara import *
import time
import subprocess


class Email:
    """
    The Email class describes a Email connection and has proper methods to retrieve or send an email

    It has a self.POPstatus bool variable. True means that Email obj. is currently connected to server

    It uses POP Connection to retrieve email from server and SMTP to send mail to server
    """

    def __init__(self):
        self.lock = threading.Lock()
        pass

    def setup(self):
        """
        poplib.POP3  implements the actual POP3 protocol.If no port is set, the standard POP 110 port is used

        poplib.POP3_SSL connects to POP via a SSL socket. If no port is set, the standard POPviaSSL 995 is used

        UNTIL you RUN setup() the mails which were sent after the last setup() call WILL NOT BE SEEN in python!!!

        @return: 0 if connection is setup w/home/adrian/GitHub/mailboxith success and -1 if fail to comm
        """

        try:
            self.IMAPConn = imaplib.IMAP4_SSL('imap.gmail.com')
            self.IMAPConn.login(email_user, email_pwd)
            self.IMAPConn.select()
        except:
            Logger.error('Could not login to email via IMAP4_SSL !')
            return -1

        # use SMTP to send email to SMTPConn
        try:
            self.SMTPConn = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
            self.SMTPConn.ehlo()  # Identify yourself to an ESMTP SMTPConn using EHLO.
            self.SMTPConn.starttls()  # Put the SMTP connection in TLS (Transport Layer Security) mode.
            self.SMTPConn.login(email_user, email_pwd)
        except:
            Logger.error('Could not login to email via SMTP!')
            return -1
        finally:
            return 0

    def setupSMTP(self):
        # use SMTP to send email to SMTPConn
        try:
            self.SMTPConn = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
            self.SMTPConn.ehlo()  # Identify yourself to an ESMTP SMTPConn using EHLO.
            self.SMTPConn.starttls()  # Put the SMTP connection in TLS (Transport Layer Security) mode.
            self.SMTPConn.login(email_user, email_pwd)
        except:
            Logger.error('Could not login to email via SMTP!')
            return -1
        finally:
            return 0

    def setupIMAP(self):
        try:
            self.IMAPConn = imaplib.IMAP4_SSL('imap.gmail.com')
            self.IMAPConn.login(email_user, email_pwd)
            self.IMAPConn.select()
        except:
            Logger.error('Could not login to email via IMAP4_SSL !')
            return -1
        finally:
            return 0

    def testSMTPconn(self):
        """

        @return: True if SMTP is still alive and False if not
        """
        self.setupSMTP()
        try:
            status = self.SMTPConn.noop()[0]
        except:
            status = -1
        self.quitSMTP()
        return True if status == 250 else False

    def testIMAPconn(self):  # not working
        """

        @return: True if IMAP is still alive and False if not
        """
        self.setupIMAP()
        startTime = time.time()
        while (time.time() - startTime < 5):
            try:
                status = self.IMAPConn.check()
                self.quitIMAP()
                return True if status[0] == 'OK' else False
            except:
                self.quitIMAP()
                return False
        self.quitIMAP()
        return False

    def testSMTPping(self):
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = process.communicate('ping ' + '-w ' + '1 ' + '-W ' + '3 ' + 'smtp.gmail.com')
        if result:
            return True
        elif error:
            return False

    def testIMAPping(self):
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = process.communicate('ping ' + '-w ' + '1 ' + '-W ' + '3 ' + 'imap.gmail.com')
        if result:
            return True
        elif error:
            return False

    def getNoEmail(self):
        """
        @return: number of new emails from box
        """
        self.setupIMAP()
        try:
            self.IMAPConn.list()
            # Out: list of "folders" aka labels in gmail.
            self.IMAPConn.select("inbox")  # connect to inbox.
            result, data = self.IMAPConn.uid('search', None, "ALL")  # search and return uids instead
            self.quitIMAP()
            return len(data[0])
        except:
            self.quitIMAP()
            Logger.error('Could not retrieve from IMAPConn!')
            return

    def getEmailUIDs(self):
        """

        @return:
        """
        self.setupIMAP()
        try:
            self.IMAPConn.list()
            # Out: list of "folders" aka labels in gmail.
            self.IMAPConn.select("inbox")  # connect to inbox.
            result, data = self.IMAPConn.uid('search', None, "ALL")  # search and return uids instead
            self.IMAPConn.select()
            self.quitIMAP()
            return data[0]
        except:
            self.quitIMAP()
            Logger.error('Could not retrieve from IMAPConn!')
            return

    def getMail(self, email_uid):
        """
        The email is returned by getMail as a dictionary with the following format:

            -  'From'    : Name and e-mail address of the sender eg. Petre Adrian Razvan <raz.adrian95@gmail.com>
            -  'To'      : The receiver's mail  eg.raspberry.iot95@gmail.com
            -  'Subject' : The Subject of the mail
            -  'Body' : The body of the mail / the payload

        @param index: The index of the mail to be read
        @return: mail dictionary or None for fail communication
        """
        self.setupIMAP()
        parser = Parser()
        mail = {'From': 'A', 'To': 'A', 'Subject': 'A', 'Body': 'A'}
        try:
            self.IMAPConn.list()
            # Out: list of "folders" aka labels in gmail.
            self.IMAPConn.select("inbox")  # connect to inbox.
            result, data = self.IMAPConn.uid('search', None, "ALL")  # search and return uids instead
            self.IMAPConn.select()
            if not email_uid in data[0]:
                self.quitIMAP()
                Logger.error('Invalid Email UID!')
                return -1
            else:
                try:
                    result, data = self.IMAPConn.uid('fetch', email_uid, '(RFC822)')
                    raw_text = data[0][1]
                    # raw_text = "\n".join(raw_text[1])
                    email = parser.parsestr(raw_text)
                    mail['From'] = email.get('From')
                    mail['To'] = email.get('To')
                    mail['Subject'] = email.get('Subject')

                    if email.is_multipart():
                        # for part in email.get_payload():
                        mail['Body'] = email.get_payload()[0].get_payload()
                    else:
                        mail['Body'] = email.get_payload()
                    mail['Body'] = mail['Body'][:-1]
                    # TODO should I print Logger.info 'bout this new mail received?
                    self.quitIMAP()
                    return mail
                except:
                    self.quitIMAP()
                    Logger.error('Could not retrieve email from %s UID' % email_uid)
                    return -1
        except Exception as ex:
            self.quitIMAP()
            template = "Exception Ocuurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            Logger.error('Could not retrieve from IMAPConn!')
            Logger.error(message)
            return -1

    def sendMail(self, sender_name, recipient, subject, body):
        """
        recipient can be a single e-mail address such as joe@gmail.com

        recipient can also be a list of e-mail to send such as [joe@gmail.com, doe@yahoo.com]

        @param sender_name: The sender's name eg. Petre Adrian-Razvan
        @param recipient: e-mail address of the recipient
        @param subject: Subject of the mail, string variable
        @param body: Body of the mail, string variable
        @return: 0 if success and -1 if fails
        """
        self.setupSMTP()
        to = recipient if type(recipient) is list else [recipient]
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (sender_name, ", ".join(to), subject, body)

        try:
            self.SMTPConn.sendmail(sender_name, to, message)
            Logger.info('Email send! From: %s To: %s Subject: %s' % (sender_name, recipient, subject))
            self.quitSMTP()
            return 0
        except Exception as ex:
            self.quitSMTP()
            template = "Exception Ocuurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            Logger.error('Could not send using SMTP!')
            Logger.error(message)
            return -1

    def deleteMail(self, email_uid):
        """
        Delete the mail at the index index

        @param index: the index of the mail to be deleted
        @return: void
        """
        self.setupIMAP()
        try:
            self.IMAPConn.uid('STORE', email_uid, '+FLAGS', '(\Deleted)')
            self.IMAPConn.expunge()
            self.quitIMAP()
        except:
            self.quitIMAP()
            Logger.error('Could not delete mail at index %s' % email_uid)

    def quit(self):
        """
        Close the connection via the POP port

        -U{https://docs.python.org/2/library/poplib.html} :'On most servers deletions are not actually performed until QUIT'

        To take place, any delete command must pe followed by a quit() call
        @return: void
        """
        try:
            self.IMAPConn.close()
            self.IMAPConn.logout()
            Logger.info('Successfully closed and logged out from IMAP')
        except:
            Logger.error('Could not log out from IMAP')

        try:
            self.SMTPConn.quit()
            Logger.info('Successfully closed and logged out from SMTP')
        except:
            Logger.error('Could not log out from SMTP')

    def quitIMAP(self):
        try:
            self.IMAPConn.close()
            self.IMAPConn.logout()
            # Logger.info('Successfully closed and logged out from IMAP')
        except:
            Logger.error('Could not log out from IMAP')

    def quitSMTP(self):
        try:
            self.SMTPConn.quit()
            # Logger.info('Successfully closed and logged out from SMTP')
        except:
            Logger.error('Could not log out from SMTP')

    def restartIMAP(self):
        """
        restart the IMAP if possible
        @return: True if succeeded and False if not
        """
        self.IMAPConn.close()
        self.IMAPConn.logout()
        try:
            self.IMAPConn = imaplib.IMAP4_SSL('imap.gmail.com')
            self.IMAPConn.login(email_user, email_pwd)
            self.IMAPConn.select()
        except:
            Logger.error('Could not login to email via IMAP4_SSL !')
            return False
        Logger.info('IMAP conn successfully restarted')
        return True

    def restartSMTP(self):
        """
        restart SMTP if possible
        :return: True if succeeded and False if not
        """
        self.SMTPConn.quit()
        try:
            self.SMTPConn = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
            self.SMTPConn.ehlo()  # Identify yourself to an ESMTP SMTPConn using EHLO.
            self.SMTPConn.starttls()  # Put the SMTP connection in TLS (Transport Layer Security) mode.
            self.SMTPConn.login(email_user, email_pwd)
        except:
            Logger.error('Could not login to email via SMTP!')
            return False
        Logger.info('SMTP conn successfully restarted')
        return True
