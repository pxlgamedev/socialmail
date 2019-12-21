extends Node2D


func _ready():
	pass # Replace with function body.


func _process(delta):
	if Input.is_action_just_pressed("ui_accept"):
		get_tree().change_scene("SocialMail.tscn")
