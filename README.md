* Project Name: SMSGate 
* Descrtiption: Bridge between LAN and GSM using d-uGSM module (based on Quectel UG95) and Raspberry Pi 3
* Date: 2016-11-22 
* Author: Adrian-Razvan Petre 
* [Under AMIQ Education Program](http://www.amiq.com/consulting/education/)

## Application structure: ##
* The main app has three main flows : SMS, FS (file system) and POP(e-mail service).
* The main app will decide how to treat a command coming from a flow and redirect it to another flow.
* In the first implementation, the one described in the blog article an Ethternet connection was needed
* In the last implementeation available here as last version the internet connection comes from a PPP connetion from GPRS via the d-uGSM module


## Directory structure: ##
* smsgate/documents -> 
	* smsgate/documents/c-uGSM_module/  -> GSM docs, official http://itbrainpower.net/ sketch examples and the initial API provided by DragosIosub
	* smsgate/documents/documentation -> SMSGate User's Guide and Article (both docx and pdf files) 
	
* smsgate/sources -> executable code files for the SMSGate application 
	* smsgate/sources/ppp -> PPP start and stop scripts
	* smsgate/sources/py -> Python application source code
		* smsgate/sources/py/lib -> Library files and definition of some methods from GSM_modem class
		* smsgate/sources/py/src -> Python source files
		* smsgate/sources/py/test -> uitest cases for some basic features of the implemented classes
		* smsgate/sources/py/tmp -> scratchpad for python code snippets
	* smsgate/sources/sh -> scrips used in the work in progress stage

* smsgate/schematic -> cadence Capture and Allegro schematic design and documents (complete BOM and pdf schematics)
 	* smsgate/schematic/commandModule_v1_3 -> commandModule is the LEDs and RR push button Printed Circuit Board.
		* smsgate/schematic/commandModule_v1_3/allegro -> Cadence allegro files (brd files)
		* smsgate/schematic/commandModule_v1_3/documents -> commandModule BOM and pdf schematic
		* smsgate/schematic/commandModule_v1_3/gerberFiles -> production gerberFiles and drl file 
	* smsgate/schematic/datasheets -> pdf datasheet files for all the components in the desgn 
	* smsgate/schematic/powerModule_v1_3 ->  the main module of this system including the d-uGSM module and voltage regulators for both the 5V and 4V voltages required by the system. In the PCB version available here (v1_3) I2C connectors are externalized from the IDC10 connector to a CON2 for later use. This is also valid for the unused pins of the d-uSGM module (e.g. RI - ring indicator)
		* smsgate/schematic/powerModule_v1_3/allegro -> Cadence allegro files (brd files)
		* smsgate/schematic/powerModule_v1_3/documents -> powerModule BOM and pdf schematic
		* smsgate/schematic/powerModule_v1_3/gerberFiles -> production gerberFiles and drl file 

* smsgate/var_smsgate -> direcotry whose content must be copied in /var/smsgate at the first initialization of the SMSGate application on a brand new Rasbian OS. If this content is not copied in the /var/smsgate the python application will crash and give an error message. The template.eml and template.sms are two tempalte files for a new sms and email command. If this type of files are pasted in the input directory (/var/smsgate/input) the SMSGate daemon will parse them immediately and delete them after execution.


## Raspbian configuraton: ##
* Install Raspbian and mount its image
* Disable Raspberry Serial Console
* sudo raspi-config -> 8. Advanced Options -> A8. Serial -> Disable 
* Enable UART
* sudo vim /boot/config.txt and update enable_uart=0 to enable_uart=1 
* sudo apt-get install python3.
* edit $HOME/.bashrc and add export PYTHONPATH=$PYTHONPATH:$HOME/smsgate/src/py/lib:$HOME/smsgate/src/py/src


## Documentation links
* [itbrainpower original GSM project](http://itbrainpower.net/micro-GSM-shield-module-cuGSM/GSM-micro-shield-board-module-RaspberryPI-Arduino-c-uGSM-features-code-examples)
* [release UART interface at RPi3](https://learn.adafruit.com/adafruit-nfc-rfid-on-raspberry-pi/freeing-uart-on-the-pi)
* [Logging in python](https://docs.python.org/3/library/logging.html#levels)
* [About IMAP and SMTP](https://automatetheboringstuff.com/chapter16/)
* [Unitest in python](https://docs.python.org/2/library/unittest.html)
* [unix daemon in Python](http://web.archive.org/web/20131025230048/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

## Fusion 360 system Housing 
* [view/download the design in Web Browser here](https://myhub.autodesk360.com/ue2906e76/g/shares/SHabee1QT1a327cf2b7a7fcac2ec095da1a6?viewState=NoIgbgDAdAjCA0IDeAdEAXAngBwKZoC40ARXAZwEsBzAOzXjQEMyzd1C0A2AIwCYBWACYBmACyCAtKIidGUmPwBmEgJzS5jJUoHDB-HmgC%2BIALpA)

## Acknowledgements
* Dragos  Iosub from ITBrainPower provided a library sketch  with the d-uGSM Module. The communication with the module in the SMSGate application is based on this API, which was a very good starting point.

## Amiq Consulting blog article
* [here](https://www.amiq.com/consulting/2017/03/24/mentoring-young-talent-through-hands-on-applications/)

