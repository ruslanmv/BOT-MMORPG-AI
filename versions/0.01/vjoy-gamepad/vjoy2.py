import ctypes
import struct, time
import numpy as np


#Vjoy adapted to MMORPG-AI

CONST_DLL_VJOY = "vJoyInterface.dll"

class vJoy(object):
    def __init__(self, reference = 1):
        self.handle = None
        self.dll = ctypes.CDLL( CONST_DLL_VJOY )
        self.reference = reference
        self.acquired = False
        
    def open(self):
        if self.dll.AcquireVJD( self.reference ):
            self.acquired = True
            return True
        return False
    
    def close(self):
        if self.dll.RelinquishVJD( self.reference ):
            self.acquired = False
            return True
        return False
    
    def generateJoystickPosition(self, 
        wThrottle = 0, wRudder = 0, wAileron = 0,

        # left thb x        left thb y     left trigger
        wAxisX = 16393,   wAxisY = 16393,   wAxisZ = 16393,

        # right thb x       right thb y        right trigger
        wAxisXRot = 16393, wAxisYRot = 16393, wAxisZRot = 16393,

        # ???         ???        ???
        wSlider = 0, wDial = 0, wWheel = 0,
        # ???         ???        ???
        wAxisVX = 0, wAxisVY = 0, wAxisVZ = 0,
        # ???         ???                ???                   
        wAxisVBRX = 0, wAxisVBRY = 0, wAxisVBRZ = 0,
        # 1 = a
        # 2 = b  3 = a+b ??
        # 4 = x  5 = x+a ?? 6 = x+b
        # 8 = y
        lButtons = 0, bHats = 0, bHatsEx1 = 0, bHatsEx2 = 0, bHatsEx3 = 0):
        """
        typedef struct _JOYSTICK_POSITION
        {
            BYTE    bDevice; // Index of device. 1-based
            LONG    wThrottle;
            LONG    wRudder;
            LONG    wAileron;
            LONG    wAxisX;
            LONG    wAxisY;
            LONG    wAxisZ;
            LONG    wAxisXRot;
            LONG    wAxisYRot;
            LONG    wAxisZRot;
            LONG    wSlider;
            LONG    wDial;
            LONG    wWheel;
            LONG    wAxisVX;
            LONG    wAxisVY;
            LONG    wAxisVZ;
            LONG    wAxisVBRX;
            LONG    wAxisVBRY;
            LONG    wAxisVBRZ;
            LONG    lButtons;   // 32 buttons: 0x00000001 means button1 is pressed, 0x80000000 -> button32 is pressed
            DWORD   bHats;      // Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
                        DWORD   bHatsEx1;   // 16-bit of continuous HAT switch
                        DWORD   bHatsEx2;   // 16-bit of continuous HAT switch
                        DWORD   bHatsEx3;   // 16-bit of continuous HAT switch
        } JOYSTICK_POSITION, *PJOYSTICK_POSITION;
        """
        joyPosFormat = "BlllllllllllllllllllIIII"
        pos = struct.pack( joyPosFormat, self.reference, wThrottle, wRudder,
                                   wAileron, wAxisX, wAxisY, wAxisZ, wAxisXRot, wAxisYRot,
                                   wAxisZRot, wSlider, wDial, wWheel, wAxisVX, wAxisVY, wAxisVZ,
                                   wAxisVBRX, wAxisVBRY, wAxisVBRZ, lButtons, bHats, bHatsEx1, bHatsEx2, bHatsEx3 )
        return pos
    def update(self, joystickPosition):
        if self.dll.UpdateVJD( self.reference, joystickPosition ):
            return True
        return False
    
    #Not working, send buttons one by one
    def sendButtons( self, bState ):
        joyPosition = self.generateJoystickPosition( lButtons = bState )
        return self.update( joyPosition )
    
    def setButton( self, index, state ):
        if self.dll.SetBtn( state, self.reference, index ):
            return True
        return False
                

vj = vJoy()

# valueX, valueY between -1.0 and 1.0
# scale between 0 and 16000
def setJoy(valueX, valueY, scale):
    xPos = int(valueX*scale)
    yPos = int(valueY*scale)
    joystickPosition = vj.generateJoystickPosition(wAxisX = 16000+xPos, wAxisY = 16000+yPos)
    vj.update(joystickPosition)


def test():
    vj.open()
    print("vj opening", flush=True)
    btn = 1
    time.sleep(2)
    print("sending axes", flush=True)
    for i in range(0,1000,1):
        #vj.sendButtons( btn << i )
        xPos = int(10000.0*np.sin(2.0*np.pi*i/1000))
        yPos = int(10000.0*np.sin(2.0*np.pi*i/100))
        print(xPos, flush=True)
        joystickPosition = vj.generateJoystickPosition(wAxisX = 16000+xPos, wAxisY = 16000+yPos)
        vj.update(joystickPosition)
        time.sleep( 0.01 )
    joystickPosition = vj.generateJoystickPosition(wAxisX = 16000, wAxisY = 16000)
    vj.update(joystickPosition)
    vj.sendButtons(0)
    print("vj closing", flush=True)
    vj.close()
    
#Testing keys    
def test1():
    vj.open()
    btn = 1
    time.sleep(2)
    for i in range(0,10,1):
        vj.sendButtons( btn << i )
        time.sleep( 1 )
    vj.sendButtons(0)
    vj.close()    
    

def test2():
    time.sleep(3)
    print("vj opening", flush=True)
    vj.open()

    time.sleep(1)

    print("sending axes", flush=True)

    # valueX, valueY between -1.0 and 1.0
    # scale between 0 and 16000
    scale = 10000.0
    for i in range(0,1000,1):
        xPos = np.sin(2.0*np.pi*i/1000)
        yPos = np.sin(2.0*np.pi*i/100)
        setJoy(xPos, yPos, scale)
        time.sleep(0.01)

    print("vj closing", flush=True)
    
    reset = vj.generateJoystickPosition()
    setJoy(0, 0, scale)
    vj.close()
    
    
    
    



def test3():
    time.sleep(3)
    vj.open()
    print("vj opening", flush=True)
    time.sleep(2)
    print("sending axes", flush=True)
    joystickPosition = vj.generateJoystickPosition(wThrottle = 32000, wAxisX = 16000, wAxisY = 16000)
    vj.update(joystickPosition)
    time.sleep(5)
    joystickPosition = vj.generateJoystickPosition()
    vj.update(joystickPosition)
    #vj.sendButtons(0)
    print("vj closing", flush=True)
    vj.close()
  
    
# DOES change view. 
def test5():
    time.sleep(3)
    vj.open()
    print("vj opening", flush=True)
    time.sleep(2)
    print("sending axes", flush=True)
    joystickPosition = vj.generateJoystickPosition(wAxisX = 8000, wAxisY = 16000)
    vj.update(joystickPosition)
    time.sleep(5)
    joystickPosition = vj.generateJoystickPosition(wAxisX = 16000, wAxisY = 16000)
    vj.update(joystickPosition)
    #vj.sendButtons(0)
    print("vj closing", flush=True)
    vj.close()
    

    

def ultimate_release():
    vj.open()
    joystickPosition = vj.generateJoystickPosition()
    vj.update(joystickPosition)
    time.sleep(0.001)
    vj.close()
    

    
    
######## Gamepad definitions ###############

#LT and RT  (corresponds to Z in Joystic Test)
      
def gamepad_lt():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisZ = 32786)
    vj.update(joystickPosition)
    vj.close()
    
    
def gamepad_rt():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisZ = 0)
    vj.update(joystickPosition)
    vj.close()    
    
# Left Thumbstick

def game_lx_left():
    vj.open()
    # valueX, valueY between -1.0 and 1.0
    # scale between 0 and 16000
    scale = 16393.0
    #reset = vj.generateJoystickPosition()
    setJoy(-1, 0, scale)
    vj.close()    
    
def game_lx_right():
    vj.open()
    # valueX, valueY between -1.0 and 1.0
    # scale between 0 and 16000
    scale = 16393.0
    #reset = vj.generateJoystickPosition()
    setJoy(1, 0, scale)
    vj.close()    
    
def game_ly_up():
    vj.open()
    # valueX, valueY between -1.0 and 1.0
    # scale between 0 and 16000
    scale = 16393.0
    #reset = vj.generateJoystickPosition()
    setJoy(0, -1, scale)
    vj.close()    
    
    
def game_ly_down():
    vj.open()
    # valueX, valueY between -1.0 and 1.0
    # scale between 0 and 16000
    scale = 16393.0
    #reset = vj.generateJoystickPosition()
    setJoy(0, 1, scale)
    vj.close()        
    
    
    
#   Right Thumbstick  
    
    
def look_rx_left():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisXRot = 0)
    vj.update(joystickPosition)
    vj.close()
    
    
def look_rx_right():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisXRot = 32786)
    vj.update(joystickPosition)
    vj.close()
    
    
def look_ry_up():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisYRot = 0)
    vj.update(joystickPosition)
    vj.close()
    

def look_ry_down():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisYRot = 32786)
    vj.update(joystickPosition)
    vj.close()    
        
    


# RZ    

def throttle_max():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisZRot = 32786)
    vj.update(joystickPosition)
    vj.close()
    
    
    
    
def throttle_min():
    vj.open()
    joystickPosition = vj.generateJoystickPosition(wAxisZRot = 0)
    vj.update(joystickPosition)
    vj.close()
        
    

#Button 1 = A    
def button_A():
    vj.open()
    btn = 1
    time.sleep(2)
    vj.sendButtons(btn)
    time.sleep(1)
    vj.sendButtons(0)
    vj.close() 
    
# Buttons A, B, X, Y,
    
#Button 1 = A    
def button_A():
    vj.open()
    btn = 1
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()    
    

#Button 2 = B    
def button_B():
    vj.open()
    btn = 2
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
    
#Button 3 = AB   
def button_AB():
    vj.open()
    btn = 3
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()     

#Button 4 = X   
def button_X():
    vj.open()
    btn = 4
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()  
    
#Button 5 = AX   
def button_AX():
    vj.open()
    btn = 5
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()       

#Button 6 = BX   
def button_BX():
    vj.open()
    btn = 6
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
    
#Button 7 = ABX  
def button_ABX():
    vj.open()
    btn = 7
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()     
    
#Button 8 = Y  
def button_Y():
    vj.open()
    btn = 8
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()     
    
#Button 9 = AY  
def button_AY():
    vj.open()
    btn = 9
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
    
    
#Button 10 = BY  
def button_BY():
    vj.open()
    btn = 10
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()     
    
    
    
#Button 11 = ABY  
def button_ABY():
    vj.open()
    btn = 11
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()    
    
    
#Button 12 = XY  
def button_XY():
    vj.open()
    btn = 12
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()  
    
#Button 13 = AXY  
def button_AXY():
    vj.open()
    btn = 13
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close()     
    
#Button 14 = BXY  
def button_BXY():
    vj.open()
    btn = 14
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
    
#Button 15 = ABXY  
def button_ABXY():
    vj.open()
    btn = 15
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
    

if __name__ == '__main__':

    ultimate_release()

    
        
        
