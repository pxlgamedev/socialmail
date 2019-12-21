extends Node

var store = [] # main contact list, containing dictionaries with info for each contact
var customLists = [] # a list of lists, each containing a string for a name, followed by a list of emails

var mailingList = [] # temp list of contacts for sending an email
var sendTo = "" # string for storing contact names

var saveLoc = "user://contacts/"

func _ready():
	list_files_in_directory()
	load_custom_lists()

func _current_mailing_list(email, add):
	var exists = false
	if add:
		for i in mailingList:
			if i == email:
				exists = true
		if !exists:
			mailingList.append(email)
	if !add:
		mailingList.erase(email)
	#print(mailingList)

func newContact(fname, lname, email, address, country, phone):
	var contact = {
		socialMail = User_Data.ver,
		fname = fname,
		lname = lname,
		email = email,
		address = address,
		country = country,
		phone = phone,
	}
	var data = File.new()
	# create our save location
	data.open(saveLoc+email+".crd", File.WRITE)
	# write the data to disk
	data.store_line(to_json(contact))
	# close the file
	data.close()
	store = []
	list_files_in_directory()

func list_files_in_directory():
	var files = []
	var dir = Directory.new()
	dir.open(saveLoc)
	dir.list_dir_begin()
	while true:
		var file = dir.get_next()
		if file == "":
			break
		elif not file.begins_with("."):
			if file.ends_with("crd"):
				files.append(file)
				#print(file)
				load_data(file)
	dir.list_dir_end()
	#print(files)

func load_data(var fileName):
	# create a file object
	var loadData = File.new()
	# check that the file exists before trying to open it
	if !loadData.file_exists(saveLoc+fileName):
		print ("Abort! Abort! No file to load...")
		return
	# time to read the data in our file
	loadData.open(saveLoc+fileName, File.READ)
	# now simply overwrite store by parsing the loaded data
	var contact = []
	contact = parse_json(loadData.get_line())
	store.append(contact)
	loadData.close()
	#Done!
	# DEBUG stuff: we'll just check that everything worked right
	#print("Loaded contacts: ", store)

func save_data(var fileName):
	# create a file object
	var data = File.new()
	# create our save location
	data.open(saveLoc+fileName+".crd", File.WRITE)
	# write the data to disk
	data.store_line(to_json(store))
	# close the file
	data.close()
	# done

func save_custom_lists():
	# create a file object
	var data = File.new()
	# create our save location
	data.open(saveLoc+"ContactBook.list", File.WRITE)
	# write the data to disk
	data.store_line(to_json(customLists))
	# close the file
	data.close()
	load_custom_lists()

func load_custom_lists():
	# create a file object
	var loadData = File.new()
	# check that the file exists before trying to open it
	if !loadData.file_exists(saveLoc+"ContactBook.list"):
		print ("Abort! Abort! No file to load...")
		return
	# time to read the data in our file
	loadData.open(saveLoc+"ContactBook.list", File.READ)
	# now simply overwrite store by parsing the loaded data
	var lists = []
	lists = parse_json(loadData.get_line())
	customLists = lists
	loadData.close()
