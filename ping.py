#usage: ping.py [-o logfile] [-h hostname] [-t max_rtt] [-i interval]

import subprocess
import re
import sys, getopt
from time import localtime, strftime, sleep

max_rtt = 100 #any round-trip-time greater than this (in ms) will be reported
hostname = "google.de"
pattern = re.compile('time=(?P<ms>[\d]+\.[\d]+) ms')
logfile = "ping.log"
interval = 5 #ping interval in seconds


#parse input
opts, args = getopt.getopt(sys.argv[1:], "o:h:t:i:")
for opt, arg in opts:
	if opt == "-o":
		logfile = arg
	elif opt == "-h":
		hostname = arg
	elif opt == "-t":
		max_rtt = float(arg)
	elif opt == "-i":
		interval = float(arg)


def ping():
	report = False
	out = ""
	cause = ""
	time = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())

	try:
		cmd = "ping -c 1 " + hostname
		print cmd
		out = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)

		#ping successful, did it take too long?
		result = pattern.search(out)
		rtt = float(result.group("ms"))
		if rtt > max_rtt:
			report = True
			cause = "High RTT (" + str(rtt) + " ms)"

	except subprocess.CalledProcessError as e:
		#non-zero return code (server not reachable)
		report = True
		cause = "No reply"
		out = e.output

	if report:
		return (time, cause, out)
	else:
		return False

def report(result):
	with open(logfile, "a") as myfile:
		for i in range(0, 3):
			myfile.write(result[i] + "\n")
		myfile.write("\n")


if __name__ == "__main__":
	#main loop
	while True:
		try:
			result = ping()
			if result:
				print(result[1])
				report(result)
			sleep(interval)
		except KeyboardInterrupt:
			print "Cancelled by user"
			break
