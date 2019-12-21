extends VBoxContainer

var thread
var popup

func _ready():
	popup = $ServerSel/Popup
	popup.connect("index_pressed", self, "_on_item_pressed")
	thread = Thread.new()
	$IMAP.text = User_Data.imap_host[0]
	$ServerSel.text = User_Data.imap_host[0]
	$User.text = User_Data.imap_user
	$Pass.text = User_Data.imap_pass
	if $Pass.text == "":
		$Pass.grab_focus()
	if $User.text == "":
		$User.grab_focus()
	if $User.text != "" and $Pass.text != "":
		_login_button()
	#print("testing print of utf8:"  + char(356))

func _login_button():
	User_Data.imap_host[0] = $IMAP.text
	User_Data.imap_user = $User.text
	User_Data.imap_pass = $Pass.text
	$Error.text = "Verifying Login..."
	#print("Verifying...")
	#$PyNode._login(User_Data.imap_host, User_Data.imap_user, User_Data.imap_pass)
	thread = Thread.new()
	thread.call_deferred("start", self, "_thread_function", "Login Thread")

func _thread_function(userdata):
	# Call our py script in it's own thread
	$PyNode.call("_login", User_Data.imap_host[0], User_Data.imap_host[1], User_Data.imap_user, User_Data.imap_pass)

# Thread must be disposed (or "joined"), for portability.
func _exit_tree():
	thread.wait_to_finish()

func _failed_login():
	User_Data.isLogedIn = false
	$Error.text = "Login failed. Please check user name and password."
	
func _loged_in():
	print("success")
	User_Data.isLogedIn = true
	$Error.text = "Successfully Logged in."
	get_tree().get_root().get_node("MailBox")._ready_mail_box()
	var tabs = get_parent().get_parent().get_parent()
	#tabs.set_tab_disabled (1, false)
	#tabs.set_tab_disabled (2, false)
	tabs.current_tab = 1
	User_Data.save_password()

func _on_Pass_text_entered(new_text):
	_login_button()


func _on_ServerSel_pressed():
	var mouse = self.get_global_mouse_position()
	popup.rect_position = mouse
	popup.rect_size = Vector2(20,20)
	popup.clear()
	for i in User_Data.smtp_servers:
		if i != "":
			var server = i
			if i == 'Att':
				server = "AT&T"
			popup.add_item(server)
	popup.popup()

func _on_item_pressed(IDX):
	var list = popup.get_item_text(IDX)
	print(list)
	if list == "gmail":
		User_Data.imap_host = User_Data.smtp_servers.gmail
	if list == "Outlook":
		User_Data.imap_host = User_Data.smtp_servers.Outlook
	if list == "Yahoo":
		User_Data.imap_host = User_Data.smtp_servers.Yahoo
	if list == "AT&T":
		User_Data.imap_host = User_Data.smtp_servers.Att
	if list == "Comcast":
		User_Data.imap_host = User_Data.smtp_servers.Comcast
	if list == "Verison":
		User_Data.imap_host = User_Data.smtp_servers.Verison
	$IMAP.visible = false
	if list == "User":
		$IMAP.visible = true
	$ServerSel.text = list
	$IMAP.text = User_Data.imap_host[0]
