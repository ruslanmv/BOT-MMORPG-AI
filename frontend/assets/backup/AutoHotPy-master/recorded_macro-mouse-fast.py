from AutoHotPy import AutoHotPy
from InterceptionWrapper import *
import time
def exitAutoHotKey(autohotpy,event):
    autohotpy.stop()
def recorded_macro(autohotpy, event):
    start = time.time()
    autohotpy.moveMouseToPosition(245,387)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_DOWN
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1415457725524902e-05)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.995180130004883e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0073394775390627e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.932518005371094e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.227306365966797e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.988649368286133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.892255783081055e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.968280792236329e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.999544143676758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0096302032470705e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9905567169189455e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0103454589843751e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9966831207275394e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.1068325042724613e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.401828765869141e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9371509552001953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.004312515258789e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.932518005371094e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.007173538208008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9927024841308593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.79998779296875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0282993316650391e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0362606048583986e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.965211868286133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9992332458496094e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.998828887939453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.992122650146485e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9999485015869145e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.000041961669922e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.001731872558594e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7028093338012696e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9969701766967773e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.000207901000977e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.003162384033204e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.776571273803712e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.8771629333496096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.894371032714845e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.625797271728516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.2309761047363285e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.841472625732422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0083656311035157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.884834289550782e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0739307403564456e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.272098541259766e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.1351318359375004e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.370668411254883e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.99835205078125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0011196136474609e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.982585906982422e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0017623901367188e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519531e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0091533660888672e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.991914749145508e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0011196136474609e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2161006927490234e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7812252044677734e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.4495124816894533e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.417398452758789e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2091865539550783e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7919540405273439e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9779205322265625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0096302032470705e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9898414611816406e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0301342010498048e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9707679748535156e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.007007598876953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.925365447998047e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0025501251220704e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9819736480712892e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.986980438232422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0083656311035157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9953250885009768e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9888153076171876e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0263195037841797e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.7577152252197267e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3622512817382813e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.050804138183594e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.774093627929688e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.007266998291016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.555723190307618e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.973505020141602e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.302287101745606e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.6933679580688477e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.405612945556641e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.057905197143555e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.185293197631836e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0151863098144532e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.320880889892579e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0287761688232422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.542350769042969e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.993034362792969e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0096302032470705e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.935192108154298e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0399818420410157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.967357635498047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.4377574920654296e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.058050155639649e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.933740615844727e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.794235229492187e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.922079086303711e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0080337524414063e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0756721496582032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.222797393798829e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9305686950683595e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.86810302734375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.796619415283204e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.645202636718751e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0137557983398438e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.032135009765625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9644966125488283e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0374526977539063e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.962516784667969e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0399093627929688e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.957841873168945e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.000280380249024e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.984970092773438e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.038976669311524e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0108947753906251e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9942264556884766e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.959085464477539e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.58271598815918e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.007007598876953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9927024841308593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.228042602539063e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.513191223144532e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.5197734832763676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.806591033935547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.771305084228516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0018348693847657e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.998207092285156e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.227472305297852e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0073394775390627e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0050277709960937e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.989126205444336e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.5447349548339847e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.4778118133544924e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0023117065429687e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.997802734375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.2114257812500005e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.786563873291016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.4205913543701174e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.3453960418701172e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9687156677246096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.002809524536133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0292739868164067e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.971649169921875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.095243453979493e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.765344619750977e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9158592224121096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.007101058959961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0651817321777346e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.002788543701172e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.022836685180664e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0035972595214844e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2783279418945313e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0342807769775394e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.002405166625977e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9329528808593754e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.058910369873047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9380321502685546e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9858818054199223e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.7088394165039065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.169536590576172e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.2603740692138676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.7454833984375004e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.6586990356445317e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.425670623779297e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000020980834961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0059814453125003e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0009746551513676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.992391586303711e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0062923431396485e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2253990173339844e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.8236637115478516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9990673065185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0395984649658207e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9616355895996093e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.408670425415039e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.029346466064453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.106521606445313e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.87318229675293e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0069351196289065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0069351196289065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0182132720947266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.727478027343751e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.7181377410888674e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0505657196044924e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.889602661132813e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.926422119140625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.995014190673828e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0019283294677737e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9203891754150393e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.98817253112793e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.195192337036133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.809835433959961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9942989349365235e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.2018680572509765e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7988681793212892e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9399394989013674e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.7284622192382814e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.2302398681640625e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.1244029998779297e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(8.847713470458985e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.9945068359375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9997825622558593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.871917724609375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1262893676757814e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0092258453369141e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0059089660644535e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.021312713623047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9785633087158205e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.992868423461914e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000020980834961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.2978057861328125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.985311508178711e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.9945068359375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000497817993164e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0273456573486328e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9719600677490236e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.020286560058594e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.794235229492187e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.6210079193115236e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0089149475097657e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.017974853515625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9339790344238285e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0075569152832032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519531e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.007007598876953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.937286376953125e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.000186920166016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0009021759033207e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519531e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.331422805786133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.9945068359375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0009746551513676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.2272338867187503e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.997875213623047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.750988006591797e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9990673065185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0182857513427735e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.988649368286133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.72369384765625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9997825622558593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000570297241211e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.045797348022461e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0074119567871096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.949310302734375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.20942497253418e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0151863098144532e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3000240325927734e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9981861114501955e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0078887939453126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.93967056274414e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9989013671875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.006696701049805e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.2164115905761718e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.010988235473633e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.522157669067383e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.858804702758789e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.6195259094238286e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.4240016937255863e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.02886962890625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.512859344482422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000020980834961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.005193710327149e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.24812126159668e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0349750518798829e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.463340759277344e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.796619415283204e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.044843673706055e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.789466857910157e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.996278762817383e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.979351043701172e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0155906677246095e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0154247283935547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.5326480865478516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.5155544281005863e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.739067077636719e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0225048065185548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.201080322265625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.76052474975586e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9990673065185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0069351196289065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.930133819580079e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.6847591400146487e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9691925048828126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0128021240234375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.221439361572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.7763118743896486e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0069351196289065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.93967056274414e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9985904693603517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.055095672607422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.097606658935547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0139942169189453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0887126922607424e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9364356994628907e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9721260070800785e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0067691802978516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.130840301513672e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.000301361083984e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9855499267578125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.301454544067383e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9214153289794923e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.773834228515625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0008087158203126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9989013671875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0006427764892579e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.998279571533203e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0291080474853515e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.971649169921875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.000663757324219e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0368099212646486e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.634494781494141e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9989013671875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0010471343994142e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.99835205078125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.9945068359375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0015964508056641e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.975433349609375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.002788543701172e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0275115966796876e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.7716159820556643e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9803047180175781e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.064943313598633e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.934051513671875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0006427764892579e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0064582824707034e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.93967056274414e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.98973846435547e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000570297241211e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519531e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.848459243774414e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0286312103271484e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.270294189453125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.393360137939454e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.986980438232422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9976367950439455e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0048618316650393e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3725032806396487e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.6236305236816407e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0175704956054688e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.230478286743164e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.999544143676758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.061128616333008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.992122650146485e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000570297241211e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.99835205078125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.184795379638672e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9440650939941407e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.987354278564453e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.259420394897461e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.7408599853515624e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.999544143676758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0597705841064453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.1765232086181642e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.572391510009766e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.6045570373535157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0111331939697266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.2684803009033203e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.2265186309814457e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.562305450439453e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.97304916381836e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.99835205078125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0084381103515626e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9922256469726563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519531e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.236604690551758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.536296844482422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.210378646850586e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.894039154052735e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.9945068359375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0012855529785157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.016471862792969e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.961128234863281e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.2090206146240234e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7783641815185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.417325973510742e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1718273162841798e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0008087158203126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0771026611328127e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9254684448242187e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0220279693603517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9743442535400392e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.66718864440918e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.004384994506836e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.187894821166992e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7783641815185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0220279693603517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.1905899047851564e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.7911663055419924e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2950172424316407e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3255348205566407e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.006696701049805e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9938945770263673e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0303001403808597e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9702186584472657e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.023386001586914e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.775161743164063e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0201206207275392e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.4708251953125005e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7557144165039064e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.004240036010742e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0069351196289065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0083656311035157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.884834289550782e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3899078369140624e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0941238403320314e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.775669097900391e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.005743026733399e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.996278762817383e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.975433349609375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.997947692871094e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0152072906494144e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9911994934082035e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7838478088378908e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.99835205078125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0045509338378906e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2041797637939455e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.898807525634767e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9993057250976563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1510848999023438e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.8525123596191407e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.3755302429199223e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.360820770263672e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.4554729461669923e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.5234222412109375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.796619415283204e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.992122650146485e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0011196136474609e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.98973846435547e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.999544143676758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.437519073486328e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0333995819091797e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.002166748046875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9981861114501955e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.483959197998047e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9986629486083985e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0006427764892579e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9989013671875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0263919830322265e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.1710395812988283e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9795894622802735e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.998828887939453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9997825622558593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0116100311279297e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0194053649902346e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.701251983642579e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.992122650146485e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9993057250976563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0077953338623047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.089500427246094e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.15203857421875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.043413162231445e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.660720825195313e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0373592376708985e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.961397171020508e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0074119567871096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.930133819580079e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0013580322265626e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0672550201416015e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.008749008178711e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.287792205810547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2227764129638672e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.7773380279541017e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9990673065185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.007246017456055e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.1674633026123047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0647773742675781e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.008127212524414e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0008087158203126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0337104797363283e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9659271240234375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0589828491210938e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.410381317138672e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2335052490234377e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.183364868164063e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9985904693603517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0187835693359375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9997825622558593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0139217376708985e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.682178497314454e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.044771194458008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9892921447753907e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7728805541992188e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.1914710998535157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.8160343170166017e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0009746551513676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.001689910888672e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9977092742919924e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.455711364746094e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.546072006225586e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.176046371459961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.683473587036133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9986629486083985e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.007722854614258e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.999544143676758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9943714141845704e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0325183868408204e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.66787338256836e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.742290496826172e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3822784423828127e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0063648223876954e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.185344696044922e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.8160343170166017e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.017021179199219e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.986503601074219e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.996278762817383e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0453929901123047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0096302032470705e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.3941993713378906e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.639263153076172e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.998424530029297e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.00653076171875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9927024841308593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.007007598876953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9931793212890627e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0985603332519533e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0103454589843751e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9969940185546875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0840167999267578e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9168128967285157e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0151138305664064e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9834041595458986e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0008087158203126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9990673065185547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.4945735931396485e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.3067722320556641e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.1900405883789064e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.767873764038086e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.998828887939453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0067691802978516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.993034362792969e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0034313201904298e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.7455558776855473e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0143985748291018e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.977817535400392e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1856555938720704e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.8154850006103517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.975433349609375e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.996891021728516e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.008127212524414e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.920597076416016e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1837482452392578e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.758026123046875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.006053924560547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.000093460083008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.008604049682617e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9919872283935547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0623207092285156e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9693374633789064e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9893646240234376e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0236968994140625e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1436939239501953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0314922332763674e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.677410125732423e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0162334442138675e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.1345615386962893e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.531932830810547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.017498016357422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.901191711425782e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.997947692871094e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0074119567871096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.920597076416016e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0074844360351564e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.993106842041016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.5420188903808595e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.2354850769042969e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9311904907226564e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0008087158203126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0009746551513676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0194053649902346e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.806156158447266e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.236604690551758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7633438110351563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9974708557128906e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.8410682678222656e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0645389556884766e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9629001617431641e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.207921981811524e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.76637077331543e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0411014556884768e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9671916961669923e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000020980834961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.022981643676758e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9955635070800783e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.813308715820313e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.2079944610595704e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.792835235595703e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0193328857421874e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0067691802978516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.002166748046875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.984970092773438e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0063858032226565e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.930133819580079e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.960371017456055e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0011196136474609e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.89675521850586e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9991397857666016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0004043579101563e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.007173538208008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.006219863891602e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9893646240234376e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0003318786621096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.290487289428711e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.999275207519531e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9998550415039062e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9993782043457032e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0001659393310548e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0074119567871096e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.946823120117188e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.237558364868164e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.773284912109375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.899139404296875e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.8282871246337894e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.127979278564453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.2350292205810547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.8291473388671875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.93421745300293e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.00653076171875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0008087158203126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.2303333282470703e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7621517181396487e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9081573486328125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0170936584472657e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9839744567871095e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.958744049072266e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0009746551513676e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.019094467163086e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.531051635742188e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.295494079589844e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.0079612731933595e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.018949508666993e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.17582893371582e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.8051605224609377e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.001140594482422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.0006427764892579e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.027294158935547e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.583099365234375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.960371017456055e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.007173538208008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.428791046142578e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.5904178619384766e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.5316219329833986e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.782676696777344e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.4466514587402344e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9093494415283207e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.8738250732421876e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9997825622558593e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000020980834961e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.91731071472168e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.58669662475586e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.99725341796875e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.433393478393555e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.5702457427978517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1653900146484375e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.310535430908204e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9992332458496094e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.227254867553712e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.820823669433594e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.06281852722168e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.361318588256836e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0078887939453126e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9996166229248047e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.995180130004883e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.176782608032227e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.995346069335938e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(9.915828704833986e-08)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.9985904693603517e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.032062530517579e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.191326141357422e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.315303802490234e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.5518875122070313e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(6.109237670898438e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.870891571044922e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.967451095581054e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.2710094451904297e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.765748977661133e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.858732223510742e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.008459091186524e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.997730255126953e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.030704498291016e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.2810440063476565e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.339529037475586e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.425048828125e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.788471221923828e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.785444259643555e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.611637115478516e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0663013458251954e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9682388305664065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9752979278564453e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.0094852447509765e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.9893646240234376e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.255367279052735e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.83503532409668e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.0069351196289065e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(2.996444702148438e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.000736236572266e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.744840621948242e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.9579868316650394e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.373384475708008e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.6079883575439455e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.1366348266601565e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.173444747924805e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.1974315643310546e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(5.483150482177735e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(4.742860794067383e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.808923721313477e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(7.606267929077149e-07)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.1717414855957031e-05)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_UP
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.314471244812012e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(1.7107725143432618e-06)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(3.599174022674561e-05)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    end = time.time()
    print(end - start)
if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)
    auto.registerForKeyDown(auto.F1,recorded_macro)
    auto.start()
