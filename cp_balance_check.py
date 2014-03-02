#!/usr/bin/python

#Author: Emmanuel Lartey
#Version: 1.0
#Title: CP Balance Checker and Notifier
#Date: 10th November 2013

import os, commands, sys 
import MySQLdb as mdb 
import time
import smtplib
import email
from sys import argv
from email.mime.text import MIMEText


script, client, cpid, recipient  = argv

now = time.strftime('%H')

log_reset_time = time.strftime('%H%M')

fetchWeeklyFiles = "find /home/scripts/reports/external/topup/logs/ -name \*.csv -type f -mtime -7 | grep '_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].csv' | grep -v 'vodafone_weekly_topup_report.csv' | grep %s" % (client)

listdata = commands.getoutput(fetchWeeklyFiles)

'''
Function to write data to a file.

'''

def writeData(d):
	
	filewrite = open('/tmp/cp_alert.txt', 'ab')
	filewrite.writelines(d)
	filewrite.close()



'''
Function to read the data contained in a file.

'''

def readData(source):
        
        fileread = open(source, 'r')
        data_stream = fileread.read().rstrip()
        fileread.close()
        return data_stream


'''
Function to generate the average top up transactions over a week for a CP 

'''

def weeklyClientBalance(c):

    topup_data = []
    topups = []
        
      
    for line in listdata.split('\n'):
        
        topup_data =  readData(line).split('\n')

        #inline function for adding up all tops for a CP over 7 days
        #topups += [float(index.split(',')[2]) for index in topup_data[1:] if "Successful" in index]


        #This ignores the first line in each file. This line holds the column names
        for index in topup_data[1:]:
            if str(index.split(',')[6] == "Successful":
                topups.append(float(index.split(',')[2]))
        s = sum([float(i) for i in topups])

        #This generates a sum 10% above the weekly average
    return int(((s * 0.10)/10000) + (s/10000)/7)




'''
Function to connect to the database to fetch the CP's current exposure expo_limit

'''

def currentBalance(cid):
    try:

        con = mdb.connect('#ip_address', '#username', '#password', '#database')
        cur = con.cursor()
        cur.execute("select round((expo_limit/10000),2) as '' from ot_rms12.price_control where cp_id = '"+str(cid)+"'") 

        for i in range(cur.rowcount):

            row = cur.fetchone()
            return int(row[0])
            #print float(row[0])

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)


        con.close()


'''

Function to send email to client once limit is breached

'''

def sendMail(mes, success = True):
	me = "auto-notif@somewhere.com"
	cc = "tech@somewhere.com"
	you = str(recipient)
	title = "Low Credit Balance on Account - %s" % (client)
	
    # Create message container - the correct MIME type is multipart/alternative.
	msg = email.MIMEMultipart.MIMEMultipart('alternative')
	msg.add_header('Subject', title)
	msg.add_header('From', me)

	for rcv in you.split(','):
		msg.add_header('To', rcv)

	for rcv in cc.split(','):
		msg.add_header('Cc', rcv)

	
	part = email.MIMEText.MIMEText(mes, 'html')
	msg.attach(part)
	
	# to_addrs = headers["To"] + headers.get("Cc", []) + headers.get("Bcc", [])
	to_addrs = msg.get_all("To") + msg.get_all("Cc")
	
	#Send the message via local SMTP server.
	s = smtplib.SMTP('localhost')
	#sendmail function takes 3 arguments: sender's address, recipient's address
	#and message to send - here it is sent as one string.
	s.sendmail(me, to_addrs, msg.as_string())
	s.quit()

'''
Function to perform threshold breach checks
'''

def thresholdCheck():

	if currentBalance(cpid) < weeklyClientBalance(client):

		return 1
	
	else:

		return 0



email_body = """

Hi, \n\n
<br></br>
Your current balance is less than your daily top up average.\n\n
<br></br>
Daily Average: GHC %s \n\n
<br></br>
Current credit balance: GHC %s\n\n
<br></br>
Kindly contact Vodafone to make the necessary top up arrangements before the balance runs out. \n\n
<br></br>
Thank you. \n

""" % (weeklyClientBalance(client), currentBalance(cpid))



def main():

	if int(log_reset_time) == 0000:

		emptyFile = "cat /dev/null > /tmp/cp_alert.txt"
		commands.getoutput(emptyFile)
	
	if thresholdCheck() == 1:

		data = "%s \n" % (client)
		writeData(data)
		
		emailCheck = "cat /tmp/cp_alert.txt | grep %s | wc -l" % (client)
		alert_count = commands.getoutput(emailCheck)

		if int(alert_count) > 1:

			timecheck = int(now) % 4

			quarterCheck = int(alert_count) % 3

			if (timecheck == 0) & (quarterCheck == 1):

				sendMail(email_body)

		elif int(alert_count) == 1:

			sendMail(email_body)
	else:

		print "ok"




if __name__ == '__main__':

	main()
