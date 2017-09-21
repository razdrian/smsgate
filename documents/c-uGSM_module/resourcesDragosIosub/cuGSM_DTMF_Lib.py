############################################################################################################################################
#cuGSM_DTMF_Lib.py v1.01/08September2015 - c-uGSM 1.13 DTMF support library 
#COPYRIGHT (c) 2015 Dragos Iosub / R&D Software Solutions srl
#
#You are legaly entitled to use this SOFTWARE ONLY IN CONJUNCTION WITH c-uGSM DEVICES USAGE. Modifications, derivates and redistribution 
#of this software must include unmodified this COPYRIGHT NOTICE. You can redistribute this SOFTWARE and/or modify it under the terms 
#of this COPYRIGHT NOTICE. Any other usage may be permited only after written notice of Dragos Iosub / R&D Software Solutions srl.
#
#This SOFTWARE is distributed is provide "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied 
#warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#Dragos Iosub, Bucharest 2015.
#http://itbrainpower.net
############################################################################################################################################
from cuGSM_Serial_Lib import *

#setupMODEMforDTMFusage()
#   just set and look at modem to be ready for DTMF usage 
#   call this before encode&send or receive&decode DTMF 
def setupMODEMforDTMFusage():
    sendATcommand("AT+QTONEDET=4,1,3,3,65536",["OK","ERROR"],5)#some DTMF detection settings
    sendATcommand("AT+QTONEDET=1",["OK","ERROR"],5)#enable DTMF detection
    sendATcommand("AT+QSFR=7",["OK","ERROR"],5)#use EFR -recomended....
    sendATcommand("AT+QTDMOD=1,0",["OK","ERROR"],5)#other DTMF settings
    print("send / detect DTMF support enabled")

#disableDTMFdetection() disable the DTMF detection
def disableDTMFdetection():
    res = sendATcommand("AT+QTONEDET=0",["OK","ERROR"],5)
    if(res==1):
        print("DTMF detection disabled")



#next example for DTMF send -in that 100,100 means: 100ms DTMF lenght and 100 DTMF pause, best for decoding too. The last 3* are used as terminator string in listen4DTMF(terminator) 
#sendATcommand("AT+QWDTMF=6,0,\"ABCD0123456789*#***,100,100\"",["OK","ERROR"],10)#send some DTMF

#sendDTMF(DTMFstring, DTMFterminator, DTMFlenght, DTMFpause)
#   ...send some DTMF ...be sure you did before setupMODEMforDTMFusage()
#   DTMFstring      ... value to be transmitted ABCD0123456789*#
#   DTMFterminator  can be null....string used as terminator listen4DTMF(terminator, to)) *** can be a good choise
#   DTMFlenght      ... in msec (100 best for decoding too)
#   DTMFpause       ... in msec (100 best for decoding too)
def sendDTMF(DTMFstring, DTMFterminator, DTMFlenght, DTMFpause):
    sendATcommand("AT+QWDTMF=6,0,\""+DTMFstring+DTMFterminator+","+str(DTMFlenght)+","+str(DTMFpause)+"\"",["OK","ERROR"],10)#send it baby
    print(buffd)#4debug

#listen4DTMF(terminator, to)
#   see bellow the function the C implementation...you are free to port it to python
def listen4DTMF(terminator, to):
    print "you are free to port it from the Arduino C code example..."
    print "read inside module_DTMF_lib.py"
    return 0
#DTMF=""
#listen4DTMF("***", 55)#listen for DTMF see bellow the Arduino C code --just port yourself it to python
#/*
#Listen for DTMF until "terminator" has been found or "to" (in secs) timeout reached
#return: int 
#  -1 TIMEOUT
#  1  SUCCESS
#read DTMF string => DTMF
#*/
#char * DTMF;
#int listen4DTMF(char * terminator, int to){
#  int run = 1;
#  int res = 0;
#  int i=0, j=0;
#  unsigned long startTime;
#  char u8_c;
#  char* pch0;
#  char* pch1;
#  char DTMFstr[3];
#  char DTMFint;
#  
#  clearBUFFD();
#  startTime = millis();	
#  while(run){
#    if(millis() - startTime > (unsigned long)to *1000) {
#      #if defined(atDebug)
#        printDebugLN("to!");
#      #endif
#      clearHDSerial();
#      run=0;
#      res=-1;//timeout!
#    }
#    
#    while(TXavailable()){//read it baby
#      u8_c = aGsmREAD();
#      buffd[i]=u8_c;
#      i++;
#      if(u8_c == 0x0D) {//found EOL, let's process it
#        if (strstr(buffd,"+QTONEDET:")){
#            pch0 = strstr(buffd,"+QTONEDET:");
#            pch1 = strstr(buffd,"\r\n");
#            memset(DTMFstr,0x00,sizeof(DTMFstr));
#            strncpy(DTMFstr, pch0+11, 2);
#            DTMFint = (char) atoi(DTMFstr);
#            DTMF[j] = DTMFint;
#            j++;
#            if(strstr(DTMF,terminator)){//found logical terminator!
#                clearHDSerial();
#                run=0;//break loop
#                res=1;//go back with success
#            }
#        }
#        clearBUFFD();//prepare for and go to receive next DTMF char
#        i=0;
#        break;
#      }
#    }
#  }
#  return(res);
#}
