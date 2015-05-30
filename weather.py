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
emailconfig.read('w_email.conf')

smtpserver   = emailconfig.get('Email', 'smtpserver')
from_addr    = emailconfig.get('Email', 'from_addr')
to_addr_list = emailconfig.get('Email', 'to_addr_list').split(',')
login        = emailconfig.get('Email', 'login')
password     = emailconfig.get('Email', 'password')

# Get the content from the website
sock = urllib.urlopen("http://nwfc.pmd.gov.pk/24-hour-weather-outlook/index.php")
webpage = sock.read()
sock.close

# Parse the HTML
phtml = BeautifulSoup(webpage)

# Find the first time Gilgit is mentioned (the most recent result)
g_head = phtml.body.find(text=re.compile(".*Gilgit.*"))
# Fint the next sibling to get the description
g_desc = g_head.find_next("span").find("span").contents[0]

text = g_desc

html = """\
<html>
  <head></head>
  <body>
		<p>This is the weather forecast from the Pakistani Metrological Department:<br/>
		""" + g_head + """ """ + g_desc  + """<br/><br/>
  		<a href="http://nwfc.pmd.gov.pk/24-hour-weather-outlook/index.php">Click here to go to the website</a>
   	</p>
  </body>
</html>
"""

msg = MIMEMultipart('alternative')
#msg['Subject'] = "Gilgit weather forecast"
msg['Subject'] = g_desc
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
