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
from InterceptionWrapper import *
import collections,time,threading,queue,copy,ctypes
from timers import Timers

class FunctionRunner(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            #grabs a function from queue
            task = self.queue.get()

            #run it
            task.run()
            
            #signals to queue job is done
            self.queue.task_done()
            
class Task(object):
    def __init__(self,autohotpy,f,param):
        self.function = f
        self.arg1 = autohotpy
        self.arg2 = param
    def run(self):
        self.function(self.arg1,self.arg2)
        
class Key(object):
    def __init__(self,auto,code,str_repr,*args):
        self.auto = auto
        self.code = code
        if (len(args) != 0):
            self.state = args[0]
        else:
            self.state = 0
        self.key_id = auto.get_key_id(self.code, self.state)
        self.string_representation = str_repr
        
    def get_id(self):
        return self.key_id
        
    def up(self):
        up = InterceptionKeyStroke()
        up.code = self.code
        up.state = InterceptionKeyState.INTERCEPTION_KEY_UP | self.state
        self.auto.sendToDefaultKeyboard(up)
        
    def press(self):
        event = InterceptionKeyStroke()
        event.code = self.code
        event.state = InterceptionKeyState.INTERCEPTION_KEY_DOWN | self.state
        self.auto.sendToDefaultKeyboard(event)
        self.auto.sleep()
        event.state = InterceptionKeyState.INTERCEPTION_KEY_UP | self.state
        self.auto.sendToDefaultKeyboard(event)
        
    def down(self):
        down = InterceptionKeyStroke()
        down.code = self.code
        down.state = InterceptionKeyState.INTERCEPTION_KEY_DOWN | self.state
        self.auto.sendToDefaultKeyboard(down)
    
    def isPressed(self):
        return bool(not(self.auto.getKeyboardState(self.code,self.state) & InterceptionKeyState.INTERCEPTION_KEY_UP))
    
    def __int__(self):
        return int(self.code)
        
    def __str__(self):
        return self.string_representation
        
class AutoHotPy(object):
    
    def __init__(self):
        self.exit_configured = False
        self.user32 = ctypes.windll.user32
        
        #configure user32
        self.user32.GetCursorPos.restype = ctypes.POINTER(Point)
        #default interval between keypress
        self.default_interval = 0.01
        #Threads queue
        self.kb_queue = queue.Queue()
        self.mouse_queue = queue.Queue()
        self.macro_queue = queue.Queue()
        
        # Handlers
        self.keyboard_handler_down = collections.defaultdict(self.__default_element)
        self.keyboard_handler_hold = collections.defaultdict(self.__default_element)
        self.keyboard_handler_up = collections.defaultdict(self.__default_element)
        self.mouse_handler_hold = collections.defaultdict(self.__default_element)
        self.mouse_handler = collections.defaultdict(self.__default_element)
        self.mouse_move_handler = None
        self.keyboard_state = collections.defaultdict(self.__default_kb_element)
        self.mouse_state = collections.defaultdict(self.__default_element)
        self.loopingCall = None
        
        #are we recording a macro? Not yet...
        self.recording_macro = False
        self.enable_mouse_macro = True
        self.enable_kb_macro = True
        self.last_macro = []
        self.keys = collections.defaultdict(self.__default_kb_element)
        
        # Default key scancodes (you can send your own anyway)
        # WARNING! Most of these depend on the keyboard implementation!!!!
        self.ESC=Key(self,0x1,"ESC")
        self.N1=Key(self,0x2,"N1")
        self.N2=Key(self,0x3,"N2")
        self.N3=Key(self,0x4,"N3")
        self.N4=Key(self,0x5,"N4")
        self.N5=Key(self,0x6,"N5")
        self.N6=Key(self,0x7,"N6")
        self.N7=Key(self,0x8,"N7")
        self.N8=Key(self,0x9,"N8")
        self.N9=Key(self,0x0A,"N9")
        self.N0=Key(self,0x0B,"N0")
        self.DASH=Key(self,0x0C,"DASH")
        #self.Err:520=Key(self,0x0D)
        self.BACKSPACE=Key(self,0x0E,"BACKSPACE")
        self.TAB=Key(self,0x0F,"TAB")
        self.Q=Key(self,0x10,"Q")
        self.W=Key(self,0x11,"W")
        self.E=Key(self,0x12,"E")
        self.R=Key(self,0x13,"R")
        self.T=Key(self,0x14,"T")
        self.Y=Key(self,0x15,"Y")
        self.U=Key(self,0x16,"U")
        self.I=Key(self,0x17,"I")
        self.O=Key(self,0x18,"O")
        self.P=Key(self,0x19,"P")
        self.BRACKET_LEFT=Key(self,0x1A,"BRACKET_LEFT")
        self.BRACKET_RIGHT=Key(self,0x1B,"BRACKET_RIGHT")
        self.ENTER=Key(self,0x1C,"ENTER")
        self.LEFT_CTRL=Key(self,0x1D,"LEFT_CTRL")
        self.RIGHT_CTRL=Key(self,0x1D,"RIGHT_CTRL", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.A=Key(self,0x1E,"A")
        self.S=Key(self,0x1F,"S")
        self.D=Key(self,0x20,"D")
        self.F=Key(self,0x21,"F")
        self.G=Key(self,0x22,"G")
        self.H=Key(self,0x23,"H")
        self.J=Key(self,0x24,"J")
        self.K=Key(self,0x25,"K")
        self.L=Key(self,0x26,"L")
        self.SEMICOLON=Key(self,0x27,"SEMICOLON")
        self.APOSTROPHE=Key(self,0x28,"APOSTROPHE")
        self.GRAVE_ACCENT=Key(self,0x29,"GRAVE_ACCENT")
        self.LEFT_SHIFT=Key(self,0x2A,"LEFT_SHIFT")
        self.BACKSLASH=Key(self,0x2B,"BACKSLASH")
        self.Z=Key(self,0x2C,"Z")
        self.X=Key(self,0x2D,"X")
        self.C=Key(self,0x2E,"C")
        self.V=Key(self,0x2F,"V")
        self.B=Key(self,0x30,"B")
        self.N=Key(self,0x31,"N")
        self.M=Key(self,0x32,"M")
        self.COMMA=Key(self,0x33,"COMMA")
        self.DOT=Key(self,0x34,"DOT")
        self.SLASH=Key(self,0x35,"SLASH")
        self.RIGHT_SHIFT=Key(self,0x36,"RIGHT_SHIFT")
        self.PRINT_SCREEN=Key(self,0x37,"PRINT_SCREEN", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.LEFT_ALT=Key(self,0x38,"LEFT_ALT")
        self.RIGHT_ALT=Key(self,0x38,"RIGHT_ALT", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.SPACE=Key(self,0x39,"SPACE")
        self.CAPSLOCK=Key(self,0x3A,"CAPSLOCK")
        self.F1=Key(self,0x3B,"F1")
        self.F2=Key(self,0x3C,"F2")
        self.F3=Key(self,0x3D,"F3")
        self.F4=Key(self,0x3E,"F4")
        self.F5=Key(self,0x3F,"F5")
        self.F6=Key(self,0x40,"F6")
        self.F7=Key(self,0x41,"F7")
        self.F8=Key(self,0x42,"F8")
        self.F9=Key(self,0x43,"F9")
        self.F10=Key(self,0x44,"F10")
        self.NUMLOCK=Key(self,0x45,"NUMLOCK")
        self.SCROLLLOCK=Key(self,0x46,"SCROLLLOCK")
        self.HOME=Key(self,0x47,"HOME")
        self.UP_ARROW=Key(self,0x48,"UP_ARROW", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.PAGE_UP=Key(self,0x49,"PAGE_UP", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.DASH_NUM=Key(self,0x4A,"DASH_NUM")
        self.LEFT_ARROW=Key(self,0x4B,"LEFT_ARROW", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.NUMERIC_5 =Key(self,0x4C,"NUMERIC_5")
        self.RIGHT_ARROW=Key(self,0x4D,"RIGHT_ARROW", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.PLUS=Key(self,0x4E,"PLUS")
        self.END=Key(self,0x4F,"END", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.DOWN_ARROW=Key(self,0x50,"DOWN_ARROW", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.PAGE_DOWN=Key(self,0x51,"PAGE_DOWN", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.INSERT=Key(self,0x52,"INSERT", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.DELETE=Key(self,0x53,"DELETE", InterceptionKeyState.INTERCEPTION_KEY_E0)
        self.SHIFT_F1=Key(self,0x54,"SHIFT_F1")
        self.SHIFT_F2=Key(self,0x55,"SHIFT_F2")
        self.SHIFT_F3=Key(self,0x56,"SHIFT_F3")
        #self.SHIFT_F4=Key(self,0x57)
        #self.SHIFT_F5=Key(self,0x58)
        self.F11=Key(self,0x57,"F11") #these are not common. and might vary from one keyboard to another
        self.F12=Key(self,0x58,"F12")
        self.SHIFT_F6=Key(self,0x59,"SHIFT_F6")
        self.SHIFT_F7=Key(self,0x5A,"SHIFT_F7")
        self.SHIFT_F8=Key(self,0x5B,"SHIFT_F8")
        self.SYSTEM=Key(self,0x5B,"SYSTEM", InterceptionKeyState.INTERCEPTION_KEY_E0) #commonly known as windows key
        self.SHIFT_F9=Key(self,0x5C,"SHIFT_F9")
        self.SHIFT_F10=Key(self,0x5D,"SHIFT_F10")
        self.CTRL_F1=Key(self,0x5E,"CTRL_F1")
        self.CTRL_F2=Key(self,0x5F,"CTRL_F2")
        self.CTRL_F3=Key(self,0x60,"CTRL_F3")
        self.CTRL_F4=Key(self,0x61,"CTRL_F4")
        self.CTRL_F5=Key(self,0x62,"CTRL_F5")
        self.CTRL_F6=Key(self,0x63,"CTRL_F6")
        self.CTRL_F7=Key(self,0x64,"CTRL_F7")
        self.CTRL_F8=Key(self,0x65,"CTRL_F8")
        self.CTRL_F9=Key(self,0x66,"CTRL_F9")
        self.CTRL_F10=Key(self,0x67,"CTRL_F10")
        self.ALT_F1=Key(self,0x68,"ALT_F1")
        self.ALT_F2=Key(self,0x69,"ALT_F2")
        self.ALT_F3=Key(self,0x6A,"ALT_F3")
        self.ALT_F4=Key(self,0x6B,"ALT_F4")
        self.ALT_F5=Key(self,0x6C,"ALT_F5")
        self.ALT_F6=Key(self,0x6D,"ALT_F6")
        self.ALT_F7=Key(self,0x6E,"ALT_F7")
        self.ALT_F8=Key(self,0x6F,"ALT_F8")
        self.ALT_F9=Key(self,0x70,"ALT_F9")
        self.ALT_F10=Key(self,0x71,"ALT_F10")
        self.CTRL_PRINT_SCREEN=Key(self,0x72,"CTRL_PRINT_SCREEN")
        self.CTRL_LEFT_ARROW=Key(self,0x73,"CTRL_LEFT_ARROW")
        self.CTRL_RIGHT_ARROW=Key(self,0x74,"CTRL_RIGHT_ARROW")
        self.CTRL_END=Key(self,0x75,"CTRL_END")
        self.CTRL_PAGE_DOWN=Key(self,0x76,"CTRL_PAGE_DOWN")
        self.CTRL_HOME=Key(self,0x77,"CTRL_HOME")
        self.ALT_1=Key(self,0x78,"ALT_1")
        self.ALT_2=Key(self,0x79,"ALT_2")
        self.ALT_3=Key(self,0x7A,"ALT_3")
        self.ALT_4=Key(self,0x7B,"ALT_4")
        self.ALT_5=Key(self,0x7C,"ALT_5")
        self.ALT_6=Key(self,0x7D,"ALT_6")
        self.ALT_7=Key(self,0x7E,"ALT_7")
        self.ALT_8=Key(self,0x7F,"ALT_8")
        self.ALT_9=Key(self,0x80,"ALT_9")
        self.ALT_0=Key(self,0x81,"ALT_0")
        self.ALT_DASH=Key(self,0x82,"ALT_DASH")
        self.ALT_EQUALS=Key(self,0x82,"ALT_EQUALS")
        self.CTRL_PAGE_UP=Key(self,0x84,"CTRL_PAGE_UP")
        #self.F11=Key(self,0x85)
        #self.F12=Key(self,0x86)
        self.SHIFT_F11=Key(self,0x87,"SHIFT_F11")
        self.SHIFT_F12=Key(self,0x88,"SHIFT_F12")
        self.CTRL_F11=Key(self,0x89,"CTRL_F11")
        self.CTRL_F12=Key(self,0x8A,"CTRL_F12")
        self.ALT_F11=Key(self,0x8B,"ALT_F11")
        self.ALT_F12=Key(self,0x8C,"ALT_F12")
        self.CTRL_UP_ARROW=Key(self,0x8C,"CTRL_UP_ARROW")
        self.CTRL_DASH_NUM=Key(self,0x8E,"CTRL_DASH_NUM")
        self.CTRL_5_NUM=Key(self,0x8F,"CTRL_5_NUM")
        self.CTRL_PLUS_NUM=Key(self,0x90,"CTRL_PLUS_NUM")
        self.CTRL_DOWN_ARROW=Key(self,0x91,"CTRL_DOWN_ARROW")
        self.CTRL_INSERT=Key(self,0x92,"CTRL_INSERT")
        self.CTRL_DELETE=Key(self,0x93,"CTRL_DELETE")
        self.CTRL_TAB=Key(self,0x94,"CTRL_TAB")
        self.CTRL_SLASH_NUM=Key(self,0x95,"CTRL_SLASH_NUM")
        self.CTRL_ASTERISK_NUM=Key(self,0x96,"CTRL_ASTERISK_NUM")
        self.ALT_HOME=Key(self,0x97,"ALT_HOME")
        self.ALT_UP_ARROW=Key(self,0x98,"ALT_UP_ARROW")
        self.ALT_PAGE_UP=Key(self,0x99,"ALT_PAGE_UP")
        #self. =Key(self,0x9A)
        self.ALT_LEFT_ARROW=Key(self,0x9B,"ALT_LEFT_ARROW")
        #self. =Key(self,0x9C)
        self.ALT_RIGHT_ARROW=Key(self,0x9D,"ALT_RIGHT_ARROW")
        #self. =Key(self,0x9E)
        self.ALT_END=Key(self,0x9F,"ALT_END")
        self.ALT_DOWN_ARROW=Key(self,0xA0,"ALT_DOWN_ARROW")
        self.ALT_PAGE_DOWN=Key(self,0xA1,"ALT_PAGE_DOWN")
        self.ALT_INSERT=Key(self,0xA2,"ALT_INSERT")
        self.ALT_DELETE=Key(self,0xA3,"ALT_DELETE")
        self.ALT_SLASH_NUM=Key(self,0xA4,"ALT_SLASH_NUM")
        self.ALT_TAB=Key(self,0xA5,"ALT_TAB")
        self.ALT_ENTER_NUM=Key(self,0xA6,"ALT_ENTER_NUM")
        
        #lets create a dictionary with the keys
        #this is used when we save a macro to a file
        self.keys[self.ESC.get_id()]=self.ESC
        self.keys[self.N1.get_id()]=self.N1
        self.keys[self.N2.get_id()]=self.N2
        self.keys[self.N3.get_id()]=self.N3
        self.keys[self.N4.get_id()]=self.N4
        self.keys[self.N5.get_id()]=self.N5
        self.keys[self.N6.get_id()]=self.N6
        self.keys[self.N7.get_id()]=self.N7
        self.keys[self.N8.get_id()]=self.N8
        self.keys[self.N9.get_id()]=self.N9
        self.keys[self.N0.get_id()]=self.N0
        self.keys[self.DASH.get_id()]=self.DASH
        #self.keys[self.Err:520.get_id()]=self.
        self.keys[self.BACKSPACE.get_id()]=self.BACKSPACE
        self.keys[self.TAB.get_id()]=self.TAB
        self.keys[self.Q.get_id()]=self.Q
        self.keys[self.W.get_id()]=self.W
        self.keys[self.E.get_id()]=self.E
        self.keys[self.R.get_id()]=self.R
        self.keys[self.T.get_id()]=self.T
        self.keys[self.Y.get_id()]=self.Y
        self.keys[self.U.get_id()]=self.U
        self.keys[self.I.get_id()]=self.I
        self.keys[self.O.get_id()]=self.O
        self.keys[self.P.get_id()]=self.P
        self.keys[self.BRACKET_LEFT.get_id()]=self.BRACKET_LEFT
        self.keys[self.BRACKET_RIGHT.get_id()]=self.BRACKET_RIGHT
        self.keys[self.ENTER.get_id()]=self.ENTER
        self.keys[self.LEFT_CTRL.get_id()]=self.LEFT_CTRL
        self.keys[self.RIGHT_CTRL.get_id()]=self.RIGHT_CTRL
        self.keys[self.A.get_id()]=self.A
        self.keys[self.S.get_id()]=self.S
        self.keys[self.D.get_id()]=self.D
        self.keys[self.F.get_id()]=self.F
        self.keys[self.G.get_id()]=self.G
        self.keys[self.H.get_id()]=self.H
        self.keys[self.J.get_id()]=self.J
        self.keys[self.K.get_id()]=self.K
        self.keys[self.L.get_id()]=self.L
        self.keys[self.SEMICOLON.get_id()]=self.SEMICOLON
        self.keys[self.APOSTROPHE.get_id()]=self.APOSTROPHE
        self.keys[self.GRAVE_ACCENT.get_id()]=self.GRAVE_ACCENT
        self.keys[self.LEFT_SHIFT.get_id()]=self.LEFT_SHIFT
        self.keys[self.BACKSLASH.get_id()]=self.BACKSLASH
        self.keys[self.Z.get_id()]=self.Z
        self.keys[self.X.get_id()]=self.X
        self.keys[self.C.get_id()]=self.C
        self.keys[self.V.get_id()]=self.V
        self.keys[self.B.get_id()]=self.B
        self.keys[self.N.get_id()]=self.N
        self.keys[self.M.get_id()]=self.M
        self.keys[self.COMMA.get_id()]=self.COMMA
        self.keys[self.DOT.get_id()]=self.DOT
        self.keys[self.SLASH.get_id()]=self.SLASH
        self.keys[self.RIGHT_SHIFT.get_id()]=self.RIGHT_SHIFT
        self.keys[self.PRINT_SCREEN.get_id()]=self.PRINT_SCREEN
        self.keys[self.LEFT_ALT.get_id()]=self.LEFT_ALT
        self.keys[self.RIGHT_ALT.get_id()]=self.RIGHT_ALT
        self.keys[self.SPACE.get_id()]=self.SPACE
        self.keys[self.CAPSLOCK.get_id()]=self.CAPSLOCK
        self.keys[self.F1.get_id()]=self.F1
        self.keys[self.F2.get_id()]=self.F2
        self.keys[self.F3.get_id()]=self.F3
        self.keys[self.F4.get_id()]=self.F4
        self.keys[self.F5.get_id()]=self.F5
        self.keys[self.F6.get_id()]=self.F6
        self.keys[self.F7.get_id()]=self.F7
        self.keys[self.F8.get_id()]=self.F8
        self.keys[self.F9.get_id()]=self.F9
        self.keys[self.F10.get_id()]=self.F10
        self.keys[self.NUMLOCK.get_id()]=self.NUMLOCK
        self.keys[self.SCROLLLOCK.get_id()]=self.SCROLLLOCK
        self.keys[self.HOME.get_id()]=self.HOME
        self.keys[self.UP_ARROW.get_id()]=self.UP_ARROW
        self.keys[self.PAGE_UP.get_id()]=self.PAGE_UP
        self.keys[self.DASH_NUM.get_id()]=self.DASH_NUM
        self.keys[self.LEFT_ARROW.get_id()]=self.LEFT_ARROW
        self.keys[self.NUMERIC_5 .get_id()]=self.NUMERIC_5
        self.keys[self.RIGHT_ARROW.get_id()]=self.RIGHT_ARROW
        self.keys[self.PLUS.get_id()]=self.PLUS
        self.keys[self.END.get_id()]=self.END
        self.keys[self.DOWN_ARROW.get_id()]=self.DOWN_ARROW
        self.keys[self.PAGE_DOWN.get_id()]=self.PAGE_DOWN
        self.keys[self.INSERT.get_id()]=self.INSERT
        self.keys[self.DELETE.get_id()]=self.DELETE
        self.keys[self.SHIFT_F1.get_id()]=self.SHIFT_F1
        self.keys[self.SHIFT_F2.get_id()]=self.SHIFT_F2
        self.keys[self.SHIFT_F3.get_id()]=self.SHIFT_F3
        #self.keys[self.SHIFT_F4.get_id()]=self.SHIFT_F4
        #self.keys[self.SHIFT_F5.get_id()]=self.SHIFT_F5
        self.keys[self.F11.get_id()]=self.F11 #these are not common. and might vary from one keyboard to another
        self.keys[self.F12.get_id()]=self.F12
        self.keys[self.SHIFT_F6.get_id()]=self.SHIFT_F6
        self.keys[self.SHIFT_F7.get_id()]=self.SHIFT_F7
        self.keys[self.SHIFT_F8.get_id()]=self.SHIFT_F8
        self.keys[self.SYSTEM.get_id()]=self.SYSTEM #commonly known as windows key
        self.keys[self.SHIFT_F9.get_id()]=self.SHIFT_F9
        self.keys[self.SHIFT_F10.get_id()]=self.SHIFT_F10
        self.keys[self.CTRL_F1.get_id()]=self.CTRL_F1
        self.keys[self.CTRL_F2.get_id()]=self.CTRL_F2
        self.keys[self.CTRL_F3.get_id()]=self.CTRL_F3
        self.keys[self.CTRL_F4.get_id()]=self.CTRL_F4
        self.keys[self.CTRL_F5.get_id()]=self.CTRL_F5
        self.keys[self.CTRL_F6.get_id()]=self.CTRL_F6
        self.keys[self.CTRL_F7.get_id()]=self.CTRL_F7
        self.keys[self.CTRL_F8.get_id()]=self.CTRL_F8
        self.keys[self.CTRL_F9.get_id()]=self.CTRL_F9
        self.keys[self.CTRL_F10.get_id()]=self.CTRL_F10
        self.keys[self.ALT_F1.get_id()]=self.ALT_F1
        self.keys[self.ALT_F2.get_id()]=self.ALT_F2
        self.keys[self.ALT_F3.get_id()]=self.ALT_F3
        self.keys[self.ALT_F4.get_id()]=self.ALT_F4
        self.keys[self.ALT_F5.get_id()]=self.ALT_F5
        self.keys[self.ALT_F6.get_id()]=self.ALT_F6
        self.keys[self.ALT_F7.get_id()]=self.ALT_F7
        self.keys[self.ALT_F8.get_id()]=self.ALT_F8
        self.keys[self.ALT_F9.get_id()]=self.ALT_F9
        self.keys[self.ALT_F10.get_id()]=self.ALT_F10
        self.keys[self.CTRL_PRINT_SCREEN.get_id()]=self.CTRL_PRINT_SCREEN
        self.keys[self.CTRL_LEFT_ARROW.get_id()]=self.CTRL_LEFT_ARROW
        self.keys[self.CTRL_RIGHT_ARROW.get_id()]=self.CTRL_RIGHT_ARROW
        self.keys[self.CTRL_END.get_id()]=self.CTRL_END
        self.keys[self.CTRL_PAGE_DOWN.get_id()]=self.CTRL_PAGE_DOWN
        self.keys[self.CTRL_HOME.get_id()]=self.CTRL_HOME
        self.keys[self.ALT_1.get_id()]=self.ALT_1
        self.keys[self.ALT_2.get_id()]=self.ALT_2
        self.keys[self.ALT_3.get_id()]=self.ALT_3
        self.keys[self.ALT_4.get_id()]=self.ALT_4
        self.keys[self.ALT_5.get_id()]=self.ALT_5
        self.keys[self.ALT_6.get_id()]=self.ALT_6
        self.keys[self.ALT_7.get_id()]=self.ALT_7
        self.keys[self.ALT_8.get_id()]=self.ALT_8
        self.keys[self.ALT_9.get_id()]=self.ALT_9
        self.keys[self.ALT_0.get_id()]=self.ALT_0
        self.keys[self.ALT_DASH.get_id()]=self.ALT_DASH
        self.keys[self.ALT_EQUALS.get_id()]=self.ALT_EQUALS
        self.keys[self.CTRL_PAGE_UP.get_id()]=self.CTRL_PAGE_UP
        #self.keys[self.F11.get_id()]=self.
        #self.keys[self.F12.get_id()]=self.
        self.keys[self.SHIFT_F11.get_id()]=self.SHIFT_F11
        self.keys[self.SHIFT_F12.get_id()]=self.SHIFT_F12
        self.keys[self.CTRL_F11.get_id()]=self.CTRL_F11
        self.keys[self.CTRL_F12.get_id()]=self.CTRL_F12
        self.keys[self.ALT_F11.get_id()]=self.ALT_F11
        self.keys[self.ALT_F12.get_id()]=self.ALT_F12
        self.keys[self.CTRL_UP_ARROW.get_id()]=self.CTRL_UP_ARROW
        self.keys[self.CTRL_DASH_NUM.get_id()]=self.CTRL_DASH_NUM
        self.keys[self.CTRL_5_NUM.get_id()]=self.CTRL_5_NUM
        self.keys[self.CTRL_PLUS_NUM.get_id()]=self.CTRL_PLUS_NUM
        self.keys[self.CTRL_DOWN_ARROW.get_id()]=self.CTRL_DOWN_ARROW
        self.keys[self.CTRL_INSERT.get_id()]=self.CTRL_INSERT
        self.keys[self.CTRL_DELETE.get_id()]=self.CTRL_DELETE
        self.keys[self.CTRL_TAB.get_id()]=self.CTRL_TAB
        self.keys[self.CTRL_SLASH_NUM.get_id()]=self.CTRL_SLASH_NUM
        self.keys[self.CTRL_ASTERISK_NUM.get_id()]=self.CTRL_ASTERISK_NUM
        self.keys[self.ALT_HOME.get_id()]=self.ALT_HOME
        self.keys[self.ALT_UP_ARROW.get_id()]=self.ALT_UP_ARROW
        self.keys[self.ALT_PAGE_UP.get_id()]=self.ALT_PAGE_UP
        #self.keys[self. .get_id()]=self.
        self.keys[self.ALT_LEFT_ARROW.get_id()]=self.ALT_LEFT_ARROW
        #self.keys[self. .get_id()]=self.
        self.keys[self.ALT_RIGHT_ARROW.get_id()]=self.ALT_RIGHT_ARROW
        #self.keys[self. .get_id()]=self.
        self.keys[self.ALT_END.get_id()]=self.ALT_END
        self.keys[self.ALT_DOWN_ARROW.get_id()]=self.ALT_DOWN_ARROW
        self.keys[self.ALT_PAGE_DOWN.get_id()]=self.ALT_PAGE_DOWN
        self.keys[self.ALT_INSERT.get_id()]=self.ALT_INSERT
        self.keys[self.ALT_DELETE.get_id()]=self.ALT_DELETE
        self.keys[self.ALT_SLASH_NUM.get_id()]=self.ALT_SLASH_NUM
        self.keys[self.ALT_TAB.get_id()]=self.ALT_TAB
        self.keys[self.ALT_ENTER_NUM.get_id()]=self.ALT_ENTER_NUM
        
    def get_key_id(self, code, state):
        """
        a key id is a combination of the code and the state ignoring
        up and down bits. This is done to consider E0 and E1 states
        to differentiate left and right control keys, arrows from numbers, etc
        """
        return int("0x%s%s"% (hex(code).replace('0x', ''),hex(state & 0xFE).replace('0x', '')),16)
    
    def __default_kb_element(self):
        """
        if there is not state, it has never been pressed, so it's up
        """
        return InterceptionKeyState.INTERCEPTION_KEY_UP
        
    def __default_element(self):
        """
        Used to return None instead of a key exception for maps
        """
        return None
            
    def __null_handler(self,interception,event):
        """
        Used as a null handler to disable events like "hold"
        """
        return None
        
    def runMacro(self, autohotpy, macro_list):
        """
        go trough the events list and run the events in the specified time
        run this in another thread or you will block the execution
        autohotpy is in the parameters because I wanted to execute this as a task
        """

        def getTimeDifference(old,new):
            if (old == 0):
                return 0
            return new-old
        last_time=0
        #removing invalid events that the macro accidentally stores
        #startkey UP is pressed as first char
        #startkey DOWN is pressed as last char
        macro_valid_elements = macro_list[1:len(macro_list)-1]
        for event in macro_valid_elements:
            waiting=  getTimeDifference(last_time,event[0])
            #weight=0.00000000001
           # waiting=weight*waiting # I increaase the sspeed 
            self.sleep(waiting) #wait before firing the event
            last_time = event[0]
            
            if (isinstance(event[1],InterceptionMouseStroke)):
#                print("Stroke state:" + str(hex(event[1].state)))
#                print("Stroke flags:" + str(hex(event[1].flags)))
#                print("Stroke information:" + str(hex(event[1].information)))
#                print("Stroke rolling:" + str(hex(event[1].rolling)))
#                print("Stroke x:" + str(hex(event[1].x)))
#                print("Stroke y:" + str(hex(event[1].y)))
                self.sendToDefaultMouse(event[1])
            elif(isinstance(event[1],InterceptionKeyStroke)):
#                print("Stroke scancode:" + str(hex(event[1].code)))
#                print("Stroke state:" + str(hex(event[1].state)))
                self.sendToDefaultKeyboard(event[1])
    
    def sleep(self, *args):
        """
        Sleep. If no parameters are sent, default_interval is assumed.
        useful for waiting between keypress.
        """
        if (len(args) == 0):
            interval = self.default_interval
        else:
            interval=args[0]

        #print("time sleep_old",interval)
       # interval=0.0000000001*interval
       # print("time sleep_new",interval)
        time.sleep(interval)
            
    def start(self):
        if (not self.exit_configured):
            raise Exception("Configure a way to close the process before starting")
        #Load the dll and setup the required functions
        self.interception = InterceptionWrapper()
        # Setup context
        self.context = self.interception.interception_create_context()
        if (self.context == None):
            raise Exception("Interception driver not installed!\nInstall required drivers to continue.")
        self.running = True
        
        # Setup filters.
        self.interception.interception_set_filter(self.context, self.interception.interception_is_keyboard, InterceptionFilterKeyState.INTERCEPTION_FILTER_KEY_ALL);
        self.interception.interception_set_filter(self.context, self.interception.interception_is_mouse, InterceptionFilterMouseState.INTERCEPTION_FILTER_MOUSE_ALL);
        
        # Store a default keyboard and a default mouse
        hardware_id = ctypes.c_byte * 512
        for i in range(10):
            current_dev = self.interception.INTERCEPTION_KEYBOARD(i)
            if (self.interception.interception_is_keyboard(current_dev)):
                size = self.interception.interception_get_hardware_id(self.context, current_dev, ctypes.byref(hardware_id()), 512);
                if (size != 0):
                    self.default_keyboard_device = current_dev
                    break
        for i in range(10):
            current_dev = self.interception.INTERCEPTION_MOUSE(i)
            if (self.interception.interception_is_mouse(current_dev)):
                size = self.interception.interception_get_hardware_id(self.context, current_dev, ctypes.byref(hardware_id()), 512);
                if (size != 0):
                    self.default_mouse_device = current_dev
                    break
            
        
        # Start threads. These will run the functions the user writes
        self.kb_thread = FunctionRunner(self.kb_queue)
        self.kb_thread.setDaemon(True)
        self.kb_thread.start()
        self.mouse_thread = FunctionRunner(self.mouse_queue)
        self.mouse_thread.setDaemon(True)
        self.mouse_thread.start()
        self.macro_thread = FunctionRunner(self.macro_queue)
        self.macro_thread.setDaemon(True)
        self.macro_thread.start()
        
        
        #reserve space for the stroke
        stroke = InterceptionStroke()
        
        while (self.running):
            device = self.interception.interception_wait(self.context)
#            print("#####DEVICE ID:"+str(device))
            if (self.interception.interception_receive(self.context, device, ctypes.byref(stroke), 1) > 0):
                if (self.interception.interception_is_keyboard(device)):
                    kb_event=ctypes.cast(stroke, ctypes.POINTER(InterceptionKeyStroke)).contents
                    if (self.recording_macro & self.enable_kb_macro):
                        self.last_macro.append((time.time(), copy.deepcopy(kb_event)))
                    current_key = self.get_key_id(kb_event.code,kb_event.state)
                    current_state = self.keyboard_state[current_key] #current state for the key
                    self.keyboard_state[current_key] = kb_event.state
                    if (kb_event.state & InterceptionKeyState.INTERCEPTION_KEY_UP): #up
                        user_function = self.keyboard_handler_up[current_key]
                    else:# down
                        if (current_state == kb_event.state):
                            user_function = self.keyboard_handler_hold[current_key]
                        else:
                            user_function = self.keyboard_handler_down[current_key]
                    
                        
                    if (user_function):
                        self.kb_queue.put(Task(self,user_function,copy.deepcopy(kb_event)))
                    else:
                        self.interception.interception_send(self.context, device, ctypes.byref(stroke), 1)
                    
                elif (self.interception.interception_is_mouse(device)):
                    mouse_event=ctypes.cast(stroke, ctypes.POINTER(InterceptionMouseStroke)).contents
                    if (self.recording_macro & self.enable_mouse_macro):
                        self.last_macro.append((time.time(), copy.deepcopy(mouse_event)))
                    if (mouse_event.state != InterceptionMouseState.INTERCEPTION_MOUSE_MOVE):
                        current_state_changed = self.__toggleMouseState(mouse_event)
                        if (current_state_changed):
                            user_function = self.mouse_handler[mouse_event.state]
                        else:
                            #TODO: implement something to make a fake on hold. Mouse clicks don't automatically resend events like keyboard keys do
                            user_function = self.mouse_handler_hold[mouse_event.state]
                    else:
                        user_function = self.mouse_move_handler
                    #print("Stroke state:" + str(hex(mouse_event.state)))
                    #print("Stroke flags:" + str(hex(mouse_event.flags)))
                    #print("Stroke information:" + str(hex(mouse_event.information)))
                    #print("Stroke rolling:" + str(hex(mouse_event.rolling)))
                    #print("Stroke x:" + str(hex(mouse_event.x)))
                    #print("Stroke y:" + str(hex(mouse_event.y)))
                    #print("position 1:" +str(win32gui.GetCursorPos()))
                    if (user_function):
                        self.mouse_queue.put(Task(self,user_function,copy.deepcopy(mouse_event)))
                    else:
                        self.interception.interception_send(self.context, device, ctypes.byref(stroke), 1)
            if self.loopingCall != None:
                self.loopingCall(self)             
        self.macro_queue.join()
        self.kb_queue.join()
        self.mouse_queue.join()
        self.interception.interception_destroy_context(self.context)
    
    def __toggleMouseState(self, mouse_event):
        """
        applies the mouse state change
        returns False if no changes were made
        """
        BUTTON1=1
        BUTTON2=2
        BUTTON3=3
        BUTTON4=4
        BUTTON5=5
        WHEEL=6
        HWHEEL=7
        newState = mouse_event.state
        if ((newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_DOWN) | (newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_UP)):
            return self.__updateButtonState(BUTTON1,newState)
        elif ((newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_2_DOWN) | (newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_2_UP)):
            return self.__updateButtonState(BUTTON2,newState)
        elif ((newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_3_DOWN) | (newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_3_UP)):
            return self.__updateButtonState(BUTTON3,newState)
        elif ((newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_4_DOWN) | (newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_4_UP)):
            return self.__updateButtonState(BUTTON4,newState)
        elif ((newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_5_DOWN) | (newState == InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_5_UP)):
            return self.__updateButtonState(BUTTON5,newState)
        elif (newState == InterceptionMouseState.INTERCEPTION_MOUSE_WHEEL):
            return self.__updateButtonState(WHEEL,mouse_event.rolling)
        elif (newState == InterceptionMouseState.INTERCEPTION_MOUSE_HWHEEL):
            return self.__updateButtonState(HWHEEL,mouse_event.rolling)
            
            
    def __updateButtonState(self, button, newState):
        """
        returns true if the button state has changed
        """
        #Update button 1 if needed
        current_state = self.mouse_state[button]
        if (current_state==newState):
            return False
        else:
            self.mouse_state[button] = newState
            return True
        
    def isRunning(self):
        return self.running
        
    def stop(self):
        self.running = False
        
    def getKeyboardState(self, code, state):
        """
        Return the key state for a given scancode + state mask
        """
        return self.keyboard_state[self.get_key_id(code,state)]
    
    def getMouseState(self, code):
        return self.mouse_state[code]
    
    def registerExit(self, key, handler):
        self.exit_configured = True
        self.keyboard_handler_down[key.get_id()] = handler
        
    def registerForKeyDown(self, key, handler):
        self.keyboard_handler_down[key.get_id()] = handler
    
    def registerForKeyDownAndDisableHoldEvent(self, key, handler):
        self.keyboard_handler_down[key.get_id()] = handler
        self.keyboard_handler_hold[key.get_id()] = self.__null_handler
    
    def registerForKeyUp(self, key, handler):
        self.keyboard_handler_up[key.get_id()] = handler
        
    def registerForKeyHold(self, key, handler):
        self.keyboard_handler_hold[key.get_id()] = handler
    
    def registerForMouseButton(self, key, handler):
        self.mouse_handler[int(key)] = handler
    
    def registerForMouseButtonAndDisableHoldEvent(self, key, handler):
        self.mouse_handler[int(key)] = handler
        self.mouse_handler_hold[int(key)] = self.__null_handler
    
    def registerForMouseButtonHold(self, key, handler):
        self.keyboard_handler_hold[int(key)] = handler
    
    def registerForMouseMovement(self, handler):
        self.mouse_move_handler = handler
        
    def sendToDefaultMouse(self, stroke):
        self.interception.interception_send(self.context, self.default_mouse_device, ctypes.byref(stroke), 1)
        
    def sendToDefaultKeyboard(self, stroke):
        self.interception.interception_send(self.context, self.default_keyboard_device, ctypes.byref(stroke), 1)    
    
    def sendToDevice(self, device, stroke):
        self.interception.interception_send(self.context, device, ctypes.byref(stroke), 1)  
        
    def mouseMacroStartStop(self):
        """
        start/stop recording a macro that only takes mouse events into account
        """
        if (self.recording_macro):
            self.recording_macro = False
        else:
            self.enable_mouse_macro = True
            self.enable_kb_macro = False
            self.recording_macro = True
    def keyboardMacroStartStop(self):
        """
        start/stop recording a macro that only saves keyboard events
        """
        
        if (self.recording_macro):
            self.recording_macro = False
        else:
            self.enable_mouse_macro = False
            self.enable_kb_macro = True
            self.recording_macro = True
    
  
         
    def macroStartStop(self):
        """
        start/stop recording a macro
        """
        

        if (self.recording_macro):
            self.recording_macro = False 
            
        else:
            
            self.enable_mouse_macro = True
            self.enable_kb_macro = True
            self.clearLastRecordedMacro() #clear old macro (if any)
            self.recording_macro = True
           

        
    def fireLastRecordedMacro(self):
        self.recording_macro = False
        self.macro_queue.put(Task(self,self.runMacro,self.last_macro))
        
    def clearLastRecordedMacro(self):
        self.last_macro = []
        
    def __getMouseFlagsString(self, event):
        flags = event.flags
        
        if (flags & InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE):
            flags_string = "InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE"
        else:
            flags_string = "InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE"
        if (flags & InterceptionMouseFlag.INTERCEPTION_MOUSE_VIRTUAL_DESKTOP):
            flags_string += "& InterceptionMouseFlag.INTERCEPTION_MOUSE_VIRTUAL_DESKTOP"
        if (flags & InterceptionMouseFlag.INTERCEPTION_MOUSE_ATTRIBUTES_CHANGED):
            flags_string += "& InterceptionMouseFlag.INTERCEPTION_MOUSE_ATTRIBUTES_CHANGED"
        if (flags & InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_NOCOALESCE):
            flags_string += "& InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_NOCOALESCE"
        if (flags & InterceptionMouseFlag.INTERCEPTION_MOUSE_TERMSRV_SRC_SHADOW):
            flags_string += "& InterceptionMouseFlag.INTERCEPTION_MOUSE_TERMSRV_SRC_SHADOW"
        
        return flags_string
        
    def __getMouseStateString(self, event):
        return {
            0x000 : "InterceptionMouseState.INTERCEPTION_MOUSE_MOVE",
            0x001 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_DOWN",
            0x002 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_UP",
            0x004 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_2_DOWN",
            0x008 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_2_UP",
            0x010 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_3_DOWN",
            0x020 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_3_UP",
            0x040 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_4_DOWN",
            0x080 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_4_UP",
            0x100 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_5_DOWN",
            0x200 : "InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_5_UP",
            0x400 : "InterceptionMouseState.INTERCEPTION_MOUSE_WHEEL",
            0x800 : "InterceptionMouseState.INTERCEPTION_MOUSE_HWHEEL",
        }[event.state]
        
    def saveLastRecordedMacro(self, filename,*args):
        openfile = open(filename, 'w')
        output_script_text = "from AutoHotPy import AutoHotPy\nfrom InterceptionWrapper import *\ndef exitAutoHotKey(autohotpy,event):\n    autohotpy.stop()\ndef recorded_macro(autohotpy, event):\n"
        openfile.write(output_script_text)
        
        if (len(args) == 1):
            openfile.write("    autohotpy.moveMouseToPosition("+str(args[0][0])+","+str(args[0][1])+")\n")
        
        def getTimeDifference(old,new):
            if (old == 0):
                return 0
            return new-old
            
        def getEventKeyId(event):
            return self.get_key_id(event.code, event.state)
        
        last_time=0
        #removing invalid events that the macro accidentally stores
        #startkey UP is pressed as first char
        #startkey DOWN is pressed as last char
        macro_valid_elements = self.last_macro[1:len(self.last_macro)-1]
        for event in macro_valid_elements:
            sleep_time = getTimeDifference(last_time,event[0])
           # print("sleep time_old", sleep_time)
           # if (sleep_time != 0) :
           
           
            #sleep_time= 0.0001*sleep_time 
           #    print("sleep time_new", sleep_time)


            last_time = event[0]
            openfile.write("    autohotpy.sleep("+str(sleep_time)+")\n")
            if (isinstance(event[1],InterceptionMouseStroke)):
                openfile.write("    stroke = InterceptionMouseStroke()\n")
                openfile.write("    stroke.state = "+self.__getMouseStateString(event[1])+"\n")
                openfile.write("    stroke.flags = "+self.__getMouseFlagsString(event[1])+"\n")
                openfile.write("    stroke.rolling = "+str(event[1].rolling)+"\n")
                openfile.write("    stroke.x = "+str(event[1].x)+"\n")
                openfile.write("    stroke.y = "+str(event[1].y)+"\n")
                openfile.write("    stroke.information = "+str(event[1].information)+"\n")
                openfile.write("    autohotpy.sendToDefaultMouse(stroke)\n")
            elif(isinstance(event[1],InterceptionKeyStroke)):
                keyid =getEventKeyId(event[1])
                if (keyid != None):
                    key = self.keys[keyid]
                    keyname = str(key)
                    
                    if (event[1].state & InterceptionKeyState.INTERCEPTION_KEY_UP):
                        openfile.write("    autohotpy."+keyname+".up()\n")
                    else:
                        openfile.write("    autohotpy."+keyname+".down()\n")
                else:
                    code = event[1].code
                    state = event[1].state
                    openfile.write("    stroke = InterceptionMouseStroke()\n")
                    openfile.write("    stroke.code = "+str(code)+"\n")
                    openfile.write("    stroke.state = "+str(state)+"\n")
                    openfile.write("    stroke.information = "+str(event[1].information)+"\n")
                    openfile.write("    autohotpy.sendToDefaultKeyboard(stroke)\n")
        openfile.write("if __name__==\"__main__\":\n    auto = AutoHotPy()\n    auto.registerExit(auto.ESC,exitAutoHotKey)\n    auto.registerForKeyDown(auto.F1,recorded_macro)\n    auto.start()\n")
        openfile.close()

        
    def isRecording(self):
        return self.recording_macro
    
    def getMousePosition(self):
        #x, y = win32api.GetCursorPos()
        res = Point()
        self.user32.GetCursorPos(ctypes.byref(res))
        return (res.x,res.y)
    
    def moveMouseToPosition(self, x, y):
        width_constant = 65535.0/float(self.user32.GetSystemMetrics(0))
        height_constant = 65535.0/float(self.user32.GetSystemMetrics (1)) 
        # move mouse to the specified position
        stroke = InterceptionMouseStroke()
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
        stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE
        stroke.x = int(float(x)*width_constant)
        stroke.y = int(float(y)*height_constant)
        self.sendToDefaultMouse(stroke)
    
    def run(self, macro, trigger_event):
        """
        manually send a macro to be run
        """
        if (isinstance(trigger_event,InterceptionMouseStroke)):
            self.mouse_queue.put(Task(self, macro, trigger_event))
        elif(isinstance(trigger_event,InterceptionKeyStroke)):
            self.kb_queue.put(Task(self, macro, trigger_event))
        
