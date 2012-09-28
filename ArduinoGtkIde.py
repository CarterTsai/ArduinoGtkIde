#! /usr/bin/env python

print """
    ArduinoGtkIde  Copyright (C) 2009  Harry van Haaren

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under the conditions of the GNU General Public License
    either version 3 of the License, or (at your option) any later version.
"""


#		ArduinoGtkIde. A development Enviroment for AVR based microchips.
#		Copyright (C) 2009  Harry van Haaren <harryhaaren@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, see <http://www.gnu.org/licenses/>.


import os
import sys
import gtk
import gobject
import gtk.glade
import subprocess
import shutil

#--- Set Program run variables ---
DEBUG = False
DEBUG_BUILD = False
DEBUG_FILE = False
DEBUG_SERIAL = False
DEBUG_WINDOW = False
DEBUG_SYNTAX_HIGHLIGHT = False

__version__ = "0.0.1"
__author__  = "Harry van Haaren <harryhaaren@gmail.com>"
#--- I realize this is program is quite messy and sloppy,it has thought me a lot about python,
#	 And in my next project, I do think that I will adhere to the OOP standards a bit more ;)

#--- Define sys.path so it loads LOCAL modules before modules in /usr/lib/python
#--- Allows me to have a "customized" colour scheme by editing gtkcodebuffer.py in the syntax folder.
sys.path.insert(0,"./lib/")
sys.path.insert(0,"./lib/codebuffer/")
sys.path.insert(0,"./lib/resources/")

import compile
import gtkcodebuffer 		#-- Must be loaded AFTER sys.path.insert. Otherwise the wrong version is used.
import serial				#-- Same.

gtkcodebuffer.add_syntax_path("./lib/codebuffer/syntax")  # Must be done after importing the module.
print ""
if DEBUG: print "Serial  loaded from:",serial.__file__
if DEBUG: print "Compile loaded from:", compile.__file__
if DEBUG: print "GtkCodeBuffer loaded from:",gtkcodebuffer.__file__
if DEBUG: print ""


#--- Start Main Program
print "Click Connect to turn on Serial Monitoring."

class main:
	
	# --- Default Enviromental Variables ---
	Filename = ""
	arduinoLocation = "/dev/ttyUSB0"
	connectionError = "there is no active connection to an Arduino."
	connectedToArduino = False
	autoOpenLastFileBool = True
	
	
	def __init__					(self):
		# Load Glade XML
		self.xml = gtk.glade.XML("ui.glade")
		
		# Get Window
		self.mainWindow = self.xml.get_widget('mainWindow')			# mainwindow = MainApp, newFile = NewFile,preferencesWindow = Preferences, about = About.
		self.mainWindow.connect("delete_event", self.quit)
		self.mainWindow.connect("destroy", self.quit)
		
		# Get Windows child
		#self.mainWindow_child = self.mainWindow.get_child()
		
		# Get our Label
		self.label = self.xml.get_widget('label1')
		
		# Connect functions to Buttons
		self.quitButton = self.xml.get_widget('quit')
		self.quitButton.connect('clicked', self.quit)

		self.aboutWindow = self.xml.get_widget("aboutWindow") # aboutWindow.run(), aboutWindow.hide() take care of closing & reopening.

		self.compileWindow = self.xml.get_widget("feedbackDialog")
		self.compileWindow.connect("destroy",self.quitCompileWindow)
		self.compileWindow.connect("delete_event",self.quitCompileWindow)
		
		self.compileWindowCancel = self.xml.get_widget("feedbackClose")
		self.compileWindowCancel.connect("clicked",self.quitCompileWindow)
		
		self.connectButton = self.xml.get_widget("connectButton")
		self.connectButton.connect ("clicked",self.changeSerialConnectionState)
		
		self.textArea = self.xml.get_widget("mainTextArea")
		self.textAreaBuffer = self.textArea.get_buffer()
		
		# -- Attempt at line numbers... to be continued!
		#self.textArea.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 30)
		#self.textArea.connect("expose_event", self.line_numbers_expose)


		self.actionLabel = self.xml.get_widget("actionLabel")
		self.feedbackLabel = self.xml.get_widget("feedbackLabel")
		self.resultLabel = self.xml.get_widget("resultLabel")
		
		self.serialTextArea = self.xml.get_widget("serialTextArea")
		self.serialTextAreaBuffer = self.serialTextArea.get_buffer()
		
		self.preferencesButton = self.xml.get_widget("preferences")
		self.preferencesButton.connect("clicked",self.preferencesWindow)
		
		self.preferencesWindow = self.xml.get_widget("preferencesWindow")
		self.preferencesWindow.connect("destroy",self.quitPreferencesWindow)
		self.preferencesWindow.connect("delete_event",self.quitPreferencesWindow)
		
		self.newFileWindow = self.xml.get_widget("newFile")
		self.newFileWindow.connect("delete_event",self.quitNewFileWindow)
		self.newFileWindow.connect("destroy",self.quitNewFileWindow)
		
		self.newFileNameEntry = self.xml.get_widget("newFileNameEntry")
		self.newFileNameEntryBuffer = self.newFileNameEntry.get_text()
		
		self.newFileOkButton = self.xml.get_widget("newFileOk")
		self.newFileOkButton.connect("clicked",self.newFileProduction)
		
		self.newFileCancelButton = self.xml.get_widget("newFileCancel")
		self.newFileCancelButton.connect("clicked",self.newFileCancel)
		
		
		self.executeButton = self.xml.get_widget("execute")
		self.executeButton.connect("clicked",self.compileSketch)
		
		self.applyButton = self.xml.get_widget("apply")
		self.applyButton.connect("clicked",self.uploadSketch)
		
		self.arduinoLocationDropBox = self.xml.get_widget("arduinoLocationDropBox")
		self.arduinoLocationDropBox.connect("changed",self.updateArduinoLocation)
		
		self.arduinoCpuDropBox = self.xml.get_widget("arduinoCpuDropBox")
		self.arduinoCpuDropBox.connect("changed",self.updateArduinoBoard)
		
		self.serialTextAreaScroller = self.xml.get_widget("scrolledwindowSerialTextArea")
		self.serialTextAreaScrollerValue = self.serialTextAreaScroller.get_vadjustment()
		self.serialTextAreaScrollerHValue = self.serialTextAreaScroller.get_hadjustment()
		
		self.sendSerialEntry = self.xml.get_widget("sendSerialEntry")
		self.sendSerialEntryBuffer = self.sendSerialEntry.get_text()
		
		self.baudrateEntry = self.xml.get_widget("baudrateEntry")
		self.baudrateEntryBuffer = self.baudrateEntry.get_text()
		
		self.baudrateButton = self.xml.get_widget("baudrateButton")
		self.baudrateButton.connect ("clicked",self.updateBaudrate)
		
		self.sendSerialButton = self.xml.get_widget("sendSerialButton")
		self.sendSerialButton.connect("clicked", self.sendSerialData)
		
		self.newButton = self.xml.get_widget("new")
		self.newButton.connect("clicked",self.newFile)
		
		self.saveButton = self.xml.get_widget("save")
		self.saveButton.connect("clicked",self.saveFile)

		self.aboutButton = self.xml.get_widget('about')
		self.aboutButton.connect('clicked', self.about)
		
		self.openButton = self.xml.get_widget('open')
		self.openButton.connect('clicked',self.openWindow)
		
		#--- Open File Dialoge ---
		self.openWindow = self.xml.get_widget("openWindow")
		self.openWindow.connect("delete_event",self.quitOpenWindow)
		self.openWindow.connect("destroy",self.quitOpenWindow)
		
		self.openWindowFileChooser = self.xml.get_widget("fileChooser")
		
		self.openWindowOpenButton = self.xml.get_widget("openWindowOpen")
		self.openWindowOpenButton.connect("clicked",self.openWindowOpen)
		
		self.openWindowCloseButton = self.xml.get_widget("openWindowClose")
		self.openWindowCloseButton.connect("clicked",self.openWindowClose)
		#--- End Open File Dialoge ---


		# self.widget will be attached to the Activity
		# This can be any GTK widget except a window
		#self.widget = self.mainWindow_child
		self.mainWindow.show_all()
		
		self.startSyntaxHighlighing()
		self.autoOpenLastFile()
		# GTK gets active
		self.gtkMain()
		return None
		
		
	def compileSketch				(self,*args):
		
		self.saveFile() # Saves textBuffer to Disk. Make compiles Disk version.
		try:
			returnData = "Failed to assign a compile error."
			feedbackLabel = "Blank string"
			if DEBUG_BUILD: print "Starting Compile.."
			self.oldWorkingDir = os.getcwd()
			if DEBUG_BUILD: print "Current Working Dir:",str(os.getcwd() )
			try:
				os.chdir(str(os.getcwd() )+"/sketches/"+self.Filename+"/" ) 
			except:
				print "Error changing directories"
				return False
			if DEBUG_BUILD: print "New Working Dir:",str(os.getcwd() )

		
			if DEBUG_BUILD: print "Calling Compile..."
			print ""
			compileOut,compileErr = compile.compileSketch()
			print "Compiler Output",compileOut

			if compileErr == "":
				if DEBUG_BUILD: print "Compiler Error is blank. IE Successfull compile!"
				self.compileFeedback("Compiling Sketch...",str(compileOut),"Please wait...")
				print "Done Compiling."
				self.compileFeedback("Compiling Sketch...",str(compileOut),"Finished Successfully!")
					
				if DEBUG_BUILD: print "Finished. Returning to old Working Dir..."
				os.chdir(self.oldWorkingDir)
				return True
			else:
				print "Error in Compiling: "
				print compileErr
				self.compileFeedback("Compiling Sketch...",str(compileErr),"Error: See above for details.")
				os.chdir(self.oldWorkingDir)
				return False
			
		except:
			print "Error in Compiling: Compiler not found."
			print compileErr
			self.compileFeedback("Compiling Sketch...","Error in Compiling: Compiler not found.\nPlease ensure you have make & avr-gcc & avr-libc installed.","Error: See above for details.")
			os.chdir(self.oldWorkingDir)
			return False
		
			#'str(compileOut)+"\n\n"+str(compileErr)
	
	def uploadSketch				(self,*args):
		reconnectLater = False
		
		if self.connectedToArduino == True:
			reconnectLater = True
			self.changeSerialConnectionState()			

		try:
			returnData = "Failed to assign an Upload error."
			feedbackLabel = "Blank string"
			if DEBUG_BUILD: print "Starting Upload..."
			self.oldWorkingDir = os.getcwd()
			if DEBUG_BUILD: print "Current Working Dir:",str(os.getcwd() )
			try:
				os.chdir(str(os.getcwd() )+"/sketches/"+self.Filename+"/" ) 
			except:
				print "Error changing directories"
				if (reconnectLater ==True):
					self.changeSerialConnectionState()
				return False
			if DEBUG_BUILD: print "New Working Dir:",str(os.getcwd() )

		
			if DEBUG_BUILD: print "Calling Upload..."
			print ""
			uploadOut,uploadErr = compile.uploadSketch()
			print "Upload Output",uploadOut

			if uploadErr == "":
				print "EQUALS BLANK"
				self.compileFeedback("Uploading Sketch...",str(uploadOut),"Please wait...")
				print "Done Compiling."
				self.compileFeedback("Uploading Sketch...",str(uploadOut),"Finished Successfully!")
					
				if DEBUG_BUILD: print "Finished. Returning to old Working Dir..."
				os.chdir(self.oldWorkingDir)
				
				if (reconnectLater ==True):
					self.changeSerialConnectionState()
				return True
			else:
				print "Error in Uploading: "
				print uploadErr
				self.compileFeedback("Upload Sketch...",str(uploadErr),"Error: See above for details.",)
				os.chdir(self.oldWorkingDir)
				
				if (reconnectLater ==True):
					self.changeSerialConnectionState()
				return False
			
		except:
			print "Error in Upload: Uploader not found."
			print compileErr
			self.compileFeedback("Compiling Sketch...","Error in Upload: Uploader not found.\nPlease ensure you have make & avr-gcc & avr-libc installed.","Error: See above for details.")
			os.chdir(self.oldWorkingDir)
			return False
		

	def compileFeedback				(self,actionLabel,feedbackLabel,resultLabel,*args):

		self.actionLabel.set_text(actionLabel)
		self.feedbackLabel.set_text(feedbackLabel)
		self.resultLabel.set_text(resultLabel)
		self.compileWindow.set_title("Compilation & Uploading Info")
		self.compileWindow.show_all()
		
		return True
	
	
	def autoOpenLastFile			(self,*args):
		try:	
			if (self.autoOpenLastFileBool == True):
				if DEBUG_FILE: print "Starting Auto Open Last Sketch..."
				lastFile = open("./sketches/quit.pde","r")
				if DEBUG_FILE: print "lastFile opend OK"
				try:
					if DEBUG_FILE: print "Opening last sketch"
					self.Filename = lastFile.read()
					if DEBUG_FILE: print "Self.Filename on AutoOpen:", self.Filename
					openFile = open("./sketches/"+str(self.Filename)+"/"+str(self.Filename)+".pde","r")
					if DEBUG_FILE: print "Setting Text buffer"
					self.textAreaBuffer.set_text(openFile.read() )
					openFile.close()
				except:
					print "Could not auto-open last file. File does not exist."
			return True
		except:
			print "Warning: File quit.pde does not exist in the sketches folder."
			print "         Creating a new one..."
			file = open("./sketches/quit.pde","w")
			file.close()
			print "         Finished..."
			
			return False
		
			
	def startSyntaxHighlighing		(self,*args):
		try:
			lang = gtkcodebuffer.SyntaxLoader("arduino")
			if DEBUG_SYNTAX_HIGHLIGHT: print lang
			self.textAreaBuffer = gtkcodebuffer.CodeBuffer(lang=lang)
			self.textArea.set_buffer( self.textAreaBuffer )
			if DEBUG_SYNTAX_HIGHLIGHT: print self.textAreaBuffer
		except:
			print "Error: Syntax higlighting resources not found."
		return True
		
	
	
	def updateArduinoBoard			(self,*args):
		self.arduinoCpu = self.arduinoCpuDropBox.get_active_text()
		print "Arduino Board type updated to "+self.arduinoCpu+"."
		return True
		
	def updateArduinoLocation		(self,*args):
		self.arduinoLocation = self.arduinoLocationDropBox.get_active_text()
		print "Arduino location updated to "+self.arduinoLocation+"."
		return True
		
	def sendSerialData				(self,*args):
		if (self.connectedToArduino == True):
			self.sendSerialEntryBuffer = self.sendSerialEntry.get_text()
			self.arduinoSerial.write(self.sendSerialEntryBuffer)
			
			self.text = self.sendSerialEntryBuffer   # self.text = text printed in Serial Monitor
			#-- From Update Serial Monitor
			self.serialTextAreaBuffer.set_text(self.serialTextAreaBuffer.get_text(self.serialTextAreaBuffer.get_start_iter(),self.serialTextAreaBuffer.get_end_iter())+self.text+"\n") ### WARNING! Wrapped

			print "Sent \""+self.sendSerialEntryBuffer+"\" to the Arduino."
		else:
			print "Error sending data: "+ self.connectionError
		return True
		
		
	def preferencesWindow			(self,*args):
		if DEBUG_WINDOW: print "Init"+ str(self.preferencesWindow)
		self.preferencesWindow.show_all()
		if DEBUG_WINDOW: print "1 " + str(self.preferencesWindow)
		return True
		
		
	def updateBaudrate				(self,*args):
		if (self.connectedToArduino == True):	
			self.newBaudrate = int(self.baudrateEntry.get_text())
			self.arduinoSerial.setBaudrate(self.newBaudrate)
			print "Baud rate successfully changed to" ,str(self.newBaudrate)+"."
		else:
			print "Error applying Baud Rate: "+ self.connectionError
		return True
		
	def changeSerialConnectionState	(self,*args):
		#--- Check if disconnected, if YES then Connect, or Visa Versa
		if (self.connectedToArduino == False):
			try:
				# --- Connect, And Change Label to "Disconnect" ---
				self.serialBaudRate =9600
				self.serialConnection = self.arduinoLocation
				self.arduinoSerial = serial.Serial(port=self.serialConnection,baudrate=self.serialBaudRate,timeout = 0)
				print "Connected to Arduino at "+self.arduinoLocation+"."
				self.connectedToArduino = True
				self.connectButton.set_label("gtk-disconnect")
			except:
				print "Error: The connection to your Arduino could not be established."
				print "Please ensure it is correctly plugged in, and selected in the Preferences."
			return True
		else:

			self.connectButton.set_label("gtk-connect")
			self.arduinoSerial.close()
			self.connectedToArduino = False
			print "Disconnected from Arduino at"+self.arduinoLocation+"."
			
		return True
	
	def gtkMain						(self,*args):
		gobject.timeout_add (199,self.updateSerialMonitor)    #updateSerialMonitor
		gtk.main()
		return True
	
	def openWindowOpen				(self,*args):
		self.openWindowFilename = str(self.openWindowFileChooser.get_filename() )
		print "Opening file ",str(self.openWindowFilename)+"."
		self.openFile = open(self.openWindowFilename,"r")
		
		# -- Opening a file results in a long Filename: "/mnt/sda4/.../sketches/<name>/<name>.pde"
		# -- self.Filename should only be the <name>.
		a,b,c = self.openWindowFilename.rpartition("/")
		self.Filename,a,b =  c.rpartition(".")
		if DEBUG_FILE: print self.Filename

		self.openWindowClose()
		self.textAreaBuffer.set_text(self.openFile.read() )
		self.updateTextAreaMarkers()
		return True
		
	def updateTextAreaMarkers		(self,*args):
		startIter = self.textAreaBuffer.get_start_iter()
		endIter = self.textAreaBuffer.get_end_iter()
		self.textToSave = self.textAreaBuffer.get_text(startIter,endIter)
		if DEBUG_FILE: print self.textAreaBuffer.get_line_count()
		return True
		
	def newFile						(self,*args):
		self.saveFileBackup()
		print "Creating a new Sketch..."
		self.newFileWindow.show_all()
		return True
		
	def newFileProduction			(self,*args):
		print "Setting up new Sketch..."
		self.newFileNameEntryBuffer = self.newFileNameEntry.get_text()
		self.newFileNameEntry.set_text("")
		self.Filename = self.newFileNameEntryBuffer
		self.newFileWindow.hide()
		
		# Make new Sketch directory, Paste Makefile in there. Insert TARGET = self.Filename on line # 40
		os.mkdir("./sketches/"+str(self.Filename) )
		shutil.copy("./lib/Makefile", ("./sketches/"+str(self.Filename)+"/Makefile" ) )
		
		self.Makefile = open("./sketches/"+str(self.Filename)+"/Makefile")
		
		#Sets a default arduino sketch to the Text area.
		self.defaultSketch = open("./lib/default.pde","r")
		self.textAreaBuffer.set_text( self.defaultSketch.read() )
		self.defaultSketch.close()
		
		self.saveFile()
		print "Done setting up new sketch ("+str(self.Filename)+")"
		return True
		
			
	def newFileCancel				(self,*args):
		print "Cancelled making a new Sketch"
		self.newFileWindow.hide()
		return True
		
	def updateSerialMonitor			(self,*args):
		if (self.connectedToArduino == True):	
			if DEBUG_SERIAL: print "Starting update of Serial Monitor"
			
			#Update ONLY if there is new data available...
			if self.arduinoSerial.inWaiting() != 0:
				try:
					self.text = str(self.arduinoSerial.read(self.arduinoSerial.inWaiting() ) )

					self.serialTextAreaBuffer.set_text(self.serialTextAreaBuffer.get_text( \
					self.serialTextAreaBuffer.get_start_iter(),self.serialTextAreaBuffer.get_end_iter() ) + self.text) ### WARNING! Wrapped
						
					self.serialTextAreaScrollerValue.value = float(100000)
					self.serialTextAreaScroller.set_focus_vadjustment(self.serialTextAreaScrollerValue)
					
					self.serialTextAreaScrollerHValue.value = float(100000)
					self.serialTextAreaScroller.set_focus_hadjustment(self.serialTextAreaScrollerHValue)
				except:
					
					print "Error: Serial Monitor just recieved a crazy character.\nThis probably means you have the wrong Baud Rate selected."
					self.serialTextAreaBuffer.set_text(self.serialTextAreaBuffer.get_start_iter(),self.serialTextAreaBuffer.get_start_iter()+'Warning:\nYou probably\nhave a "bad"\nBaud Rate selected')
				if DEBUG_SERIAL: print "Serial Monitor Updated"
			else:
				if DEBUG_SERIAL: print "No New Serial Data available.."
				pass
		else:
			if DEBUG_SERIAL: print "Serial Monitor not available as there is no active connection to the Arduino"
		return True
		
	def saveFile					(self,*args):
		
		self.updateTextAreaMarkers()    # writes to self.textToSave: entire contents of editing area
		try:
			if DEBUG_FILE: print "Checking if Sketch save dir exists..."
			check = open("./sketches/"+str(self.Filename)+"/"+str(self.Filename)+".pde","r") 
			if DEBUG_FILE: print "Sketch save dir exists. Taking no action."
		except:
			if DEBUG_FILE: print "Creating Sketch Dir."
			try:
				os.mkdir("./sketches/"+str(self.Filename))
			except:
				if type(self.Filename) != type("str"): #Checks for self.Filename = 0 (ie not filename)
					self.Filename = "unknownProject"

				ouputFile = open("./sketches/"+str(self.Filename)+"/"+str(self.Filename)+".pde","w")
				ouputFile.write(self.textToSave)
				print "Saved", self.Filename, "to disk."
				return True				
				
		ouputFile = open("./sketches/"+str(self.Filename)+"/"+str(self.Filename)+".pde","w")
		ouputFile.write(self.textToSave)
		print "Saved", self.Filename, "to disk."
		return True
		
		
	def saveFileBackup				(self,*args):
		self.updateTextAreaMarkers()
		
		self.saveFilename = "quit" #-- LEAVE ALONE!! It makes a quit.pde upon exiting the program.
		
		ouputFile = open("./sketches/"+str(self.saveFilename)+".pde","w")
		ouputFile.write(self.Filename)
		print "Saved", self.saveFilename, "to disk."
		return True
		
		
	def openWindow					(self,*args):
		self.openWindow.show_all()

		return True
		
	def openWindowClose				(self,*args):
		self.openWindow.hide()
		return True

	def about 						(self,*args):

		#self.aboutWindowChild = self.aboutWindow.get_child()
		#self.aboutCloseButton = self.xml.get_widget("aboutClose")
		#self.aboutCloseButton.connect("clicked",self.aboutQuit)
		
		#self.widget = self.aboutWindowChild
		self.aboutWindow.show_all()
		self.aboutWindow.run()
		self.aboutWindow.hide()
		return False

	def quitAbout					(self,*args):
		self.aboutWindow.hide()
		#gtk.main_quit()
		return True
		
	def quitNewFileWindow			(self,*args):
		self.newFileWindow.hide()
		#gtk.main_quit()
		return True
		
	def quitOpenWindow				(self,*args):
		self.openWindow.hide()
		return True
		
	def quitPreferencesWindow		(self,*args):
		self.preferencesWindow.hide()
		if DEBUG_WINDOW: print "After Destroy ",self.preferencesWindow
		return True
		
	def quitCompileWindow			(self,*args):
		self.compileWindow.hide()
		if DEBUG_WINDOW: print "After Destroy ",self.compileWindow
		return True
		
	def quitFeedbackWindow			(self,*args):
		self.feedbackWindow.hide()
		self.feedbackWindow.destroy()
		if DEBUG_WINDOW: print "After QuitFeedback:",self.feedbackWindow
	def quit						(self,*args):
		#self.arduinoSerial.close() 		#Clean up the connection
		try:
			self.saveFile()		 	#Save a backup of the file in case a "accidental" quit was pressed
		except:
			print "Warning: Could not save file..."
		try:
			self.saveFileBackup()		 	#Save a backup of the file in case a "accidental" quit was pressed
		except:
			print "Warning: Could not save \"on quit\" file..."
		gtk.main_quit() 
		return True
				
if __name__ == '__main__':
	main()
	
