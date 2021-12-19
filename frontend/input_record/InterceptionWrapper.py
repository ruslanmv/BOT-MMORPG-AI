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
# ctypes to work with interception .dll
import ctypes
    
class InterceptionKeyState(object):
    INTERCEPTION_KEY_DOWN             = 0x00
    INTERCEPTION_KEY_UP               = 0x01
    INTERCEPTION_KEY_E0               = 0x02
    INTERCEPTION_KEY_E1               = 0x04
    INTERCEPTION_KEY_TERMSRV_SET_LED  = 0x08
    INTERCEPTION_KEY_TERMSRV_SHADOW   = 0x10
    INTERCEPTION_KEY_TERMSRV_VKPACKET = 0x20

class InterceptionFilterKeyState(object):
    INTERCEPTION_FILTER_KEY_NONE             = 0x0000
    INTERCEPTION_FILTER_KEY_ALL              = 0xFFFF
    INTERCEPTION_FILTER_KEY_DOWN             = InterceptionKeyState.INTERCEPTION_KEY_UP
    INTERCEPTION_FILTER_KEY_UP               = InterceptionKeyState.INTERCEPTION_KEY_UP << 1
    INTERCEPTION_FILTER_KEY_E0               = InterceptionKeyState.INTERCEPTION_KEY_E0 << 1
    INTERCEPTION_FILTER_KEY_E1               = InterceptionKeyState.INTERCEPTION_KEY_E1 << 1
    INTERCEPTION_FILTER_KEY_TERMSRV_SET_LED  = InterceptionKeyState.INTERCEPTION_KEY_TERMSRV_SET_LED << 1
    INTERCEPTION_FILTER_KEY_TERMSRV_SHADOW   = InterceptionKeyState.INTERCEPTION_KEY_TERMSRV_SHADOW << 1
    INTERCEPTION_FILTER_KEY_TERMSRV_VKPACKET = InterceptionKeyState.INTERCEPTION_KEY_TERMSRV_VKPACKET << 1

class InterceptionMouseState(object):
    INTERCEPTION_MOUSE_MOVE               = 0x000
    INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN   = 0x001
    INTERCEPTION_MOUSE_LEFT_BUTTON_UP     = 0x002
    INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN  = 0x004
    INTERCEPTION_MOUSE_RIGHT_BUTTON_UP    = 0x008
    INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN = 0x010
    INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP   = 0x020
    INTERCEPTION_MOUSE_BUTTON_1_DOWN      = INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
    INTERCEPTION_MOUSE_BUTTON_1_UP        = INTERCEPTION_MOUSE_LEFT_BUTTON_UP
    INTERCEPTION_MOUSE_BUTTON_2_DOWN      = INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
    INTERCEPTION_MOUSE_BUTTON_2_UP        = INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
    INTERCEPTION_MOUSE_BUTTON_3_DOWN      = INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN
    INTERCEPTION_MOUSE_BUTTON_3_UP        = INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP
    INTERCEPTION_MOUSE_BUTTON_4_DOWN      = 0x040
    INTERCEPTION_MOUSE_BUTTON_4_UP        = 0x080
    INTERCEPTION_MOUSE_BUTTON_5_DOWN      = 0x100
    INTERCEPTION_MOUSE_BUTTON_5_UP        = 0x200
    INTERCEPTION_MOUSE_WHEEL              = 0x400
    INTERCEPTION_MOUSE_HWHEEL             = 0x800

class InterceptionFilterMouseState(object):
    INTERCEPTION_FILTER_MOUSE_NONE               = 0x0000
    INTERCEPTION_FILTER_MOUSE_ALL                = 0xFFFF
    INTERCEPTION_FILTER_MOUSE_LEFT_BUTTON_DOWN   = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
    INTERCEPTION_FILTER_MOUSE_LEFT_BUTTON_UP     = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
    INTERCEPTION_FILTER_MOUSE_RIGHT_BUTTON_DOWN  = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
    INTERCEPTION_FILTER_MOUSE_RIGHT_BUTTON_UP    = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
    INTERCEPTION_FILTER_MOUSE_MIDDLE_BUTTON_DOWN = InterceptionMouseState.INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN
    INTERCEPTION_FILTER_MOUSE_MIDDLE_BUTTON_UP   = InterceptionMouseState.INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP
    INTERCEPTION_FILTER_MOUSE_BUTTON_1_DOWN      = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_DOWN
    INTERCEPTION_FILTER_MOUSE_BUTTON_1_UP        = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_UP
    INTERCEPTION_FILTER_MOUSE_BUTTON_2_DOWN      = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_2_DOWN
    INTERCEPTION_FILTER_MOUSE_BUTTON_2_UP        = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_2_UP
    INTERCEPTION_FILTER_MOUSE_BUTTON_3_DOWN      = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_3_DOWN
    INTERCEPTION_FILTER_MOUSE_BUTTON_3_UP        = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_3_UP
    INTERCEPTION_FILTER_MOUSE_BUTTON_4_DOWN      = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_4_DOWN
    INTERCEPTION_FILTER_MOUSE_BUTTON_4_UP        = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_4_UP
    INTERCEPTION_FILTER_MOUSE_BUTTON_5_DOWN      = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_5_DOWN
    INTERCEPTION_FILTER_MOUSE_BUTTON_5_UP        = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_5_UP
    INTERCEPTION_FILTER_MOUSE_WHEEL              = InterceptionMouseState.INTERCEPTION_MOUSE_WHEEL
    INTERCEPTION_FILTER_MOUSE_HWHEEL             = InterceptionMouseState.INTERCEPTION_MOUSE_HWHEEL
    INTERCEPTION_FILTER_MOUSE_MOVE               = 0x1000

class InterceptionMouseFlag(object):
    """
    If INTERCEPTION_MOUSE_MOVE_ABSOLUTE value is specified, dx and dy contain
    normalized absolute coordinates between 0 and 65,535.
    The event procedure maps these coordinates onto the display surface.
    Coordinate (0,0) maps onto the upper-left corner of the display surface;
    coordinate (65535,65535) maps onto the lower-right corner.
    In a multimonitor system, the coordinates map to the primary monitor. 
    http://msdn.microsoft.com/en-us/library/windows/desktop/ms646273%28v=vs.85%29.aspx
    """
    INTERCEPTION_MOUSE_MOVE_RELATIVE      = 0x000
    INTERCEPTION_MOUSE_MOVE_ABSOLUTE      = 0x001
    INTERCEPTION_MOUSE_VIRTUAL_DESKTOP    = 0x002
    INTERCEPTION_MOUSE_ATTRIBUTES_CHANGED = 0x004
    INTERCEPTION_MOUSE_MOVE_NOCOALESCE    = 0x008
    INTERCEPTION_MOUSE_TERMSRV_SRC_SHADOW = 0x100

class InterceptionMouseStroke(ctypes.Structure):
    _fields_ = [("state", ctypes.c_ushort),
                ("flags", ctypes.c_ushort),
                ("rolling", ctypes.c_short),
                ("x", ctypes.c_int),
                ("y", ctypes.c_int),
                ("information", ctypes.c_uint)]


class InterceptionKeyStroke(ctypes.Structure):
    _fields_ = [("code", ctypes.c_ushort),
                ("state", ctypes.c_ushort),
                ("information", ctypes.c_uint)]

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

#typedef char InterceptionStroke[sizeof(InterceptionMouseStroke)];
InterceptionStroke = InterceptionMouseStroke * 1

#typedef void *InterceptionContext;
InterceptionContext_p = ctypes.c_void_p

#typedef int InterceptionDevice;
InterceptionDevice = ctypes.c_int

#typedef int InterceptionPrecedence;
InterceptionPrecedence = ctypes.c_int

#typedef unsigned short InterceptionFilter;
InterceptionFilter = ctypes.c_uint


    

class InterceptionWrapper(object):
    INTERCEPTION_MAX_KEYBOARD = 10    
    INTERCEPTION_MAX_MOUSE = 10    
    INTERCEPTION_MAX_DEVICE = ((INTERCEPTION_MAX_KEYBOARD) + (INTERCEPTION_MAX_MOUSE))
    
    def INTERCEPTION_KEYBOARD(self, index):
        return ((index) + 1)
    
    def INTERCEPTION_MOUSE(self, index):
        return ((self.INTERCEPTION_MAX_KEYBOARD) + (index) + 1)
    
    def __interception_is_invalid(self, device):
        """
        int ITERCEPTION_API interception_is_invalid(InterceptionDevice device);
        """
        return self.interceptionDll.interception_is_invalid(device)
    
    def __interception_is_keyboard(self, device):
        """
        int ITERCEPTION_API interception_is_keyboard(InterceptionDevice device);
        """
        return self.interceptionDll.interception_is_keyboard(device)
        
    def __interception_is_mouse(self, device):
        """
        int ITERCEPTION_API interception_is_mouse(InterceptionDevice device);
        """
        return self.interceptionDll.interception_is_mouse(device)
        
    def __init__(self):
        # Load DLL into memory.
        self.interceptionDll = ctypes.WinDLL ("./interception.dll")
        
        # Setup return types
        self.interceptionDll.interception_create_context.restype = InterceptionContext_p
        self.interceptionDll.interception_get_filter.restype = InterceptionFilter
        self.interceptionDll.interception_get_precedence.restype = InterceptionPrecedence
        self.interceptionDll.interception_wait.restype = InterceptionDevice
        self.interceptionDll.interception_wait_with_timeout.restype = InterceptionDevice
        self.interceptionDll.interception_is_invalid.restype = ctypes.c_int
        self.interceptionDll.interception_is_keyboard.restype = ctypes.c_int
        self.interceptionDll.interception_is_mouse.restype = ctypes.c_int
        self.interceptionDll.interception_send.restype = ctypes.c_int
        self.interceptionDll.interception_receive.restype = ctypes.c_int
        self.interceptionDll.interception_get_hardware_id.restype = ctypes.c_uint

        
        #Setup callback functions (that actually call the dll again)
        funct_type = ctypes.WINFUNCTYPE(ctypes.c_int,InterceptionDevice)
        self.interception_is_invalid  = funct_type(self.__interception_is_invalid)
        self.interception_is_keyboard = funct_type(self.__interception_is_keyboard)
        self.interception_is_mouse = funct_type(self.__interception_is_mouse)


        # Setup argument info for functions requiring pointer to InterceptionContext
        self.interceptionDll.interception_destroy_context.argtypes = [InterceptionContext_p]
        self.interceptionDll.interception_set_filter.argtypes = [InterceptionContext_p,
                                                                 funct_type,
                                                                 InterceptionFilter]
        self.interceptionDll.interception_get_filter.argtypes = [InterceptionContext_p,
                                                                 InterceptionDevice]
        self.interceptionDll.interception_get_precedence.argtypes = [InterceptionContext_p,
                                                                     InterceptionDevice]
        self.interceptionDll.interception_set_precedence.argtypes = [InterceptionContext_p,
                                                                     InterceptionDevice,
                                                                     InterceptionPrecedence]
        self.interceptionDll.interception_wait.argtypes = [InterceptionContext_p]
        self.interceptionDll.interception_wait_with_timeout.argtypes = [InterceptionContext_p]
        self.interceptionDll.interception_send.argtypes = [InterceptionContext_p,
                                                           InterceptionDevice,
                                                           ctypes.c_void_p,
                                                           ctypes.c_uint]
        self.interceptionDll.interception_receive.argtypes = [InterceptionContext_p,
                                                           InterceptionDevice,
                                                           ctypes.c_void_p,
                                                           ctypes.c_uint]
        self.interceptionDll.interception_get_hardware_id.argtypes = [InterceptionContext_p,
                                                                      InterceptionDevice,
                                                                      ctypes.c_void_p,
                                                                      ctypes.c_uint]
        
    
    def interception_create_context(self):
        """
        InterceptionContext ITERCEPTION_API interception_create_context(void);
        """
        return self.interceptionDll.interception_create_context()
    
    def interception_destroy_context(self, context):
        """
        void ITERCEPTION_API interception_destroy_context(InterceptionContext context);
        """
        return self.interceptionDll.interception_destroy_context(context)
    
    def interception_set_filter(self, context, predicate, filter1):
        """
        void ITERCEPTION_API interception_set_filter(InterceptionContext context, InterceptionPredicate predicate, InterceptionFilter filter);
        """
        return self.interceptionDll.interception_set_filter(context, predicate, filter1)
        
    def interception_get_filter(self, context, device):
        """
        InterceptionFilter ITERCEPTION_API interception_get_filter(InterceptionContext context, InterceptionDevice device);
        """
        return self.interceptionDll.interception_get_filter(context, device)
        
    def interception_get_precedence(self, context, device):
        """
        InterceptionPrecedence ITERCEPTION_API interception_get_precedence(InterceptionContext context, InterceptionDevice device);
        """
        return self.interceptionDll.interception_get_precedence(context, device)
        
    def interception_set_precedence(self, context, device, precedence):
        """
        void ITERCEPTION_API interception_set_precedence(InterceptionContext context, InterceptionDevice device, InterceptionPrecedence precedence);
        """
        return self.interceptionDll.interception_set_precedence(context, device, precedence)
    
    def interception_wait(self, context):
        """
        InterceptionDevice ITERCEPTION_API interception_wait(InterceptionContext context);
        """
        return self.interceptionDll.interception_wait(context)
        
    def interception_wait_with_timeout(self, context):
        """
        InterceptionDevice ITERCEPTION_API interception_wait_with_timeout(InterceptionContext context, unsigned long milliseconds);
        """
        return self.interceptionDll.interception_wait_with_timeout(context)
        
    def interception_send(self, context, device, stroke_p, nstroke):
        """
        #int ITERCEPTION_API interception_send(InterceptionContext context, InterceptionDevice device, const InterceptionStroke *stroke, unsigned int nstroke);
        """
        return self.interceptionDll.interception_send(context, device, stroke_p, nstroke)
        
    def interception_receive(self, context, device, stroke_p, nstroke):
        """
        int ITERCEPTION_API interception_receive(InterceptionContext context, InterceptionDevice device, InterceptionStroke *stroke, unsigned int nstroke);
        """
        return self.interceptionDll.interception_receive(context, device, stroke_p, nstroke)
    
    def interception_get_hardware_id(self, context, device, hardware_id_buffer_p, buffer_size):
        """
        unsigned int ITERCEPTION_API interception_get_hardware_id(InterceptionContext context, InterceptionDevice device, void *hardware_id_buffer, unsigned int buffer_size);
        """
        return self.interceptionDll.interception_get_hardware_id(context, device, hardware_id_buffer_p, buffer_size)


#TODO:
#the following typedef is not needed. it basically defines the function to send to set_filter (we do that manually)
#typedef int (*InterceptionPredicate)(InterceptionDevice device);
