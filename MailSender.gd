extends VBoxContainer

export var eNum = -1
export var msgTo = ""
export var msgSubject = ""
export var msgBody = ""

var mutex
var thread

func _ready():
	print(msgTo)
	$To.text = msgTo
	$Subject.text = msgSubject
	$Body.text = msgBody

func _send_mail():
	if User_Data.isLogedIn:
		msgTo = Contact_Book.sendTo
		msgSubject = $Subject.text 
		msgBody = $Body.text
		if msgTo != "":
			mutex = Mutex.new()
			thread = Thread.new()
			thread.start(self, "_thread_function", "Send Mail Thread")
	if msgTo == "":
		$Error.text = "Please enter a delivery address."
	if !User_Data.isLogedIn:
		$Error.text = "Error: No user loged in."

func _thread_function(userdata):
	# Call our py script in it's own thread
	print("I'm a thread! Userdata is: ", userdata)
	mutex.lock()
	$PyNode._sending_mail(User_Data.imap_host[0], User_Data.imap_host[1], User_Data.imap_user, User_Data.imap_pass, Contact_Book.mailingList, msgSubject, msgBody)
	mutex.lock()

# Thread must be disposed (or "joined"), for portability.
func _exit_tree():
	if thread != null:
		thread.wait_to_finish()

func _mail_sent():
	$Subject.text = ""
	$Body.text = ""
	$Error.text = "Message sent."

func _failed_to_send():
	$Error.text = "Please check delivery address."

func _on_Contacts_update_to():
	var names = ""
	print(Contact_Book.mailingList)
	for i in Contact_Book.mailingList:
		for n in Contact_Book.store:
			if n.email == i:
				names = (names + n.fname + " " + n.lname + " ")
	#to = (to + '"')
	print(names)
	Contact_Book.sendTo = names
	$To.text = names

func _on_Body_focus_entered():
	$Body.size_flags_stretch_ratio = 5
	$Error.size_flags_stretch_ratio = 0

func _on_Body_focus_exited():
	$Body.size_flags_stretch_ratio = 4
	$Error.size_flags_stretch_ratio = 1
