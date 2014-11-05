#!/usr/bin/python
# -*- encoding: utf-8 -*-

from optparse import OptionParser
import ConfigParser
import urllib
from BeautifulSoup import BeautifulSoup
#from bs4 import BeautifulSoup
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
emailconfig.read('email.conf')

smtpserver   = emailconfig.get('Email', 'smtpserver')
from_addr    = emailconfig.get('Email', 'from_addr')
to_addr_list = emailconfig.get('Email', 'to_addr_list').split(',')
login        = emailconfig.get('Email', 'login')
password     = emailconfig.get('Email', 'password')

# Get the content from the website
#sock = urllib.urlopen("http://www.ukclimbing.com/forums/")
sock = urllib.urlopen("http://www.ukclimbing.com/forums/i.php?f=2")
webpage = sock.read()
sock.close

# Parse the HTML
phtml = BeautifulSoup(webpage)

# Find the main content
maincontent = phtml.body.find('table', attrs={'class':'table table-striped table-condensed small lst top10'})

# Find all the topics
results = ""

# Oslo
topic1 = maincontent.findAll("a", text=re.compile(".*oslo.*", re.IGNORECASE))
topic2 = maincontent.findAll("a", text=re.compile(".*norway.*", re.IGNORECASE))
topic3 = maincontent.findAll("a", text=re.compile(".*climb.*", re.IGNORECASE))

topics = topic1 + topic2 + topic3
print topics

for link in topics:
	print link

exit()

text = topics

html = """\
<html>
  <head></head>
  <body>
		<p>This is an alert that one or more of your search terms 'Oslo' or 'Norway' is currently being actively discussed on UKC.<br/><br/>
		Search results:<br/>""" + results + """<br/><br/>
  		<a href="http://www.ukclimbing.com/forums/">Click here to go to the ukc forum</a>
   	</p>
  </body>
</html>
"""

msg = MIMEMultipart('alternative')
msg['Subject'] = "UKC forum alert"
msg['From'] = from_addr
msg['To'] = ','.join(to_addr_list)

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

server = smtplib.SMTP(smtpserver)
server.starttls()
server.login(login,password)
problems = server.sendmail(from_addr, to_addr_list, msg.as_string())
server.quit()
