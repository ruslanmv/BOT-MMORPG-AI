from AutoHotPy import AutoHotPy
from InterceptionWrapper import *
import time
def exitAutoHotKey(autohotpy,event):
    autohotpy.stop()
def recorded_macro(autohotpy, event):
    start = time.time()
    autohotpy.moveMouseToPosition(241,388)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_DOWN
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.6300001144409184e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.9998760223388674e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000020980834961e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000259399414063e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039065e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310547e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0005702972412112e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519532e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039065e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0015239715576174e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.98973846435547e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621094e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621094e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519532e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0005702972412112e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0013580322265626e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.998424530029297e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0066032409667969e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9929409027099612e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101564e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0113716125488283e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9888877868652346e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519532e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519532e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039065e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101564e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310547e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666017e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101564e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0015964508056642e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.992122650146485e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9989013671875003e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0010471343994142e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.987354278564454e-09)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101564e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x =0
    stroke.y=1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)

    end = time.time()
    print(end - start)
if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)
    auto.registerForKeyDown(auto.F1,recorded_macro)
    auto.start()
