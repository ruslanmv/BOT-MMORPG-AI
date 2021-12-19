# -*- coding: utf-8 -*-
"""
@author: Emilio Moretti
Copyright 2013 Emilio Moretti <emilio.morettiATgmailDOTcom>
This program is distributed under the terms of the GNU Lesser General Public License.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

#WARNING: handling mouse events is harder than keyboard events.
# You have to do most things manually
from AutoHotPy import AutoHotPy
from InterceptionWrapper import InterceptionMouseState,InterceptionMouseStroke


def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    autohotpy.stop()
        
def rightButton(autohotpy,event):
    """
    This function simulates a right click
    """
    stroke = InterceptionMouseStroke() # I highly suggest you to open InterceptionWrapper to read which attributes this class has
    
    #To simulate a mouse click we manually have to press down, and release the buttons we want.
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
    autohotpy.sendToDefaultMouse(stroke)
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
    autohotpy.sendToDefaultMouse(stroke)
    
def leftButton(autohotpy,event):
    """
    This function simulates a left click
    """
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
    autohotpy.sendToDefaultMouse(stroke)
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
    autohotpy.sendToDefaultMouse(stroke)
    

if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    # lets switch right and left mouse buttons!
    auto.registerForMouseButton(InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN,rightButton)
    auto.registerForMouseButton(InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN,leftButton)
    auto.start()
