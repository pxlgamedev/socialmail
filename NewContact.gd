extends VBoxContainer

signal reset_contacts

func _ready():
	pass # Replace with function body.

func edit_contact(email):
	for i in Contact_Book.store:
		print(i)
		if i.email == email:
			$fname.text = i.fname
			$lname.text = i.lname
			$email.text = i.email
			$address.text = i.address
			$country.text = i.country
			$phone.text = i.phone

func _on_Button_pressed():
	if $fname.text == "":
		$Error.text = "Please enter a name"
		return
	if $email.text == "":
		$Error.text = "Invalid Email"
		return
	if $fname.text != "" and $email.text != "":
		$Error.text = ""
		if "@" in $email.text and "." in $email.text:
			var fname = $fname.text
			var lname = $lname.text
			var email = $email.text
			var address = $address.text
			var country = $country.text
			var phone = $phone.text
			Contact_Book.newContact(fname, lname, email, address, country, phone)
			$fname.text = ""
			$lname.text = ""
			$email.text = ""
			$address.text = ""
			$country.text = ""
			$phone.text = ""
			print("Contact Added")
			emit_signal("reset_contacts")
			get_parent().current_tab = 0
			return
		$Error.text = "Invalid Email"
