extends Node

var ver = "v0.1"

var imap_host
var imap_user = ""
var imap_pass = ""

var smtp_servers = {
	# smtp login, SMTP port, IMAP login, IMAP4_SSL port, folder name
	gmail = ["imap.gmail.com", 587, "imap.gmail.com", 993, "Inbox", "Sent"], #'"[Gmail]/All Mail"'
	Outlook = ["smtp-mail.outlook.com", 587, "imap-mail.outlook.com", 143, "Inbox", "Sent"],
	#Yahoo = ["smtp.mail.yahoo.com", 465, "imap.mail.yahoo.com", 993, "Inbox"],
	#Att = ["smtp.mail.att.net", 465, "imap.mail.att.net", 993, "Inbox"],
	#Comcast = ["smtp.comcast.net", 465, "imap.comcast.net", 993, "Inbox"],
	#Verison = ["smtp.verison", 465, "imap.verison", 993, "Inbox"],
	User = ["", 465, "", 993, "Inbox"],
}

var saveLoc = "user://contacts/"
var savePass = false # Use at your own peril: password will be stored in plain text if enabled
var postage = false # use to keep only a single thread loading mail

var store = {
	imap = "",
	user = "",
	pas = "", # will be stored in plain text if implimented
	ver = "",
}

var isLogedIn = false

var _mail = -1

func _ready():
	print("User data is stored in: ", OS.get_user_data_dir())
	# check if a Saves directory exists.
	var dir = Directory.new()
	if !dir.dir_exists(saveLoc):
		# if not we'll create it.
		dir.open("user://")
		dir.make_dir(saveLoc)
	load_data("prefs")
	imap_host = store.imap
	imap_user = store.user
	imap_pass = store.pas

func load_data(var fileName):
	# create a file object
	var loadData = File.new()
	# check that the file exists before trying to open it
	if !loadData.file_exists(saveLoc+fileName+".dta"):
		print ("Abort! Abort! No file to load...")
		store.imap = smtp_servers.gmail
		return
	# time to read the data in our file
	loadData.open(saveLoc+fileName+".dta", File.READ)
	# now simply overwrite store by parsing the loaded data
	store = parse_json(loadData.get_line())
	if typeof(store.imap) == 4: # TODO v0.2 temporary overwrite for v0.1 data, remove for v0.3
		print("Store is not list")
		print("Store is: ", store.imap)
		store.imap = smtp_servers.gmail
		print("Store is now: ", store.imap)
	store.imap[1] = int(store.imap[1]) # convert the ports from string to int
	store.imap[3] = int(store.imap[3])
	loadData.close()
	#Done!
	# DEBUG stuff: we'll just check that everything worked right
	print("Loaded data: ", store)

func save_data(var fileName):
	# create a file object
	var data = File.new()
	# create our save location
	data.open(saveLoc+fileName+".dta", File.WRITE)
	# write the data to disk
	data.store_line(to_json(store))
	# close the file
	data.close()
	# done

func save_password():
	store.imap = imap_host
	store.user = imap_user
	if savePass == true:
		store.pas = imap_pass
	if savePass == false:
		store.pas = ""
	save_data("prefs")
