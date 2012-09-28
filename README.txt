This README will show you some basics of installing the IDE.

See <http://sites.google.com/site/arduinogtkide/> for more info!

This file is to help you install the Arduino GTK IDE.
Its main concerns are:

  -Dependencies. Programs that need to be installed on your computer 
    to allow the IDE to function correctly.
  -Enviroment Variables. Where programs are located, and how let the
    IDE automatically find them.
   
I wrote this program specifically for Linux (as I developed the IDE on it).
Therefore to configure the software for windows\mac it may be nessisary to 
edit the makefile provided in the Libs directory.

Now for the actual dependencies & enviroment:

python2  <-- The programming language the IDE is written in.
      (Python2  is recommended. All other versions are untested.)

avr-gcc <-- Is an AVR compiler. It is needed to compile the code to AVR.
avrdude <-- Is an Upload tool for AVR based microchips.
make    <-- Used to configure the compile & upload process.

All 3 of these programs are EXPECTED to be 
located in /usr/bin. On a "Normal install" of any linux distro,
the programs will automatically be installed there.

As im using a Debian derative, Apt-get is the package manager.
So I can tell you that the following line will install your
dependencies for you IF you are using a Debian derative.

sudo apt-get install python2.5 gcc-avr avrdude gcc

If that command did not work, reload your sources or check with Google.

-Harry van Haaren, 07/06/2009

PS: Feedback to <harryhaaren@gmail.com> please!


#   ArduinoGtkIde. A development Enviroment for AVR based microchips.
#   Copyright (C) 2009  Harry van Haaren <harryhaaren@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.


