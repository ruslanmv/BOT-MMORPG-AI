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

repeat_always = False

def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    autohotpy.stop()
    
def alwaysLoopMacro(autohotpy,event):
    global repeat_always
    autohotpy.A.press()
    autohotpy.B.press()
    autohotpy.C.press()
    
    #now that we are finished, let's check if we should loop
    # If repeat_always= true, then we tell autohotpy to run loopMacro again
    if repeat_always:
        autohotpy.run(alwaysLoopMacro, event)
        
def enableDisableLoopMacro(autohotpy, event):
    global repeat_always
    
    if repeat_always:
        repeat_always = False
    else:
        # let's enable it, and then we call it for the first time, so it starts running as soon as possible
        repeat_always = True
        alwaysLoopMacro(autohotpy, event)

    
if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    auto.registerForKeyDown(auto.F1,enableDisableLoopMacro)
    
    auto.start()
