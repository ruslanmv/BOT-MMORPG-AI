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

#The example starts here
from AutoHotPy import AutoHotPy  # we need to tell python that we are going to use the library


# The following function is called when you press ESC.
#autohotpy is the instance that controlls the library, you should do everything through it.
def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    autohotpy.stop() #makes the program finish successfully. Thisis the right way to stop it
    
def superCombo(autohotpy,event):
    """
    This function is called when you press "A" key.
    It executes the combo: A -> S -> move left -> move up -> A -> S
    """
    autohotpy.A.press()  # press() method simulates a key press by sending first the key down, and later the key up events
    autohotpy.S.press()
    autohotpy.LEFT_ARROW.press()
    autohotpy.UP_ARROW.press()
    autohotpy.A.press()
    autohotpy.S.press()


# THIS IS WERE THE PROGRAM STARTS EXECUTING!!!!!!!!
if __name__=="__main__":
    auto = AutoHotPy()  #Initialize the library
    auto.registerExit(auto.ESC, exitAutoHotKey)   # Registering an end key is mandatory to be able to stop the program gracefully
    auto.registerForKeyDown(auto.A,superCombo) # This method lets you say: "when I press A in the keyboard, then execute "superCombo"
    auto.start()                                #Now that everything is registered we should start runnin the program
