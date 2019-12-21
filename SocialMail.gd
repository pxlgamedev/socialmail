extends Control

signal rectify_screen

export var msgFrom = ""
export var msgSubject = ""
export var msgBody = ""

func _ready():
	pass
	#$Margin/MenuTabs.set_tab_disabled (2, true)
	#$Margin/MenuTabs.set_tab_disabled (1, true)

func _ready_mail_box():
	User_Data.postage = true

func freeze_scroll():
	print("freezing")

func thaw_scroll():
	print("thawing")

func _on_Margin_resized():
	#self.rect_size = OS.get_window_size()
	if $Margin.rect_size.x > $Margin.rect_size.y:
		emit_signal("rectify_screen", true)
	if $Margin.rect_size.x < $Margin.rect_size.y:
		emit_signal("rectify_screen", false)
