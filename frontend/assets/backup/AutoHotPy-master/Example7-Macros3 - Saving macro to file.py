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
from InterceptionWrapper import *

mouse_initial_position = (0,0)
save_file = "./recorded_macro.py"

def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    autohotpy.stop()

def startStopMacro(autohotpy,event):
    global mouse_initial_position
    if not autohotpy.isRecording():
        mouse_initial_position  = autohotpy.getMousePosition()   
    autohotpy.macroStartStop()


def fireMacro(autohotpy,event):
    global mouse_initial_position
    autohotpy.moveMouseToPosition(mouse_initial_position[0],mouse_initial_position[1])
    autohotpy.fireLastRecordedMacro()    

def clearMacro(autohotpy,event):
    autohotpy.clearLastRecordedMacro()
    
def saveMacro(autohotpy,event):
    global mouse_initial_position
    autohotpy.saveLastRecordedMacro(save_file,mouse_initial_position)

    
if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    auto.registerForKeyDown(auto.F1,startStopMacro)
    auto.registerForKeyDown(auto.F2,fireMacro)
    auto.registerForKeyDown(auto.F3,saveMacro)
    auto.registerForKeyDown(auto.F10,clearMacro)
    
    auto.start()
