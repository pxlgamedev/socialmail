extends PanelContainer

# Declare member variables here. Examples:
# var a = 2
# var b = "text"

# Called when the node enters the scene tree for the first time.
func _ready():
	get_tree().get_root().get_node("MailBox").connect("rectify_screen", self, "_rectify")

func _rectify(portr):
	if portr == false:
		self.size_flags_stretch_ratio = 0.5
	if portr == true:
		self.size_flags_stretch_ratio = 1
# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
