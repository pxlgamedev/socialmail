import imaplib
import smtplib
import pprint
import email
import io
import re
from imaplib import IMAP4
from imaplib import IMAP4_SSL
from smtplib import SMTP
from email.mime.image import MIMEImage
from bs4 import BeautifulSoup

# Explicit is better than implicit
from godot import exposed, export
from godot.bindings import Node2D, Vector2, PoolByteArray

encription_warning = "[Message not found: This email may be encrypted for your security. SocialMail does not currently feature end to end encryption.]"

@exposed
class ReadMail(Node2D):
	#testVar = export(str)
	def _read_mail(self, imap_host, imap_port, imap_user, imap_pass, imap_folder, eNum, imap_sent): # reads the most recent email and parses the text
		### Reading emails from the server. The bulk of the work is here
		### We prosses an email, clean up the text, check if it is a reply
		### Load the original email if it is a reply, and check for and load images
		try: 
			if "gmail" in imap_host: # gmail server requires an ssl connection
				imap = IMAP4_SSL(imap_host, imap_port)
			else: # tls is preferred
				imap = IMAP4(imap_host, imap_port)
				imap.starttls()
			## login to server
			imap.login(imap_user, imap_pass)
		except:
			print("Failed to login")
			return
		#print(imap.list()) # for identifying mailboxes on the server
		imap.select("Inbox") # connect to all mail.
		result, data = imap.uid('search', None, "ALL") # search and return uids instead
		ids = data[0] # data is a list.
		id_list = ids.split() # ids is a space separated string
		latest_email_uid = data[0].split()[eNum]
		result, data = imap.uid('fetch', latest_email_uid, '(RFC822)') # fetch the email headers and body (RFC822) for the given ID
		raw_email = data[0][1] # here's the body, which is raw headers and html and body of the whole email
		b = email.message_from_bytes(raw_email)
		date = b['Date']
		email_subject = b['subject']
		email_from = b['from']
		email_inreply = b['in-reply-to']
		email_body = b.get_payload()
		if b.is_multipart(): # search for text in the body
			for part in b.walk():
				ctype = part.get_content_type()
				cdispo = str(part.get('Content-Disposition'))
				if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
					email_body = part.get_payload()
					#print(email_body)
					break
		frm = BeautifulSoup(email_from, 'html.parser')
		sub = BeautifulSoup(email_subject, 'html.parser')
		try: # Try parsing the body text
			body = BeautifulSoup(email_body, 'html.parser')
		except: # if email is encrypted it will throw an exception
			body = encription_warning
			#print(b['subject'])
			#print(b.keys())
		'''
		text = text.strip('\\t')
		text = text.replace('\\n', ' \n ')
		'''
		if email_inreply != "None": # if this email is a reply
			try:
				if "gmail" in imap_host:
					sent = IMAP4_SSL(imap_host, imap_port)
				else:
					sent = IMAP4(imap_host, imap_port)
					sent.starttls()
				## login to server
				sent.login(imap_user, imap_pass)
				if "gmail" in imap_host:
					sent.select('"[Gmail]/Sent Mail"') # connect to sent mail.
					#print("Opening gmail 'Sent'")
				else:
					sent.select('Sent') # connect to sent mail.
					#print("Opening 'Sent'")
				# Search for the original email ID
				messages = sent.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
				# Process the result to get the message id’s
				messages = messages[1][0].split()
				# Use the first id to view the headers for a message
				result, source_data = sent.fetch(messages[0], '(RFC822)')
				raw_source = source_data[0][1] # here's the body, which is raw headers and html and body of the whole email
				s = email.message_from_bytes(raw_source) # convert to message object
				source_subject = s['subject']
				source_date = s['Date']
				source_bcc = s['bcc']
				#print("BCC from source: ", source_bcc)
				source_body = s.get_payload(decode=True) 
				#print(frm, " Sent a reply to: ", source_subject)
				self.get_parent().msgIsReply = True
				src_sub = BeautifulSoup(source_subject, 'html.parser')
				try: # extra check for encryption (in case user has encypted email)
					src_body = BeautifulSoup(source_body, 'html.parser')
				except: # if email is encrypted it will throw an exception
					src_body = encription_warning
				self.get_parent().originSub = src_sub.get_text()
				self.get_parent().originBody = src_body.get_text()
				self.get_parent().originDate = src_date
				self.get_parent().originbcc = src_bcc
			except:
				print("No origin found")
		self.get_parent().msgFrom = frm.get_text()
		#print(frm.contents)
		add1 = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(frm))
		self.get_parent().msgEmail = add1[0]
		self.get_parent().msgSubject = sub.get_text()
		if body != encription_warning:
			body = body.get_text()
		self.get_parent().msgBody = body
		self.get_parent().msgDate = date
		self.get_parent()._print_mail()
		for part in b.walk(): # Check for image attachments
			ctype = part.get_content_type()
			if ctype in ['image/jpeg', 'image/png']:
				by = bytearray(part.get_payload(decode=True))
				#print(by[0])
				pool = PoolByteArray(by) # create a Godot PoolByteArray
				self.get_parent().add_image(pool) #Pass it to the mail fetcher
				# Below line is for saving to disk
				#open(part.get_filename(), 'wb').write(part.get_payload(decode=True))
	def _sending_mail(self, imap_host, imap_port, imap_user, imap_pass, imap_to, subject, message):
		print("recieving")
		imap = SMTP(imap_host, imap_port)
		imap.starttls()
		## login to server
		imap.login(imap_user, imap_pass)
		msg = ("From: " + imap_user + "\r\nTo: " + " " +"\r\nSubject: "+ subject +"\r\n\n"+ message)
		try:
			imap.sendmail(imap_user, imap_to, msg)
			print("Mail sent")
			self.get_parent()._mail_sent()
		except:
			print("Failed to send mail")
			self.get_parent()._failed_to_send()
		imap.quit()
	def _login(self, imap_host, imap_port, imap_user, imap_pass):
		print("Logging in")
		imap = SMTP(imap_host, imap_port)
		imap.starttls()
		try:
			r = imap.login(imap_user, imap_pass)
			imap.helo()
			self.get_parent()._loged_in()
		except:
			print("fail")
			self.get_parent()._failed_login()
		print("ready")
