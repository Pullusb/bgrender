### Blender background rendering script --- Samuel.B ###
# -*- coding: cp1252 -*-
import os
import sys
import re
import datetime

## uncomment bottom line to set current working directory to script location :
# os.chdir(os.path.dirname(sys.argv[0]))

def checknum(inp):
	try:
		int(inp)
	except ValueError:
		return True
	else:
		return False

def numchoice(number):
	try:
		int(number)
	except ValueError:
		return True
	else:
		if number != "1" and number != "2":
			return True
		else:
			return False

def choice(chosen):
	if chosen != "y" and chosen != "n":
		return True
	else:
		return False

def userinput(choosetype, ask, askhelp):
	mod = str.lower(raw_input(ask)).strip()
	while choosetype(mod):
		mod = str.lower(raw_input(askhelp)).strip()
	return mod

def timestamp():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def timesub(date_str):
	return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

###beginning of the script and display###
separator = "--------------------"
print separator
print "current location : " + os.getcwd()

myOS = sys.platform

poweroff = "shutdown -h"
slash = '/'
if myOS == "linux" or myOS == "linux2":
	# linux
	print "operating system : Linux"

elif myOS == "darwin":
	# OS X
	print "operating system : MACos"

elif myOS == "win32" or myOS == "win64":
	# Windows
	print "operating system : Windows"
	poweroff = 'shutdown /s /t 60 /c "render as finished, power off in 1 minutes"'
	slash = '\\'

else:
	print "your system '"+ sys.platform + "' was not recognized automatically by the script\nOS specific command power off will be set as Unix"

#choose your background rendering parameters
print "help : write 'help' anytime"
print separator + "\n"

###inputs of the user###
#get filename
unfound = True
while unfound:
	filename = raw_input('Enter the name of your blendfile (extension not necessary): ').strip()
	while filename == "help" or not filename:
		filename = raw_input('Ex : "myfile.blend" or "myfile" if your in the same directory as the script.\nelse add the path : "subdir/myfile" or "subdir/myfile.blend" (without quotes)\nWrite your filename : ').strip()
	input_ext = re.search(r'\.[Bb][Ll][Ee][Nn][Dd].*', filename)
	if not input_ext:
		filename = filename + ".blend"
		print 'extension added'
	if not os.path.exists(filename):
		print separator
		print "ERROR ! " + filename + " was not found in the current working directory :\n" + os.getcwd() + "\nIf your file isn't in this directory you need to add the path before(without slash at the beginning)."
		retryname = userinput(choice,
			'Retry? (y/n) : ',
			'"y" will prompt again file name, "n" will pass this step with even if detection of the file failed\n Retry? (y/n): ')
		if retryname == "n":
			unfound = False
	else:
		unfound = False

#dislay file name
if os.path.exists(filename):
	print "file checked"
print "working on : " + filename

shortfilename = filename[:-6]

##choose the render mode
rendermode = userinput(numchoice,
	'1/image or 2/animation? : ',
	'Please enter "1" for a still image or "2" for an animation : ')

if rendermode == "1":
	##one frame only
	#choose frame
	framenum = raw_input('Frame number : ').strip()
	while not framenum or checknum(framenum):
		framenum = raw_input('Please enter the number of the frame to render : ').strip()

elif rendermode == "2":
	##animation
	#choose between blend file frame range and manual set
	animmode = userinput(choice,
		'Set frame range manually? (y/n): ',
		'Please enter "n" to use the frame range preset in your blend file or "y" to enter manually : ')

	if animmode == "y":
		#enter frame range manually
		framestart = userinput(checknum,
			'Start frame : ',
			'Set the beginning frame of your animation : ')
		frameend = raw_input('End frame : ').strip()
		while checknum(frameend) or int(frameend) < int(framestart):
			frameend = raw_input('Set the final frame of your animation (it must be a equal or higher number than start): ').strip()

##choose if a specific name must be set
outputmode = userinput(choice,
	'Set output path and name manually? (y/n):  ',
	'Please enter "n" to leave blend file preset for output or "y" to set it : ')

#set output
if outputmode == "y":
	#write the path/outputname
	print "--------help--------\nUse // at the start of the path to render relative to the blend file.\nThe # characters are replaced by the frame number, and used to define zero padding.\nani_##_test.png becomes ani_01_test.png\ntest-######.png becomes test-000001.png\nWhen the filename has no #, The suffix #### is added to the filename\nThe frame number will be added at the end of the filename.\n--------------------"
	#full path display
	print "current location of output : " + os.getcwd() + slash
	output = raw_input('Write the path and output name according to the help above : ').strip()
	while not output:
		output = raw_input('Write your output name (ex : "img_" or "render/imgs_####" wihtout quotes): ').strip()

##choose if a log file must be created
logfile = userinput(choice,
	'Generate a log file (command and rendertime infos)? (y/n): ',
	'If "y" a log file with current command and start/end/elapsed time infos will be created (y/n): ')

##choose if an OS script with all the parameters before must be created
scriptmode = userinput(choice,
	'Generate a "quick script" file to save your parameters ? (y/n): ',
	'If "y" a script file will be created with all the parameter entered before.\n"n" do nothing (y/n): ')

#command assemblage
command = "blender -b " + filename
if outputmode == "y":
	command = command + " -o " + output

if rendermode == "1":
	command = command + " -f " + framenum
else:
	if animmode == "n":
		command = command + " -a"
	else:
		command = command + " -s " + framestart + " -e " + frameend + " -a"

if scriptmode == "y":
	#script creation
	waitcount = "2"
	print separator
	pyscript = shortfilename + "_bg_launcher.py"
	header = "#script created with blender_background_launcher.py#\n"
	pyhead = [
		"import os\n",
		"import time\n"]
	pyverbose = [
		'print "launching command in ', waitcount, ' seconds:"\n',
		'time.sleep(', waitcount, ')\n']
	pytime = ["import datetime\n\n",
		"def timestamp():\n",
		"\treturn datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')\n\n",
		"def timesub(date_str):\n",
		"\treturn datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')\n\n"]
	pylog1 = [
		'log = "', shortfilename, '_log.txt"\n',
		"logdoc = open(log, 'a')\n",
		'logdoc.write("', command, '\\n")\n',
		'logdoc.write("started : " + startrender + "\\n")\n',
		'logdoc.close()\n\n'
		]
	pylog2 = [
		"\nlogdoc = open(log, 'a')\n",
		'logdoc.write("ended   : " + endrender + "\\n")\n',
		'logdoc.write("elapsed : " + lapse + "\\n")\n',
		'logdoc.write("', separator ,'\\n")\n',
		'logdoc.close()\n'
		]
	scmd = 'os.system("' + command + '")\n'
	if not os.path.exists(pyscript):
		scriptfile = open(pyscript, 'a')
		scriptfile.write(header)
		scriptfile.writelines(pyhead)
		scriptfile.writelines(pytime)
		scriptfile.writelines(pyverbose)
		scriptfile.write("startrender = timestamp()\n")
		scriptfile.write('print "started at : " + startrender\n')
		if logfile == "y":
			scriptfile.writelines(pylog1)
		scriptfile.write(scmd)
		scriptfile.write("endrender = timestamp()\n")
		scriptfile.write('lapse = str(timesub(endrender) - timesub(startrender))\n')
		if logfile == "y":
			scriptfile.writelines(pylog2)
		scriptfile.write('print "ended at : " + endrender\n')
		scriptfile.write('print "elapsed  : " + lapse\n')
		scriptfile.close()
		print '"quick script" generated : ' + pyscript
	else:
		scriptfile = open(pyscript, 'a')
		scriptfile.write('#---next-command---\n')
		scriptfile.write("startrender = timestamp()\n")
		scriptfile.write('print "started at : " + startrender\n')
		if logfile == "y":
			scriptfile.writelines(pylog1)
		scriptfile.write(scmd)
		scriptfile.write("endrender = timestamp()\n")
		scriptfile.write('lapse = str(timesub(endrender) - timesub(startrender))\n')
		if logfile == "y":
			scriptfile.writelines(pylog2)
		scriptfile.write('print "ended at : " + timestamp()\n')
		scriptfile.write('print "elapsed  : " + lapse\n')
		scriptfile.close()
		print '"' + pyscript + "' script detected, current command added to previous\nQuick script will run multiple-job for " + shortfilename + "\nBe carefull with output path (risk of overwriting image file)"
		print separator
	if logfile == "y":
		print "NOTE : The quick sript will also create/edit logfiles"
	
powermode = userinput(choice,
	'/!\ POWER OFF the computer when render finish ? (y/n): ',
	'if "y" the computer will be SHUTDOWN after rendering end\n"n" will do nothing (y/n): ')

#shutdown alert
if powermode == "y":
	print '---/!\---> Computer will shutdown after rendering'
	if scriptmode == "y":
		print 'NOTE: The"power off" command is not added to the "quick script" previously created'

#ask if render now
launchrender = userinput(choice,
	'Launch the render now ("n" answer will exit)? (y/n): ',
	'If "y" the script will launch the render with your parameter. "n" will exit the script(y/n): ')
if launchrender == "n":
	exit()

#create the log file
if logfile == "y":
	log = shortfilename + "_log.txt"
	if rendermode == "1":
		os.system("echo " + filename + " - frame " + framenum + " >> " + log)
	else:
		if animmode == "y":
			os.system("echo " + filename + " - animation from " + framestart + " to " + frameend + " >> " + log)
		else:
			os.system("echo " + filename + " - animation" + " >> " + log)
	os.system("echo " + command + " >> " + log)
	startrender = timestamp()
	os.system("echo render start : " + startrender + " >> " + log)
	print log + " file created"

print "executing : " + command
os.system(command)
endrender = timestamp()
print "render finished : " + endrender 

#log endtimeupdate
if logfile == "y":
	os.system("echo render end : " + endrender + " >> " + log)
	elapsed = str(timesub(endrender) - timesub(startrender))
	print elapsed
	loghandle = open(log, 'a')
	loghandle.write("rendertime : " + elapsed + "\n")
	loghandle.write(separator + "\n")
	loghandle.close()
	print "log file updated"

#poweroff computer
if powermode == "y":
	os.system(poweroff)