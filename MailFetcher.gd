extends Control

export var _mail = -1
export var msgFrom = ""
export var msgEmail = ""
export var msgSubject = ""
export var msgBody = ""
export var msgDate = ""

export var msgIsReply = false
export var originSub = ""
export var originBody = ""
export var originBcc = ""
export var originDate = ""

export var images = []
var hasImage = false
var tex = preload("texrect.tscn")

var thread
var mutex

func add_image(pool):
	var image = Image.new()
	var image_error = image.load_jpg_from_buffer(pool)
	if image_error != OK:
		image_error = image.load_png_from_buffer(pool)
		if image_error != OK:
			return
	var texture = ImageTexture.new()
	texture.create_from_image(image)
	images.append(texture)
	display_image()

func _print_mail():
	$From.bbcode_text = msgFrom
	$Subject.bbcode_text = msgSubject
	$Body.bbcode_text = msgBody
	$Date.bbcode_text = str("[right] ", msgDate, " ")
	$Buttons/Error.bbcode_text = ""
	if msgIsReply:
		$From.bbcode_text = User_Data.imap_user
		$Subject.bbcode_text = originSub
		$Body.bbcode_text = originBody
		$Date.bbcode_text = str("[right] ", originDate, " ")
		$Body.size_flags_stretch_ratio = 4
		$RepliesBox.size_flags_stretch_ratio = 4
		$RepliesBox/VBoxContainer/Control/VBoxContainer/From.bbcode_text = str(msgFrom, " wrote:")
		$RepliesBox/VBoxContainer/Control/VBoxContainer/Body.bbcode_text = msgBody
		$RepliesBox/VBoxContainer/Control/VBoxContainer/Date.bbcode_text = str("[right] ", msgDate, " ")
		$RepliesBox.visible = true
	User_Data.postage = true

func display_image():
	$ImageBox/TextureRect.texture = images[0]
	$Body.size_flags_stretch_ratio = 3
	$ImageBox.visible = true
	var newImage = tex.instance()
	$ImageBox/MultiImageBox.add_child(newImage)
	newImage.texture_normal = images[-1]
	newImage.connect("pressed", self, "_change_image", [newImage.texture_normal])
	if 	$ImageBox/MultiImageBox.get_child_count() > 1:
		$ImageBox/MultiImageBox.visible = true

func _change_image(image):
	print("clicked")
	$ImageBox/TextureRect.texture = image

func _scrolling_mail(mail):
	_mail = mail
	mutex = Mutex.new()
	thread = Thread.new()
	thread.call_deferred("start", self, "_thread_function", "Fetching Mail")
	$Buttons/Error.bbcode_text = "[center]Loading..."

func _thread_function(userdata):
	mutex.lock()
	$PyNode._read_mail(User_Data.imap_host[2], User_Data.imap_host[3], User_Data.imap_user, User_Data.imap_pass, User_Data.imap_host[4], _mail, User_Data.imap_host[5])
	mutex.unlock()

func _exit_tree():
    thread.wait_to_finish()

func _on_Reply_pressed():
	var subject = "Re: " + msgSubject
	var message = $Reply.text
	### send to original bcc and include current message
	$PyNode._sending_mail(User_Data.imap_host[0], User_Data.imap_host[1], User_Data.imap_user, User_Data.imap_pass, msgEmail, subject, message)

func _mail_sent():
	$Buttons/Error.text = "Replied"
	$Reply.text = ""

func _failed_to_send():
	$Buttons/Error.text = "Failed"

func _on_Reply_focus_entered():
	$Reply.size_flags_stretch_ratio = 3
	if !msgIsReply and !hasImage:
		$Body.size_flags_stretch_ratio = 6
	if msgIsReply and !hasImage:
		$Body.size_flags_stretch_ratio = 2
		$RepliesBox.size_flags_stretch_ratio = 4

func _on_Reply_focus_exited():
	$Reply.size_flags_stretch_ratio = 1
	if !msgIsReply and !hasImage:
		$Body.size_flags_stretch_ratio = 8
	if msgIsReply and !hasImage:
		$Body.size_flags_stretch_ratio = 4
		$RepliesBox.size_flags_stretch_ratio = 4
