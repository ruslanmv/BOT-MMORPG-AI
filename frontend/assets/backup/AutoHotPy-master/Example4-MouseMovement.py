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
from InterceptionWrapper import InterceptionMouseState,InterceptionMouseStroke,InterceptionMouseFlag


def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    autohotpy.stop()
        
def moveHandler(autohotpy,event):
    """
    This function inverts mouse axis!
    """
    if not(event.flags & InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE):
        event.x *= -1
        event.y *= -1
    autohotpy.sendToDefaultMouse(event)
    

if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    # lets switch right and left mouse buttons!
    auto.registerForMouseMovement(moveHandler)
    auto.start()
