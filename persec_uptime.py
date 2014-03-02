#!/usr/bin/python

#Author: Emmanuel Lartey
#Version: 1.0
#Title: Daemonizer ( General Purpose Daemonizer for Shell or Perl scripts )
#Date: 23rd February 2014

import os
import time
import commands
from multiprocessing import Process

from daemon import runner

class UptimeCheck:

	def __init__(self):
		
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path = '/var/run/psec_uptime.pid'
		self.pidfile_timeout = 5


	def run(self):

		#Assisgns file paths
		filepath = '/var/log/app_tomcat_uptime/new_app/'
		dirpath = os.path.dirname(filepath)

		#Checks whether log path exists and if not creates it.
		while True:
			if not os.path.isdir(dirpath):
				os.makedirs(dirpath)
			
			#Place shell/perl script to be daemonized
			http_check = "/usr/bin/perl /usr/local/bin/http_uptime_new_app.pl"
			commands.getoutput(http_check)
			time.sleep(1)
			
def main():

	upcheck = UptimeCheck()

	run_daemon = runner.DaemonRunner(upcheck)
	p = Process(target=run_daemon.do_action())
	p.start()
	p.join()


if __name__ == '__main__':
	
	main()
	