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

encription_warning = "[Message not found: This email may be encrypted for your security. SocialMail does not currently feature end to end encryption.]"

ids_list = []

class SMail():
	def _read_mail(imap_host, imap_port, imap_user, imap_pass, imap_folder, eNum): # reads the most recent email and parses the text
		### Reading emails from the server. The bulk of the logic is here
		### We prosses an email, clean up the text, check if it is a reply
		### If the message is a reply, search for the original email in the sent box
		### If the original email exists, run a search on the inbox for all emails replying to the original
		### And finally, check for and load images
		global ids_list
		if eNum == -1:
			ids_list = []
		email_recieved = {
			'alreadyLoaded' : False
			}
		try:
			if "gmail" in imap_host: # gmail server requires an ssl connection
				print("gmail server")
				imap = IMAP4_SSL(imap_host, imap_port)
			else: # tls is preferred
				imap = IMAP4(imap_host, imap_port)
				imap.starttls()
			## login to server
			print(imap_user, imap_pass)
			imap.login(imap_user, imap_pass)
		except:
			print("Failed to login")
			return False
		#print(imap.list()) # for identifying mailboxes on the server
		imap.select("Inbox") # connect to all mail.
		result, data = imap.uid('search', None, "ALL") # search and return uids instead
		ids = data[0] # data is a list.
		id_list = ids.split() # ids is a space separated string
		current_email_uid = data[0].split()[eNum]
		#print(current_email_uid)
		result, data = imap.uid('fetch', current_email_uid, '(RFC822)') # fetch the email headers and body (RFC822) for the given ID
		raw_email = data[0][1] # here's the body, which is raw headers and html and body of the whole email
		b = email.message_from_bytes(raw_email)
		email_recieved['msg_id'] = b['Message-ID']
		#print("printing id", msg_id, ids_list)
		for i in ids_list:
			if i == email_recieved['msg_id']:
				print("mail already loaded")
				email_recieved['alreadyLoaded'] = True
				#self.get_parent()._already_loaded()
				return
		ids_list.append(email_recieved['msg_id'])
		email_from = b['from']
		email_subject = b['subject']
		email_recieved['date'] = b['Date']
		email_recieved['inreply'] = b['in-reply-to']
		email_recieved['refs'] = b['references']
		email_body = b.get_payload()
		if b.is_multipart(): # search for text in the body
			for part in b.walk():
				ctype = part.get_content_type()
				cdispo = str(part.get('Content-Disposition'))
				if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
					email_body = part.get_payload()
					#print(email_body)
					break
		# Use beautifulsoup to get readable text
		frm = BeautifulSoup(email_from, 'html.parser')
		sub = BeautifulSoup(email_subject, 'html.parser')
		try: # Try parsing the body text
			body = BeautifulSoup(email_body, 'html.parser')
		except: # if email is encrypted it will throw an exception
			email_recieved['body'] = encription_warning
		email_recieved['from'] = frm.get_text()
		email_recieved['subject'] = sub.get_text()
		#find just the email address
		add1 = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(frm))
		email_recieved['email'] = add1[0]
		if body != encription_warning:
			email_recieved['body'] = body.get_text()
		return email_recieved
		'''
		text = text.strip('\\t')
		text = text.replace('\\n', ' \n ')
		'''
	def _read_source(imap_host, imap_port, imap_user, imap_pass, imap_folder, email_inreply):
		source = {
			'alreadyLoaded' : False
			}
		try: ## Time to search for the original email
			try:
				if "gmail" in imap_host: # gmail server requires an ssl connection
					print("gmail server")
					imap = IMAP4_SSL(imap_host, imap_port)
				else: # tls is preferred
					imap = IMAP4(imap_host, imap_port)
					imap.starttls()
				## login to server
				#print(imap_user, imap_pass)
				imap.login(imap_user, imap_pass)
			except:
				print("Failed to login")
				return False
			if "gmail" in imap_host:
				imap.select('"[Gmail]/Sent Mail"') # connect to sent mail.
				#print("Opening gmail 'Sent'")
			else:
				imap.select('Sent') # connect to sent mail.
				#print("Opening 'Sent'")
			# Search for the original email ID
			messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
			# Process the result to get the message id’s
			messages = messages[1][0].split()
			# Use the first id to view the headers for a message
			result, source_data = imap.fetch(messages[0], '(RFC822)')
			raw_source = source_data[0][1] # here's the body, which is raw headers and html and body of the whole email
			s = email.message_from_bytes(raw_source) # convert to message object
			source_subject = s['subject']
			source['date'] = s['Date']
			source['bcc'] = s['bcc']#.split(',')
			source['msg_id'] = s['Message-ID']
			#print("BCC from source: ", source_bcc)
			source_body = s.get_payload()
			if s.is_multipart(): # search for text in the body
				for part in s.walk():
					ctype = part.get_content_type()
					cdispo = str(part.get('Content-Disposition'))
					if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
						source_body = part.get_payload()
						#print(email_body)
						break
			#print(frm, " Sent a reply to: ", source_subject)
			self.get_parent().msgIsReply = True
			src_sub = BeautifulSoup(source_subject, 'html.parser')
			try: # extra check for encryption (in case user has encypted email)
				src_body = BeautifulSoup(source_body, 'html.parser')
			except: # if email is encrypted it will throw an exception
				src_body = encription_warning
			source['subject'] = src_sub.get_text()
			source['body'] = src_body.get_text()
			return source
		except:
			print("no origin found")
			return False

	def find_replies(imap_host, imap_port, imap_user, imap_pass, imap_folder, email_inreply):
		try:
			# On to find more emails that may be replies
			replies_list = []
			try:
				if "gmail" in imap_host: # gmail server requires an ssl connection
					print("gmail server")
					imap = IMAP4_SSL(imap_host, imap_port)
				else: # tls is preferred
					imap = IMAP4(imap_host, imap_port)
					imap.starttls()
				## login to server
				#print(imap_user, imap_pass)
				imap.login(imap_user, imap_pass)
			except:
				print("Failed to login")
				return False
			imap.select("Inbox")
			replies = imap.search(None, 'HEADER', 'IN-REPLY-TO', email_inreply)
			# BODY.PEEK[HEADER.FIELDS (SUBJECT)]
			print("searched inbox for ", email_inreply)
			# Process the result to get the message id’s
			replies = replies[1][0].split()
			print("got list of replies")
			# Use the first id to view the headers for a message
			replies.reverse()
			for i in replies:
				reply = {}
				print("Checking list of replies")
				result, reply_data = imap.fetch(i, '(RFC822)')
				print("loaded a reply")
				raw_reply = reply_data[0][1] # here's the body, which is raw headers and html and body of the whole email
				#print("raw reply")
				r = email.message_from_bytes(raw_reply) # convert to message object
				#reply_to = r['in-reply-to']
				reply['refs'] = r['references']
				print("references", reply['refs'])
				reply_from = r['from']
				reply_email = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(reply_from))
				reply['date'] = r['Date']
				reply['msg_id'] = r['Message-ID']
				reply_body = r.get_payload()
				if r.is_multipart(): # search for text in the body
					for part in r.walk():
						ctype = part.get_content_type()
						cdispo = str(part.get('Content-Disposition'))
						if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
							reply_body = part.get_payload()
							#print(email_body)
							break
				rep_from = BeautifulSoup(reply_from, 'html.parser')
				reply['email'] = reply_email[0]
				reply['from'] = rep_from.get_text()
				try: # extra check for encryption (in case user has encypted email)
					rep_body = BeautifulSoup(reply_body, 'html.parser')
					reply['body'] = rep_body.get_text()
				except: # if email is encrypted it will throw an exception
					reply['body'] = encription_warning
				#print("Hello! I am found, ")
				replies_list.append(reply)
			return replies_list
		except:
			return False
			print("No more replies found.")

	## Check for image attachments
	def _read_images(imap_host, imap_port, imap_user, imap_pass, imap_folder, message_ID): # reads the most recent email and parses the text
		for part in b.walk():
			ctype = part.get_content_type()
			if ctype in ['image/jpeg', 'image/png']:
				by = bytearray(part.get_payload(decode=True))
				#print('image found')
				#print(by[0])
				#TODO display image
				# Below line is for saving to disk
				#open(part.get_filename(), 'wb').write(part.get_payload(decode=True))
	def _sending_mail(imap_host, imap_port, imap_user, imap_pass, imap_to, subject, message, reply_to):
		print("recieving")
		imap = SMTP(imap_host, imap_port)
		imap.starttls()
		## login to server
		imap.login(imap_user, imap_pass)
		msg = (reply_to + "From: " + imap_user + "\r\nTo: " + " " +"\r\nSubject: "+ subject +"\r\n\n"+ message)
		try:
			imap.sendmail(imap_user, imap_to, msg)
			print("Mail sent")
		except:
			print("Failed to send mail")
		imap.quit()

	def _imap_login(imap_host, imap_port, imap_user, imap_pass):
		try:
			if "gmail" in imap_host: # gmail server requires an ssl connection
				print("gmail server")
				imap = IMAP4_SSL(imap_host, imap_port)
			else: # tls is preferred
				imap = IMAP4(imap_host, imap_port)
				imap.starttls()
			## login to server
			print(imap_user, imap_pass)
			imap.login(imap_user, imap_pass)
			return True
		except:
			print("Failed to login")
			return False

	def _login(imap_host, imap_port, imap_user, imap_pass):
		print("Logging in")
		imap = SMTP(imap_host, imap_port)
		imap.starttls()
		try:
			r = imap.login(imap_user, imap_pass)
			imap.helo()
			#self.get_parent()._loged_in()
		except:
			print("log in failed")
			return False
			#self.get_parent()._failed_login()
		print("Successfully logged in")
		return True
