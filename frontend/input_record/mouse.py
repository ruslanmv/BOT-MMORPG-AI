# -*- coding: utf-8 -*-


from AutoHotPy import AutoHotPy

initial_position = (0,0)

def exitAutoHotKey(autohotpy,event):
    """
    exit the program when you press ESC
    """
    autohotpy.stop()

def startStopMacro(autohotpy,event):
    global initial_position
    if not autohotpy.isRecording():
        initial_position  = autohotpy.getMousePosition()   
    autohotpy.mouseMacroStartStop()  #record mouse only


def fireMacro(autohotpy,event):
    global initial_position
    autohotpy.moveMouseToPosition(initial_position[0],initial_position[1])
    autohotpy.fireLastRecordedMacro()    

def clearMacro(autohotpy,event):
    autohotpy.clearLastRecordedMacro()
    
if __name__=="__main__":
    print("---- Hello to Mouse---- ")
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
