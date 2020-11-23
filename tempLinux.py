import subprocess
import re
from utils.basic_functions import *

def main():
	dic = {}
	IPAddresses = dickeys_into_list(dic)
	fileOut = "Pingout.dat"
	fileErr = "Pingerr.dat"
	print('Array of IP addresses:     ' + str(IPAddresses))

	# Ping All the Addresses
	with open(fileOut,"wb") as out, open(fileErr,"wb") as err:
		for i in range(len(IPAddresses)):
			subprocess.run('ping -c 4 ' + IPAddresses[i], stdout=out, stderr=err, shell=True)

	# Finding All the Losses
	lossArray = []
	pattern = re.compile('received, ')
	for line in open(fileOut):
		for match in re.finditer(pattern, line):
			lossArray.append(line.split('received, ')[1].split('%')[0])
	loss = [int(i) for i in lossArray]
	print('Array of losses (as int):  ' + str(loss))

	# Finding All the Average Times
	avgTimeArray = []
	pattern = re.compile(', time ')
	for line in open(fileOut):
		for match in re.finditer(pattern, line):
			avgTimeArray.append(line.split(', time ')[1].split('ms')[0])
	avgTime = [int(i) for i in avgTimeArray]
	print('Avg response time (in ms): ' + str(avgTime))

	# Updating All the Preferences
	for key in dic:
		dic[key] = (0.75*loss[IPAddresses.index(key)]) + (0.25*avgTime[IPAddresses.index(key)])

	print(f'CURR BEST - {IPAddresses[bestServerIndex]} | loss:{str(loss[bestServerIndex])}% | time:{str(avgTime[bestServerIndex])}')

	delete_file_in_cwd(fileErr)
	delete_file_in_cwd(fileOut)

if __name__ == '__main__':
    main()