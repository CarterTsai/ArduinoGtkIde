
#		ArduinoGtkIde. A development Enviroment for AVR based microchips.
#		Copyright (C) 2009  Harry van Haaren <harryhaaren@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.



import subprocess

def compileSketch():
	try:
		stdout_text = ""
		proc = subprocess.Popen( ("make"),
							stdin = subprocess.PIPE,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout_text , stderr_text = proc.communicate()

		return stdout_text,stderr_text
	except:
		pass
	#	return False
	return True

def uploadSketch():
	try:
		proc = subprocess.Popen( ("make", "upload"),
									stdin = subprocess.PIPE,
									stdout = subprocess.PIPE,
									stderr = subprocess.PIPE)
		stdout_text , stderr_text = proc.communicate()

		return stdout_text,stderr_text
	except:
		return False

