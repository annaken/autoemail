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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
enc = 'utf-8'

# Get outbout email settings from config
emailconfig = ConfigParser.RawConfigParser()
emailconfig.read('k_email.conf')

smtpserver   = emailconfig.get('Email', 'smtpserver')
from_addr    = emailconfig.get('Email', 'from_addr')
to_addr_list = emailconfig.get('Email', 'to_addr_list').split(',')
login        = emailconfig.get('Email', 'login')
password     = emailconfig.get('Email', 'password')

# Get the content from the website
sock = urllib.urlopen("http://www.klartale.no/")
webpage = sock.read()
sock.close

# Parse the HTML
phtml = BeautifulSoup(webpage)

# Find the main content
maincontent = phtml.body.find('div', attrs={'class':'mainContent'})

# Get the main article's title
article_title = maincontent.h2.a.span.string
enc_article_title = unicode(article_title).encode(enc)
subject = "Klar Tale " + enc_article_title

# and short content
article_text = maincontent.find('div', attrs={'class':'subtext'}).contents[5]
enc_article_text = unicode(article_text).encode(enc)
text = enc_article_title + "\n\n" + enc_article_text

# now go to the other page and get the full content
articleurl = maincontent.h2.a['href']

# Get the content from that other page
sock = urllib.urlopen(articleurl)
articlepage = sock.read()
sock.close

# Parse the HTML
parthtml = BeautifulSoup(articlepage)

# Get the article full text
article_content = parthtml.body.find('div', attrs={'class':'articleText'})
plist = article_content.findAll('p')
pstring = ''.join(unicode(p).encode(enc) for p in plist)

html = """\
<html>
  <head></head>
  <body>
		<p>
	  	<i><b>""" + enc_article_text + """</b></i><br/><br/>""" + pstring + """<br/><br/>
  		<a href="http://www.klartale.no">Trykk her for hele siden</a>
   	</p>
  </body>
</html>
"""

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
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
