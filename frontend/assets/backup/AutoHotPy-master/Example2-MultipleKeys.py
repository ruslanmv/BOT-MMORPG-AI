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
from AutoHotPy import AutoHotPy

def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press Ctrl + Alt + F10
    """
    if (autohotpy.LEFT_CTRL.isPressed() & autohotpy.LEFT_ALT.isPressed()):  #check if ctrl and alt are also pressed
        autohotpy.stop()
    else:#if ctrl +al is not pressed, then it's a normal  F10 keypress. send it as is
        autohotpy.sendToDefaultKeyboard(event)
        
def openTaskManager(autohotpy,event):
    """
    This function is called when you press DELETE key
    """
    if (autohotpy.LEFT_CTRL.isPressed() & autohotpy.LEFT_ALT.isPressed()):  #check if ctrl and alt are also pressed
        autohotpy.LEFT_ALT.up()        #release alt
        autohotpy.sleep() #don't forget to sleep when you manually send a "down" state
        autohotpy.LEFT_SHIFT.down()
        autohotpy.sleep() 
        autohotpy.ESC.down()
        autohotpy.sleep() 
        autohotpy.LEFT_SHIFT.up()
        autohotpy.ESC.up()
    else: #if ctrl +al is not pressed, then it's a normal  Del keypress. send it as is
        autohotpy.sendToDefaultKeyboard(event)

if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.F10,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    # In win7 the task manager is launched when you press Ctrl + Shift + ESC
    # I don't like that. Lets call the task manager when you press Ctrl + Alt + Supr
    auto.registerForKeyDown(auto.DELETE,openTaskManager)   
    auto.start()
