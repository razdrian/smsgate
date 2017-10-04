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
# NAME: peopleCls.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of People class

############################################################################################################################################
from xml.dom import minidom
from globalPara import *
import json

class People:
    """
    self.people  -> is a list of dictionaries
                 -> each dictionary in people has the following keys: ID Name PhoneNo Email and Group
                 -> for the latter, Group is a list, beacuse a person can be part of multiple groups
    self.gropups -> list of groups in the phonebook
    """

    people = []
    groups = []

    def __init__(self):
        self.people = []
        self.groups = []
        if self.setup() is True:
            Logger.error('Error while opening/reading phonebook.json')


    def setup(self):
        """
        setup the people dictionary and groups list with new information from the XML file

        @return: True if an error occurred while reading json or None otherwise
        """
        try:

            with open(phonebook_path + 'phonebook.json') as data_file:
                data = json.load(data_file)

            self.people = data['employees']
            self.groups = data['groups'].keys()

            for employee in self.people:
                employee.update({'Group':[]})
                for group in data['groups']:
                    if int(employee['ID']) in data['groups'][group]:
                        employee['Group'].append(group)

        except:
            return True


        return None

    def getGroups(self):
        return self.groups

    def getGroupConts(self, group, option):
        """
        It is the duty of the callee function to give the group without spaces in corners and ALL LOWERNAMES

        @param option:
            -   if it is PhoneNo return numbers of the group members
            -   if it is Email return email of the group members
        @param group:
            -   the group whose member's phone numbers are wanted,
            -   can take spaces in the right or left eg. '  Admins  '
            -   is not case sensitive ' Admins ' is the same as 'admIns'
        @return: None if not found, list of Phone No. if option is PhoneNo of list of e-mails if option is Email
        """
        numbers = []
        emails = []
        if group in self.groups:
            for employee in self.people:
                if group in employee['Group']:
                    numbers.append(employee['PhoneNo'])
                    emails.append(employee['Email'])
            if option == 'PhoneNo':
                return numbers
            else:
                return emails
        else:
            Logger.warning('Group %s not found!' % group)
            return None

    def getName(self, phoneno):
        """
        It is the duty of the callee function to give the phoneno without spaces in corners and without +4..

        @param phoneno: phone number for what is wanted the owner
        @return: the owner's name from database or None
        """
        for employee in self.people:
            if employee['PhoneNo'] == phoneno:
                return employee['Name']
        return None

    def checkPhoneNo(self, phoneno):
        """
        Checks if a Phone Number is in the PhoneBook and return True if so and False if not

        It is the duty of the callee function to give the phoneno without spaces in corners and without +4..

        @param phoneno: Phone NUmber to be checked
        @return: True or False
        """
        for employee in self.people:
            if employee['PhoneNo'] == phoneno:
                return True
        return False

    def checkEmail(self, email):
        """
        Checks if an Email address is in the PhoneBook and return True if so and False if not

        It is the duty of the callee function to give the email without spaces in corners

        @param email: email address to be checked
        @return: True or False
        """
        for employee in self.people:
            if employee['Email'] == email:
                return True
        return False


