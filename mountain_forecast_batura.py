#!/usr/bin/python
# -*- encoding: utf-8 -*-

from optparse import OptionParser
import ConfigParser
import urllib
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
#from lib.bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
enc = 'utf-8'

# Get outbout email settings from config
emailconfig = ConfigParser.RawConfigParser()
emailconfig.read('/home/annaken/autoemail/w_email.conf')

smtpserver   = emailconfig.get('Email', 'smtpserver')
from_addr    = emailconfig.get('Email', 'from_addr')
to_addr_list = emailconfig.get('Email', 'to_addr_list').split(',')
login        = emailconfig.get('Email', 'login')
password     = emailconfig.get('Email', 'password')

# Get the content from the website
sock = urllib.urlopen("http://www.mountain-forecast.com/peaks/Batura/forecasts/5000")
webpage = sock.read()
sock.close

# Parse the HTML
phtml = BeautifulSoup(webpage)

# Get everything
maincontent = phtml.body.find('div', attrs={'id':'forecast-cont'})

# Get the table where we name the days
day_tr = maincontent.find('tr', attrs={'class':'lar hea '} )

daylist = []

# What does our column layout look like?
col_list = day_tr.findAll('td', {"colspan":True})
for col in col_list:

	# How many columns does the day span?
	numcols = int(col['colspan'])

	# If it's not three, it's a special case html
	if len(col.contents)!=3:
		day = col.contents[0].strip()[0:2].upper()
		#day = col.contents[0].strip()[0]
		
	else:
		day = col.find('b').contents[0][0:2].upper()
		#day = col.find('b').contents[0][0]

	# Fill the list with the a day per column	
	for i in range (0, numcols):
#		print "numcols", i
		daylist.append(day)

#print daylist

weatherlist = []

# Weather description
witems = maincontent.findAll('div', attrs={'class':'weathercell'})

for w in witems:
	# Get the description
	wdesc = w.find('img')['alt']
	
	# Split the desc into words
	wdesc_parts = wdesc.split()

	# If it's only one word
	if len(wdesc_parts)==1:
		wsdesc = wdesc_parts[0][0] + wdesc_parts[0][-1]

	# If it's two words
	else:
		wsdesc = wdesc_parts[0][0] + wdesc_parts[1][0]
	
	weatherlist.append(wsdesc)

#print weatherlist

snowlist = []

# Get snow
snowitems = maincontent.findAll('span', attrs={'class':'snow'})

for s in snowitems:
	snowlist.append(s.contents[0])

#print snowlist

weathermsg = ''

for i in range(0, 17):
	
#	print daylist[i]
#	print weatherlist[i]
#	print snowlist[i]

	weathermsg+=daylist[i]
	weathermsg+=weatherlist[i]
	weathermsg+=snowlist[i]
	weathermsg+=' '


text = weathermsg


html = """\
<html>
  <head></head>
  <body>
		<p>This is the weather forecast from Mountain Forecast for Batura 5000m:<br/>
		""" + weathermsg  + """<br/><br/>
   	</p>
  </body>
</html>
"""

msg = MIMEMultipart('alternative')
msg['Subject'] = "Batura 5000 weather forecast"
msg['From'] = from_addr
msg['To'] = ','.join(to_addr_list)

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
#msg.attach(part2)

server = smtplib.SMTP(smtpserver)
server.starttls()
server.login(login,password)
problems = server.sendmail(from_addr, to_addr_list, msg.as_string())
server.quit()
