"""
@author: Emilio Moretti
Copyright 2014 Emilio Moretti <emilio.morettiATgmailDOTcom>
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
#######################################
# Press Alt+F4 after pressing a joystick button combination
####################################### 
import pygame
from pygame.locals import *

# do something when the following buttons are pressed:
# joystick 0: button 3 + joystick 0: button 9 + joystick 1: button 2
PRESSED_BUTTONS = [(0,3),(0,9),(1,2)]


class App:
    def autoHotPyMacro(self,autoHotPyInstance):
        autoHotPyInstance.LEFT_ALT.down() #release alt
        autoHotPyInstance.sleep() #don't forget to sleep when you manually send a "down" state
        autoHotPyInstance.F4.down()
        autoHotPyInstance.sleep()
        autoHotPyInstance.LEFT_ALT.up()
        autoHotPyInstance.F4.up()
        
    def __init__(self):
        pygame.init()
 
        # Set up the joystick
        pygame.joystick.init()
 
        self.my_joysticks = {}

        for joy,button in PRESSED_BUTTONS:
            self.my_joysticks[joy] = pygame.joystick.Joystick(joy)
            self.my_joysticks[joy].init()

 
    # A couple of joystick functions...
    def check_axis(self, joystick, p_axis):
        if (joystick in self.my_joysticks.keys()):
            if (p_axis < self.my_joysticks[joystick].get_numaxes()):
                return self.my_joysticks[joystick].get_axis(p_axis)
 
        return 0
 
    def check_button(self, joystick, p_button):
        if (joystick in self.my_joysticks.keys()):
            if (p_button < self.my_joysticks[joystick].get_numbuttons()):
                return self.my_joysticks[joystick].get_button(p_button)
 
        return False
 
    def check_hat(self, joystick, p_hat):
        if (joystick in self.my_joysticks.keys()):
            if (p_hat < self.my_joysticks[joystick].get_numhats()):
                return self.my_joysticks[joystick].get_hat(p_hat)
 
        return (0, 0)
 
    def loopingCall(self,autohotpy):
        self.g_keys = pygame.event.get()
        for event in self.g_keys:
            if (event.type == QUIT):
                self.quit()
                return
        all_pressed = True
        for joystick,button in PRESSED_BUTTONS:
            if not(self.check_button(joystick,button)):
                all_pressed = False
                break
        if all_pressed:
            self.autoHotPyMacro(autohotpy)         
         
    def quit(self):
        #pygame.display.quit()
        exit(0)

if __name__=="__main__":
    auto = AutoHotPy() #Initialize the library
    auto.registerExit(auto.ESC, exitAutoHotKey) # Registering an end key is mandatory to be able to stop the program gracefully
    app = App()
    auto.loopingCall = app.loopingCall
    auto.start() #Now that everything is registered we should start runnin the program


