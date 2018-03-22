import subprocess
# result = subprocess.run(['echo', 'da'], stdout=subprocess.PIPE)
# print (result.stdout)

process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
result, error = process.communicate('ping ' + '-w ' + '1 ' + '-W ' + '3 ' + 'smtp.gmail.com')

