# -*- coding: utf-8 -*-


from AutoHotPy import AutoHotPy
from InterceptionWrapper import *

mouse_initial_position = (0,0)
save_file = "./recorded_macro.py"

def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    print("ESC - exitAutoHotKey")
    autohotpy.stop()



def startStopMacro(autohotpy,event):

    print("F1 - startStopMacro")
    global mouse_initial_position
    if not autohotpy.isRecording():
        mouse_initial_position  = autohotpy.getMousePosition()  
    autohotpy.macroStartStop()

    
 


def fireMacro(autohotpy,event):
    print("F2 - fireMacro")

    global mouse_initial_position
    autohotpy.moveMouseToPosition(mouse_initial_position[0],mouse_initial_position[1])
    autohotpy.fireLastRecordedMacro()
   

def clearMacro(autohotpy,event):
    print("F4 - clearMacro")
    autohotpy.clearLastRecordedMacro()
    
def saveMacro(autohotpy,event):
    print("F3 - saveMacro")
    global mouse_initial_position
    autohotpy.saveLastRecordedMacro(save_file,mouse_initial_position)

    
if __name__=="__main__":

    print("---- Hello to Macro--Mouse+ Keyboard-- ")
    print("Press F1 to start/stop macro")
    print("Press F2 to start macro")
    print("Press F3 to save macro")
    print("Press F4 to clear macro")
    print("Press ESC to exit")
    print("----------")
    print("")
    print("waiting key")
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    auto.registerForKeyDown(auto.F1,startStopMacro)
    auto.registerForKeyDown(auto.F2,fireMacro)
    auto.registerForKeyDown(auto.F3,saveMacro)
    auto.registerForKeyDown(auto.F4,clearMacro)
    
    auto.start()
