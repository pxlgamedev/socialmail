extends ScrollContainer

export var sepMargin = -500
export var numofcards = 30

var vrect = 0
var vcard = 0
var postage = 0

onready var card = preload("res://SocialMailCard.tscn")

func _ready():
	#get_tree().get_root().connect("size_changed", self, "update_scroll")
	update_scroll()

func add_card(input):
	print(input)
	var newCard = card.instance()
	newCard.get_child(0).get_child(2).get_child(0)._scrolling_mail(User_Data._mail)
	$VBoxContainer.call_deferred("add_child", newCard)
	User_Data._mail -=1

func add_old_card(input):
	print(input)
	var goback = User_Data._mail + numofcards
	if goback >= 0:
		return
	var oldCard = card.instance()
	var topCard = $VBoxContainer/Control
	oldCard.get_child(0).get_child(1).get_child(0)._scrolling_mail(goback)
	$VBoxContainer.call_deferred("add_child_below_node", topCard, oldCard)
	User_Data._mail +=1

func update_scroll():
	vrect = self.rect_size.y + sepMargin
	vcard = vrect
	print(self.rect_size.y, " ", vrect, " ", vcard)
	$VBoxContainer.add_constant_override("separation", vrect)
	self.scroll_vertical = 0

func _physics_process(delta):
	if User_Data.postage == true:
		if $VBoxContainer.get_child_count() < 5:
			User_Data.postage == false
			add_card("First Card")
		if self.scroll_vertical < (vrect * 2):
			if User_Data._mail + numofcards < 0:
				print("Checking mail", User_Data._mail + numofcards)
				add_old_card("Adding first card")
				if $VBoxContainer.get_child_count() > numofcards:
					print("removing last card")
					var lastCard = $VBoxContainer.get_child(numofcards)
					lastCard.call_deferred("queue_free")
					self.scroll_vertical += vrect
		if self.scroll_vertical > vcard:
			print("checking mail ", User_Data._mail)
			add_card("Adding last card")
			if $VBoxContainer.get_child_count() > numofcards:
				var firstCard = $VBoxContainer.get_child(1)
				firstCard.call_deferred("queue_free")
				print("first card deleted")
				self.scroll_vertical -= vrect
			if $VBoxContainer.get_child_count() < numofcards:
				vcard += vrect
