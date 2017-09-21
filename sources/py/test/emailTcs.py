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
# NAME: emailTcs.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains a test case for Email class

############################################################################################################################################

import unittest
from emailClass import *
from time import *


def suite():
    suite = unittest.TestSuite()
    suite.addTest(EmailWidgetTestCase('test_send_email'))
    suite.addTest(EmailWidgetTestCase('test_retrieve_email'))
    suite.addTest(EmailWidgetTestCase('test_send_multiemail'))
    return suite


class EmailWidgetTestCase(unittest.TestCase):
    """
    This class tests the sendMail and getMail methods from Email class by sending an e-mail to its own address
    and then reading the new income mail. If the sent mail does not corresponds to the received one, there is an error.
    """


    def setUp(self):
        self.emailWidget = Email()
        self.esubject = 'Weathercast'
        self.ebody = 'This is a test e-mail send from EmailWidgetTestCase class automatically! Today it is a rainy day!'
        self.sender_name = 'Petre Adrian-Razvan'
        self.eaddress = 'raspberry.iot95@gmail.com'

        self.multino=5

    def tearDown(self):
        self.emailWidget = None

    def test_send_email(self):
        # send an e-mail to yourself
        self.emailWidget.setup()
        self.emailWidget.sendMail(self.sender_name, self.eaddress, self.esubject, self.ebody)
        self.emailWidget.quit()

        # check if you received it and delete it
        self.emailWidget.setup()
        self.assertEqual(int(self.emailWidget.getNoEmail()), 1, "No. of Email is not 1!")
        self.emailWidget.deleteMail(1)
        self.emailWidget.quit()

    def test_retrieve_email(self):
        # send an e-mail to yourself
        self.emailWidget.setup()
        self.emailWidget.sendMail(self.sender_name, self.eaddress, self.esubject, self.ebody)
        self.emailWidget.quit()

        #check if the received email is correct
        self.emailWidget.setup()
        new_mail = self.emailWidget.getMail(1)
        self.assertEqual(new_mail['From'], self.sender_name + " <" + self.eaddress + ">", "From is not the same!")
        self.assertEqual(new_mail['To'], self.eaddress, "To is not the same!")
        self.assertEqual(new_mail['Subject'], self.esubject, "Subject is not the same!")
        self.assertEqual(new_mail['Body'], self.ebody, "Body is not the same!")
        self.emailWidget.deleteMail(1)
        self.emailWidget.quit()

    def test_send_multiemail(self):
        # send some e-mails to yourself
        self.emailWidget.setup()
        for i in range (self.multino):
            self.emailWidget.sendMail(self.sender_name, self.eaddress, self.esubject+str(i), self.ebody)
        self.emailWidget.quit()

        #check if the received emails are correct
        self.emailWidget.setup()
        self.assertEqual(self.multino,self.emailWidget.getNoEmail(),'Not all mails arrived in inbox!')
        for i in range (self.multino):
            new_mail = self.emailWidget.getMail(i+1)
            self.assertEqual(new_mail['From'], self.sender_name + " <" + self.eaddress + ">", "From is not the same!")
            self.assertEqual(new_mail['To'], self.eaddress, "To is not the same!")
            self.assertEqual(new_mail['Subject'], self.esubject+str(i), "Subject is not the same!")
            self.assertEqual(new_mail['Body'], self.ebody, "Body is not the same!")
            self.emailWidget.deleteMail(i+1)

        self.emailWidget.quit()


mysuite = suite()
if __name__ == '__main__':
    unittest.main()
