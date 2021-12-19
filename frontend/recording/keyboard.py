# -*- coding: utf-8 -*-

from AutoHotPy import AutoHotPy

def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    print("ESC - exitAutoHotKey")
    autohotpy.stop()

def startStopMacro(autohotpy,event): 
    print("F1 - startStopMacro")
    autohotpy.keyboardMacroStartStop()  #record keyboard only


def fireMacro(autohotpy,event):
    print("F2 - fireMacro")
    autohotpy.fireLastRecordedMacro()    

def clearMacro(autohotpy,event):
    print("F3 - clearMacro")
    autohotpy.clearLastRecordedMacro()
    
if __name__=="__main__":
    print("---- Hello to Keyboard---- ")
    print("Press F1 to start/stop macro")
    print("Press F2 to start macro")
    print("Press F3 to clear macro")
    print("Press ESC to exit")
    print("----------")
    print("")
    print("waiting key")    
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)   # Registering an end key is mandatory to be able tos top the program gracefully
    
    auto.registerForKeyDown(auto.F1,startStopMacro)
    auto.registerForKeyDown(auto.F2,fireMacro)
    auto.registerForKeyDown(auto.F3,clearMacro)
    
    auto.start()
