import imaplib
import smtplib
import pprint
import email
import html2text
import io
from imaplib import IMAP4
from imaplib import IMAP4_SSL
from smtplib import SMTP
from html2text import HTML2Text
from email.mime.image import MIMEImage

# Explicit is better than implicit
from godot import exposed, export
from godot.bindings import Node2D, Vector2, PoolByteArray

@exposed
class ReadMail(Node2D):
	# connect to host using SSL
	testVar = export(str)
	def _read_mail(self, imap_host, imap_port, imap_user, imap_pass, imap_folder, eNum): # reads the most recent email and parses the text
		print("trying")
		try:
			if "gmail" in imap_host:
				imap = IMAP4_SSL(imap_host, imap_port)
			else:
				imap = IMAP4(imap_host, imap_port)
				imap.starttls()
			## login to server
			imap.login(imap_user, imap_pass)
		except:
			print("Failed to login")
			return
		#print(imap.list())
		imap.select("Inbox") # connect to all mail.
		result, data = imap.uid('search', None, "ALL") # search and return uids instead
		ids = data[0] # data is a list.
		id_list = ids.split() # ids is a space separated string
		latest_email_uid = data[0].split()[eNum]
		result, data = imap.uid('fetch', latest_email_uid, '(RFC822)') # fetch the email headers and body (RFC822) for the given ID
		raw_email = data[0][1] # here's the body, which is raw headers and html and body of the whole email
		b = email.message_from_bytes(raw_email)
		date = b['Date']
		body = ""
		email_subject = b['subject']
		email_from = b['from']
		email_body = b.get_payload(decode=True)
		if b.is_multipart():
			for part in b.walk():
				ctype = part.get_content_type()
				cdispo = str(part.get('Content-Disposition'))
				# skip any text/plain (txt) attachments
				if ctype == 'text/plain' and 'attachment' not in cdispo:
					email_body = part.get_payload(decode=True)  # decode
					#print(email_body)
					break
		html = str(email_body)
		parser = HTML2Text()
		parser.wrap_links = False
		parser.skip_internal_links = False
		parser.inline_links = False
		parser.ignore_anchors = False
		parser.ignore_images = False
		parser.ignore_emphasis = False
		parser.ignore_links = True
		parser.ignore_tables = False
		parser.single_line_break = True
		parser.unicode_snob = True
		parser.reference_links = True
		frm = str(email_from)
		#frm = parser.handle(str(email_from))
		sub = parser.handle(str(email_subject))
		text = parser.handle(html)
		text = text.strip('\\t\\n\\r')
		text = text.strip('\\t')
		text = text.strip('b\'')
		text = text.strip('\\r')
		text = text.replace('\\n\\n', '\n')
		text = text.replace('\\n', ' \n ')
		text = text.replace('\\r', '')
		self.get_parent().msgFrom = frm
		self.get_parent().msgSubject = sub
		self.get_parent().msgBody = text
		self.get_parent().msgDate = date
		self.get_parent()._print_mail()
		for part in b.walk():
			ctype = part.get_content_type()
			if ctype in ['image/jpeg', 'image/png']:
				by = bytearray(part.get_payload(decode=True))
				print(by[0])
				pool = PoolByteArray(by)
				self.get_parent().add_image(pool)
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
