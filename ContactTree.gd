extends Tree

signal update_to

var popup
var newBook # for adding a new contact book
var editing # selected item from right mouse clicking
var oldBook

func _ready():
	popup = self.get_child(0)
	popup.connect("index_pressed", self, "_on_item_pressed")
	call_deferred("build_contact_tree", true)

### Popup Menu ###

func build_popup_menu():
	popup.clear()
	popup.rect_size = Vector2(20,20)
	popup.add_item("New Contact")
	if "@" in editing.get_tooltip(0):
		popup.add_separator(editing.get_text(0))
		popup.add_item("Edit Contact")
		popup.add_separator(" add/remove ")
		var num = 5
		var email = editing.get_tooltip(0)
		for i in Contact_Book.customLists:
			if i[0] != null:
				num += 1
				var list = i[0]
				popup.add_check_item(list, num)
				var check = popup.get_item_index(num)
				print(check)
				popup.set_item_checked(check, false)
				for n in i:
					if n == email:
						popup.set_item_checked(check, true)
	if !"@" in editing.get_tooltip(0) and editing.get_text(0) != "Everyone":
		var num = 10
		popup.add_item("Edit Book Name")
		popup.add_item("Delete Book", num)
		var list = editing.get_text(0)
		var book = popup.get_item_index(num)
		for i in Contact_Book.customLists:
			if i[0] == list:
				if i.size() > 1:
					popup.set_item_disabled(book, true)
	popup.add_separator(" ")
	popup.add_item("New Contact Book")
	popup.popup()

func _on_item_pressed(IDX):
	#var IDX = popup.get_item_index(ID)
	var list = popup.get_item_text(IDX)
	print(list)
	if list == "New Contact":
		var tabs = self.get_parent()
		tabs.current_tab = 1
		print("New contact")
		return
	if "@" in editing.get_tooltip(0):
		if list == "Edit Contact":
			var tabs = self.get_parent()
			tabs.get_child(1).edit_contact(editing.get_tooltip(0))
			tabs.current_tab = 1
			return
		if !popup.is_item_checked(IDX):
			for i in Contact_Book.customLists:
				for n in i:
					if n == list:
						i.append(editing.get_tooltip(0))
		if popup.is_item_checked(IDX):
			for i in Contact_Book.customLists:
				for n in i:
					if n == list:
						i.erase(editing.get_tooltip(0))
		build_contact_tree(false)
		Contact_Book.call_deferred("save_custom_lists")
	if popup.get_item_text(IDX) == "New Contact Book":
		add_contact_tree()
	if popup.get_item_text(IDX) == "Edit Book Name":
		edit_list()
	if popup.get_item_text(IDX) == "Delete Book":
		var book = editing.get_text(0)
		var num = -1
		for i in Contact_Book.customLists:
			num += 1
			if i[0] == book:
				Contact_Book.customLists.remove(num)
		build_contact_tree(false)
		Contact_Book.call_deferred("save_custom_lists")

### Contact Tree ###

func edit_list():
	oldBook = editing.get_text(0)
	newBook = self.create_item()
	newBook.set_text(0, oldBook)
	newBook.set_editable(0, true)
	newBook.select(0)

func add_contact_tree():
	newBook = self.create_item()
	newBook.set_text(0, "New Book")
	newBook.set_editable(0, true)
	newBook.select(0)

func build_contact_tree(close):
	if oldBook == null:
		if self.get_children() != null:
			self.clear()
		var root = self.create_item()
		self.set_hide_root(true)
		var list1 = self.create_item(root)
		list1.set_cell_mode(0,1)
		list1.set_text(0, "Everyone")
		list1.set_tooltip(0, "")
		for i in Contact_Book.store:
			var contact = self.create_item(list1)
			contact.set_cell_mode(0,1)
			contact.set_text(0, (i.fname + " " + i.lname))
			#var email = self.create_item(contact)
			#email.set_text(0, i.email)
			#contact.set_collapsed(true)
			contact.set_tooltip(0, i.email)
		list1.select(0)
		list1.set_checked(0, false)
		list1.collapsed = close
		for i in Contact_Book.customLists:
			if i != null:
				print(i)
				var listName = i[0]
				var list2 = self.create_item()
				list2.set_cell_mode(0,1)
				list2.set_text(0, listName)
				list2.set_tooltip(0, "")
				list2.set_checked(0, false)
				list2.collapsed = true
				for n in i:
					if n != listName and n != null:
						var email = n
						var contactCopy = self.create_item(list2)
						contactCopy.set_cell_mode(0,1)
						var fname = ""
						var lname = ""
						for y in Contact_Book.store:
							if y.email == email:
								fname = y.fname
								lname = y.lname
						contactCopy.set_text(0, (fname + " " + lname))
						contactCopy.set_tooltip(0, email)
		_on_Tree_multi_selected(list1, 0, true)
		oldBook = null

func _on_Contacts_item_edited():
	if oldBook == null:
		var newList = newBook.get_text(0)
		if newList != "New Book":
			var email = editing.get_tooltip(0)
			var list_exists = false
			var email_in_list = false
			for i in Contact_Book.customLists:
				for n in i:
					if n == newList:
						list_exists = true
						print("list exists")
					if n == email:
						email_in_list =true
						print("email exists in list")
			if !list_exists:
				var newDict = []
				newDict.append(newList)
				if "@" in email and !email_in_list:
					newDict.append(email)
				Contact_Book.customLists.append(newDict)
	if oldBook != null:
		var newList = newBook.get_text(0)
		for i in Contact_Book.customLists:
			if i[0] == oldBook:
				i[0] = newList
		oldBook = null
	build_contact_tree(false)
	Contact_Book.call_deferred("save_custom_lists")

func _reset_contacts():
	build_contact_tree(true)

## Tree Selection ##

func _on_Tree_multi_selected(item, column, selected):
	var tooltip = item.get_tooltip(0)
	var check = item.is_checked(0)
	if selected:
		if check:
			item.set_checked(0, false)
			item.get_parent().set_checked(0, false)
			if item.get_children() != null:
				var child = item.get_children()
				while (child):
					child.set_checked(0, false)
					var email = child.get_tooltip(0)
					Contact_Book._current_mailing_list(email, false)
					var root = item.get_parent()
					var list = root.get_children()
					while (list):
						var contact = list.get_children()
						while(contact):
							if contact.get_tooltip(0) == email:
								contact.set_checked(0, false)
								contact.get_parent().set_checked(0, false)
							contact = contact.get_next()
						list = list.get_next()
					child = child.get_next()
		if !check:
			item.set_checked(0, true)
			if item.get_children() != null:
				var child = item.get_children()
				while (child):
					child.set_checked(0, true)
					child.select(0)
					Contact_Book._current_mailing_list(child.get_tooltip(0), true)
					child = child.get_next()
	if item.is_checked(0):
		if "@" in tooltip:
			Contact_Book._current_mailing_list(tooltip, true)
	if !item.is_checked(0):
		if "@" in tooltip:
			Contact_Book._current_mailing_list(tooltip, false)
			var root = item.get_parent().get_parent()
			var list = root.get_children()
			while (list):
				var contact = list.get_children()
				while(contact):
					if contact.get_tooltip(0) == tooltip:
						contact.set_checked(0, false)
						contact.get_parent().set_checked(0, false)
					contact = contact.get_next()
				list = list.get_next()
	emit_signal("update_to")
	#var contact = $item
	#print(contact.get_tooltip())

func _item_rmb_selected(position):
	editing = self.get_item_at_position(position)
	var mouse = self.get_global_mouse_position()
	popup.rect_position = mouse
	build_popup_menu()

func _on_Contacts_item_rmb_edited():
	print("here it is") # Replace with function body.
