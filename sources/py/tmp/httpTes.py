import subprocess


# process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# result, error = process.communicate('ping ' + '-w ' + '1 ' + '-W ' + '3 ' + '8.8.8.8')

try:
    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result,error=process.communicate(' find /var/smsgate/input/ -name \'*\'')
    result = result.split('\n')

except:
    print ('error now')
else:
    print len(result)
    if(len(result)>2):
        print ('there is someone there')
    else:
        print ('all is void there man')
