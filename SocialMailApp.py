import sys
import kivy
import socket_client
import MailFetcher
from string import ascii_lowercase
from MailFetcher import SMail

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import WipeTransition, FadeTransition, SwapTransition, CardTransition, FallOutTransition

imap_host = "imap.gmail.com"
imap_port = "587"
smtp_port = 993
imap_user = ""
imap_pass = ""
imap_folder = ""
eNum = -1
imap_sent = ""


kv = """
<Label>:
    font_name: 'Montreal-Regular.ttf'
<Card>:
	canvas.before:
		Color:
			rgba: 0.25, 0.1, 0.25, 1
		RoundedRectangle:
			size: self.size
			pos: self.pos
	_from: ''
	subject: 'testing'
	body: ''
	_date: ''
	card_size: 500

	orientation: 'vertical'
	padding: 20
	size: self.width, root.card_size
	Label:
		text: root._from
		text_size: self.size
		size_hint_y: 0.1
		halign: 'left'
		valign: 'middle'
		outline_color: 0.6, 0.5, 0.6, 1
		outline_width: 1
	Label:
		size_hint_y: 0.1
	Label:
		text: root.subject
		text_size: self.size
		size_hint_y: 0.1
		halign: 'left'
		valign: 'middle'
	Label:
		size_hint_y: 0.1
	ScrollView:
		do_scroll_x: False
		do_scroll_y: True
		Label:
			size_hint_y: None
			size_hint_x: 1
			height: self.texture_size[1]
			text_size: self.width, None
			text: root.body
			halign: 'left'
			valign: 'middle'
	Label:
		size_hint_y: 0.1
	Label:
		text: root._date
		text_size: self.size
		size_hint_y: 0.1
		halign: 'right'
		valign: 'middle'

	BoxLayout: ###  reply field here
		height: dp(30)
		spacing: dp(8)
		size_hint_y: 0.2
		TextInput:
			id: reply_button
			hint_text: 'type reply'
			text_size: self.size
			halign: 'left'
			valign: 'middle'
		Button:
			text: 'Reply'
			on_press: root.reply(reply_button.text, root.body)
			size_hint_x: 0.2

<ScrollPage>:
	canvas:
		Color:
			rgba: 0.2, 0.1, 0.2, 1
		Rectangle:
			size: self.size
			pos: self.pos
	rv: rv
	orientation: 'vertical'
	GridLayout: ### top buttons
		cols: 2
		rows: 2
		size_hint_y: None
		height: dp(108)
		padding: dp(8)
		spacing: dp(16)
		Button:
			text: 'Populate list'
			on_press: root.populate()
		Button:
			text: 'Clear list'
			on_press: root.clear()
		BoxLayout:
			spacing: dp(8)
			Button:
				text: 'Add test card'
				size_hint_x: 0.4
				on_press: root.insert('me', 'about', new_item_input.text, 'today')
			TextInput:
				id: new_item_input
				size_hint_x: 1
				hint_text: 'body of message'
				padding: dp(10), dp(10), 0, 0
		Button:
			text: 'Fetch Mail'
			on_press: root.fetch_mail()

	RecycleView: ### infinite list
		id: rv
		scroll_type: ['bars', 'content']
		scroll_wheel_distance: dp(114)
		bar_width: dp(10)
		bar_color: [.3, .1, .3, .9]
		viewclass: 'Card'
		RecycleBoxLayout:
			default_size: None, None
			default_size_hint: 1, None
			padding: 45
			size_hint_y: None
			height: self.minimum_height
			orientation: 'vertical'
			spacing: dp(20)
<ConnectPage>
	canvas.before:
		Color:
			rgba: 0.2, 0.1, 0.2, 1
		Rectangle:
			pos: self.pos
			size: self.size
"""

Builder.load_string(kv)

class Card(BoxLayout):
	def reply(self, _text, body):
		print(_text, body)

class ScrollPage(BoxLayout):
	def __init__(self, **kwargs):
		#self.register_event_type('fetch_mail')
		super(ScrollPage, self).__init__(**kwargs)
		self.fetch_mail('')
		Clock.schedule_once(self.check_scroll, 2)


	def start_scroll():
		pass

	def check_scroll(self, _):
		# Define the point to start loading more cards
		# make sure we are on the scroll page screen
		if social_app.screen_manager.current == 'Scroll':
			# calculate a scroll position based on the height of one card
			scrollpos = self.rv.convert_distance_to_scroll(0, 500)[1]
			print("Print scroll ", scrollpos)
			# first load three cards, so we have something to scroll through
			if len(self.rv.data) < 1:
				Clock.schedule_once(self.fetch_mail, 0)
			# Then check our current scroll position against the one we calculated earlier
			if self.rv.scroll_y < scrollpos and len(self.rv.data) > 0:
				Clock.schedule_once(self.fetch_mail, 0)
				#self.rv.scroll_y = 0.3
			# schedule another check in 2 seconds
			Clock.schedule_once(self.check_scroll, 2)


	def populate(self):
		self.rv.data = [{'value': ''.join(sample(ascii_lowercase, 6))}
						for x in range(50)]

	def clear(self):
		global eNum
		global _first
		self.rv.data = []
		eNum = -1

	def insert(self, card_size, _from, subject, body, _date):
		#print ('inserting: ', _from, subject, body, _date)
		self.rv.data.append({
			'_from': _from or 'name',
			'subject': subject or 'subject line',
			'body': body or 'message body',
			'_date': _date or 'date line',
			'card_size': card_size
			})
		# Calculate the amount to move the scroll bar up, to compensate for the added card
		scroll_value = self.rv.convert_distance_to_scroll(0, card_size - 100)[1]
		if scroll_value < 1:
			self.rv.scroll_y = scroll_value

	def update(self, card_size, _from, subject, body, _date):
		if self.rv.data:
			self.rv.data[0]['_from'] = _from
			self.rv.data[0]['subject'] = subject
			self.rv.data[0]['body'] = body
			self.rv.data[0]['_date'] = _date
			self.rv.data[0]['card_size'] = card_size
			self.rv.refresh_from_data()

	def fetch_mail(self, _):
		global eNum
		email_recieved = SMail._read_mail(imap_host, smtp_port, imap_user, imap_pass, imap_folder, eNum)
		#print("got an email: ", email_recieved)
		if email_recieved['alreadyLoaded'] == True:
			print('trying next message')
			if eNum < -1:
				eNum -= 1
			return
		email_is_reply = False
		card_size = 500
		if email_recieved['inreply'] != None:
			print('message is a reply')
			card_size = 1000
			email_source = SMail._read_source(imap_host, smtp_port, imap_user, imap_pass, imap_folder, email_recieved['inreply'])
			if email_source != False:
				print('source found: ', email_source['subject'])
				email_is_reply = True
		if email_is_reply:
			self.insert(card_size, email_source['from'], email_source['subject'], email_source['body'], email_source['date'])
		if not email_is_reply:
			self.insert(card_size, email_recieved['from'], email_recieved['subject'], email_recieved['body'], email_recieved['date'])
		eNum -= 1

	def remove(self):
		if self.rv.data:
			self.rv.data.pop(0)
	# Gets called on key press
	def on_key_down(self, instance, keyboard, keycode, text, modifiers):
		# But we want to take an action only when Enter key is being pressed, and send a message
		if keycode == 40:
			self.send_message(None)

	# Gets called when either Send button or Enter key is being pressed
	# (kivy passes button object here as well, but we don;t care about it)
	def send_message(self, _):
		# Get message text and clear message input field
		message = self.new_message.text
		self.new_message.text = ''
		'''
		# If there is any message - add it to chat history and send to the server
		if message:
			# Our messages - use red color for the name
			self.history.update_chat_history(f'[color=dd2020]{social_app.connect_page.username.text}[/color] > {message}')
			socket_client.send(message)
		'''
		# As mentioned above, we have to shedule for refocusing to input field
		Clock.schedule_once(self.focus_text_input, 0.1)

	# Sets focus to text input field
	def focus_text_input(self, _):
		self.new_message.focus = True

	# Passed to sockets client, get's called on new message
	def incoming_message(self, _from, subject, body):
		# Update chat history with username and message, green color for username
		self.history.update_chat_history(f'[color=20dd20]{_from}[/color] > {subject} > {body}')

	# Updates page layout
	def adjust_fields(self, *_):
		# Chat history height - 90%, but at least 50px for bottom new message/send button part
		if Window.size[1] * 0.1 < 50:
			new_height = Window.size[1] - 50
		else:
			new_height = Window.size[1] * 0.9
		self.history.height = new_height
		# New message input width - 80%, but at least 160px for send button
		if Window.size[0] * 0.2 < 160:
			new_width = Window.size[0] - 160
		else:
			new_width = Window.size[0] * 0.8
		self.new_message.width = new_width
		# Update chat history layout
		#self.history.update_chat_history_layout()
		Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

class ConnectPage(GridLayout):
	# runs on initialization
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.cols = 2  # used for our grid
		self.padding = (50, 200)
		try:
			with open("prev_details.txt","r") as f:
				d = f.read().split(",")
				imap_host = d[0]
				imap_port = d[1]
				imap_user = d[2]
		except:
			print("No prev text found")

		self.add_widget(Label(text='IP:'))  # widget #1, top left
		self.ip = TextInput(text=imap_host, multiline=False)  # defining self.ip...
		self.add_widget(self.ip) # widget #2, top right

		self.add_widget(Label(text='Port:'))
		self.port = TextInput(text=imap_port, multiline=False)
		self.add_widget(self.port)

		self.add_widget(Label(text='Email:'))
		self.username = TextInput(text=imap_user, multiline=False)
		self.add_widget(self.username)

		self.add_widget(Label(text='Password:'))
		self.user_pass = TextInput(text=imap_pass, multiline=False)
		self.add_widget(self.user_pass)

		# add our button.
		self.login = Button(text="Login")
		self.login.bind(on_press=self.login_button)
		self.add_widget(Label())  # just take up the spot.
		self.add_widget(self.login)

	def login_button(self, instance):
		imap_port = self.port.text
		imap_host = self.ip.text
		imap_user = self.username.text
		imap_pass = self.user_pass.text
		with open("prev_details.txt","w") as f:
			f.write(f"{imap_host},{imap_port},{imap_user}")
		#print(f"Joining {ip}:{port} as {username}")
		# Create info string, update InfoPage with a message and show it
		info = "One moment please..."#f"Logging in {imap_host}:{imap_port} as {imap_user}"
		social_app.info_page.update_info(info)
		social_app.screen_manager.current = 'Info'
		Clock.schedule_once(self.connect, 1)

	# Connects to the server
	# (second parameter is the time after which this function had been called,
	#  we don't care about it, but kivy sends it, so we have to receive it)
	def connect(self, _):
		# Get information for sockets client
		global imap_port
		global imap_host
		global imap_user
		global imap_pass
		imap_port = int(self.port.text)
		imap_host = self.ip.text
		imap_user = self.username.text
		imap_pass = self.user_pass.text
		if not SMail._login(imap_host, imap_port, imap_user, imap_pass):
			social_app.screen_manager.current = 'Connect'
			return
		# Create chat page and activate it
		social_app.create_scroll_page()
		social_app.screen_manager.current = 'Scroll'


# Simple information/error page
class InfoPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		# Just one column
		self.cols = 1
		# And one label with bigger font and centered text
		self.message = Label(halign="center", valign="middle", font_size=30)
		# By default every widget returns it's side as [100, 100], it gets finally resized,
		# but we have to listen for size change to get a new one
		# more: https://github.com/kivy/kivy/issues/1044
		self.message.bind(width=self.update_text_width)
		# Add text widget to the layout
		self.add_widget(self.message)

	# Called with a message, to update message text in widget
	def update_info(self, message):
		self.message.text = message
	# Called on label width update, so we can set text width properly - to 90% of label width
	def update_text_width(self, *_):
		self.message.text_size = (self.message.width * 0.9, None)

class SocialApp(App):
	def build(self):
		# We are going to use screen manager, so we can add multiple screens
		# and switch between them
		self.screen_manager = ScreenManager(transition = WipeTransition())
		# Initial, connection screen (we use passed in name to activate screen)
		# First create a page, then a new screen, add page to screen and screen to screen manager
		self.connect_page = ConnectPage()
		screen = Screen(name='Connect')
		screen.add_widget(self.connect_page)
		self.screen_manager.add_widget(screen)

		# Info page
		self.info_page = InfoPage()
		screen = Screen(name='Info')
		screen.add_widget(self.info_page)
		self.screen_manager.add_widget(screen)
		return self.screen_manager

	# We cannot create chat screen with other screens, as it;s init method will start listening
	# for incoming connections, but at this stage connection is not being made yet, so we
	# call this method later
	def create_scroll_page(self):
		self.scroll_page = ScrollPage()
		screen = Screen(name='Scroll')
		screen.add_widget(self.scroll_page)
		self.screen_manager.add_widget(screen)

# Error callback function, used by sockets client
# Updates info page with an error message, shows message and schedules exit in 10 seconds
# time.sleep() won't work here - will block Kivy and page with error message won't show up
def show_error(message):
	social_app.info_page.update_info(message)
	social_app.screen_manager.current = 'Info'
	Clock.schedule_once(sys.exit, 10)

if __name__ == "__main__":
	social_app = SocialApp()
	social_app.run()
