from AutoHotPy import AutoHotPy
from InterceptionWrapper import *
import time
def exitAutoHotKey(autohotpy,event):
    autohotpy.stop()
def recorded_macro(autohotpy, event):
    start = time.time()
    autohotpy.moveMouseToPosition(260,385)
    autohotpy.sleep(0)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_DOWN
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.2835216522216797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002797842025756836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030167102813720703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002998828887939453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004056453704833984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009467601776123047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004052877426147461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019502639770507812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029938220977783203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003001689910888672)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002997875213623047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030679702758789062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003042936325073242)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009570121765136719)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0026330947875976562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001672506332397461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029985904693603516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002004861831665039)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019936561584472656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019986629486083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0023539066314697266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0015308856964111328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029916763305664062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001979351043701172)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002233743667602539)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017800331115722656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001986980438232422)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030062198638916016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020322799682617188)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0036935806274414062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030155181884765625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020074844360351562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003998756408691406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0044400691986083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004773855209350586)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0049915313720703125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006044149398803711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008026123046875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.011060237884521484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.016878604888916016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024340152740478516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.012687444686889648)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.010184049606323242)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004971981048583984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0050563812255859375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010128021240234375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005048036575317383)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003957033157348633)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003997802734375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003997802734375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009982585906982422)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020062923431396484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004714250564575195)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003065824508666992)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0040416717529296875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003980398178100586)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029709339141845703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009987354278564453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030231475830078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0039746761322021484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005403995513916016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002969980239868164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032095909118652344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017881393432617188)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0039539337158203125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003996372222900391)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003999233245849609)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005131244659423828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0035479068756103516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005001068115234375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005029916763305664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007950305938720703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004521369934082031)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0045740604400634766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000518798828125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0062253475189208984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005624055862426758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006577730178833008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005272626876831055)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0045053958892822266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029485225677490234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002041339874267578)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00524139404296875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004767417907714844)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005427122116088867)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0005772113800048828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0040242671966552734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005780696868896484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004270076751708984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010123252868652344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001027822494506836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005052089691162109)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003984212875366211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004498481750488281)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024995803833007812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002433300018310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004905223846435547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006211042404174805)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0038046836853027344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009837150573730469)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00759577751159668)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00678706169128418)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005968332290649414)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0005390644073486328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00845646858215332)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008173227310180664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003042459487915039)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004956245422363281)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009551525115966797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007437467575073242)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00055694580078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008315563201904297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006143093109130859)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009980201721191406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007312297821044922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006117582321166992)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009989738464355469)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008031606674194336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005460262298583984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030295848846435547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008518457412719727)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00228118896484375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0070209503173828125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005980491638183594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001005411148071289)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009331941604614258)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010099411010742188)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00803232192993164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002973318099975586)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003483295440673828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0058956146240234375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032041072845458984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0062427520751953125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00154876708984375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006436347961425781)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030221939086914062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0059642791748046875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008302688598632812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029990673065185547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0070264339447021484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0035843849182128906)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0052471160888671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004998207092285156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004778385162353516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007451534271240234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030231475830078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.010986089706420898)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002221345901489258)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008549928665161133)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005611419677734375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004317283630371094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0076940059661865234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008714199066162109)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006508827209472656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005220174789428711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017781257629394531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005745649337768555)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022652149200439453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030341148376464844)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003966093063354492)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00400543212890625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001993417739868164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005559682846069336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010409355163574219)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004324197769165039)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003642559051513672)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0015106201171875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004494667053222656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00440669059753418)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0049779415130615234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003988027572631836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001789093017578125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004047393798828125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003597259521484375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0046024322509765625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004942417144775391)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004000186920166016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0038628578186035156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017592906951904297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004195451736450195)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0038797855377197266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001990079879760742)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001971721649169922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005007743835449219)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003824472427368164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005015850067138672)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003241300582885742)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0047757625579833984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001985788345336914)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003137350082397461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00421452522277832)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0026464462280273438)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0011839866638183594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003015279769897461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002002716064453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004326343536376953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0036640167236328125)
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
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003919124603271484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002733469009399414)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003289937973022461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020706653594970703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002187490463256836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009975433349609375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019986629486083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030014514923095703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002006053924560547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002996206283569336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019989013671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003917217254638672)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010082721710205078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001001596450805664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003005504608154297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004007101058959961)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030078887939453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030069351196289062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00096893310546875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030078887939453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003218412399291992)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032341480255126953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027735233306884766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003000020980834961)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020008087158203125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030069351196289062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002992391586303711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002176523208618164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030045509338378906)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019953250885009766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030062198638916016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019943714141845703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002998828887939453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020008087158203125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030050277709960938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0021352767944335938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031075477600097656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0028352737426757812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002003192901611328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002888202667236328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002049684524536133)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0012714862823486328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022602081298828125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027768611907958984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003005504608154297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030269622802734375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031807422637939453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002758502960205078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00324249267578125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030481815338134766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010731220245361328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005019426345825195)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0014348030090332031)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0005590915679931641)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019948482513427734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004151821136474609)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008487701416015625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003995180130004883)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002011537551879883)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009975433349609375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0011072158813476562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003039121627807617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001971721649169922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032088756561279297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0018117427825927734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009775161743164062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0028662681579589844)
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
    autohotpy.sleep(0.0020084381103515625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010006427764892578)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020148754119873047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001996755599975586)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009887218475341797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019986629486083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009999275207519531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030007362365722656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0016949176788330078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003002166748046875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030069351196289062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009393692016601562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002095937728881836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020258426666259766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0011603832244873047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001825571060180664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002016782760620117)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0011599063873291016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029993057250976562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008223056793212891)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001997709274291992)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030078887939453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002712249755859375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020668506622314453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009419918060302734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003067493438720703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003141164779663086)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010046958923339844)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002817392349243164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032422542572021484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002829313278198242)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0007810592651367188)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022199153900146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001798868179321289)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009794235229492188)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001007080078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029997825622558594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009925365447998047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000570297241211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003401041030883789)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0016865730285644531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0005424022674560547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001996755599975586)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009999275207519531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030069351196289062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004168033599853516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0036334991455078125)
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
    autohotpy.sleep(0.0030078887939453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002018451690673828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00312042236328125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008630752563476562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009987354278564453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009999275207519531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003010272979736328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010232925415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0023186206817626953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009627342224121094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030007362365722656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009992122650146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001374959945678711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003012418746948242)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003009319305419922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009984970092773438)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009932518005371094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029990673065185547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001007080078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001993417739868164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0018351078033447266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00302886962890625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009982585906982422)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010006427764892578)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0013785362243652344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00029206275939941406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003007173538208008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010004043579101562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010018348693847656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030057430267333984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000993490219116211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030825138092041016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0018856525421142578)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010085105895996094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009987354278564453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00200653076171875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019941329956054688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010881423950195312)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019116401672363281)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002001523971557617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00099945068359375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022208690643310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001741170883178711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010089874267578125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010013580322265625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001997232437133789)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003000020980834961)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010027885437011719)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019974708557128906)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003002643585205078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030002593994140625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017960071563720703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024356842041015625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020024776458740234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019969940185546875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010006427764892578)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019989013671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030002593994140625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003443002700805664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0018508434295654297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024957656860351562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0025103092193603516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001993894577026367)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032117366790771484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002788066864013672)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003785848617553711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001275777816772461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0007977485656738281)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003007173538208008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030002593994140625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003008127212524414)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001992464065551758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0034286975860595703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0014874935150146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002998828887939453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0040013790130615234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010004043579101562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030298233032226562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019690990447998047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0026030540466308594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024957656860351562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024111270904541016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002590179443359375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002998828887939453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020062923431396484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029952526092529297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020172595977783203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003551959991455078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0011963844299316406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003766298294067383)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002026081085205078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030252933502197266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003955364227294922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0011014938354492188)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00389862060546875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003865480422973633)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003175497055053711)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020008087158203125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00400090217590332)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002034902572631836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002966642379760742)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004024028778076172)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0035872459411621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0007760524749755859)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020246505737304688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004191160202026367)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0039958953857421875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027887821197509766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005175590515136719)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027534961700439453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000997304916381836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003980398178100586)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003998517990112305)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000570297241211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001997232437133789)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004323482513427734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001277923583984375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020542144775390625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002957582473754883)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009984970092773438)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029997825622558594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001997709274291992)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003007173538208008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001994609832763672)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009992122650146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003191709518432617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004000425338745117)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00403904914855957)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024521350860595703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0025086402893066406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020067691802978516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020034313201904297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004146575927734375)
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
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032758712768554688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010004043579101562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030651092529296875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00293731689453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004219770431518555)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0037794113159179688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004031181335449219)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004174709320068359)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003008127212524414)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009844303131103516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004010677337646484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0014646053314208984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003525972366333008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003422975540161133)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0012013912200927734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030150413513183594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009963512420654297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030066967010498047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000993967056274414)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00422215461730957)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0007774829864501953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0040013790130615234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019989013671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010535717010498047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002012491226196289)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009984970092773438)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030057430267333984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010249614715576172)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009691715240478516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001009225845336914)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019898414611816406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010030269622802734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001997232437133789)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022339820861816406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019791126251220703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001001119613647461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002009153366088867)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029976367950439453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029931068420410156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0034584999084472656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027120113372802734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009989738464355469)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003005504608154297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004172563552856445)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002827167510986328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019919872283935547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002012014389038086)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002971649169921875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003026723861694336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002019166946411133)
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
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0041120052337646484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010268688201904297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003178834915161133)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022606849670410156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0015718936920166016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003000020980834961)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003341197967529297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001659393310546875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010008811950683594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0037267208099365234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0021839141845703125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0018291473388671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019805431365966797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001001596450805664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000997304916381836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000570297241211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010144710540771484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0012140274047851562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030570030212402344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0001239776611328125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010077953338623047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020766258239746094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001924753189086914)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019981861114501953)
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
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000570297241211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019998550415039062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010018348693847656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019979476928710938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002650022506713867)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0028438568115234375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002437591552734375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010497570037841797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0005409717559814453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003210306167602539)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0018086433410644531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001980304718017578)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00200653076171875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0023648738861083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020062923431396484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019936561584472656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020034313201904297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029959678649902344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000570297241211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003411531448364258)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0021140575408935547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008666515350341797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002001523971557617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019989013671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020024776458740234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020334720611572266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002457857131958008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0016148090362548828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019788742065429688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002001523971557617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019979476928710938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020074844360351562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001992940902709961)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020160675048828125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0023031234741210938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00016951560974121094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010097026824951172)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009999275207519531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030024051666259766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009961128234863281)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009989738464355469)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010008811950683594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009996891021728516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020089149475097656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001991748809814453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0032129287719726562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0014657974243164062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019989013671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000980377197265625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009992122650146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002007007598876953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009937286376953125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010004043579101562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030951499938964844)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009927749633789062)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010406970977783203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019867420196533203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030128955841064453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020089149475097656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003180980682373047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019979476928710938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008211135864257812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022161006927490234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017838478088378906)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010004043579101562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001999378204345703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027565956115722656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0026464462280273438)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0025577545166015625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001001119613647461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030050277709960938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009937286376953125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009999275207519531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020012855529785156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030050277709960938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001992464065551758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002002239227294922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030052661895751953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001992940902709961)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002002239227294922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003021717071533203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00101470947265625)
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
    autohotpy.sleep(0.0022382736206054688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009999275207519531)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003006458282470703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029938220977783203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0029993057250976562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009992122650146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0021409988403320312)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003007173538208008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030481815338134766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001990079879760742)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009644031524658203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030455589294433594)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004014253616333008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003981590270996094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009553432464599609)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031938552856445312)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0014162063598632812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031850337982177734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008223056793212891)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003000497817993164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002003908157348633)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019986629486083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019986629486083984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002834320068359375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002049684524536133)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009620189666748047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004000663757324219)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000997781753540039)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003528594970703125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00203704833984375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001012563705444336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031862258911132812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00077056884765625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003002166748046875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009989738464355469)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003009319305419922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0050351619720458984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003435373306274414)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001001119613647461)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030052661895751953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.000993490219116211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004000186920166016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020012855529785156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0040416717529296875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010077953338623047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005006313323974609)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0064640045166015625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0015289783477783203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004524946212768555)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006119251251220703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0004317760467529297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006011247634887695)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002996206283569336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004378557205200195)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008213996887207031)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0003552436828613281)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00601506233215332)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.010089635848999023)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002405405044555664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009760379791259766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0070116519927978516)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007691383361816406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.012345314025878906)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.012435197830200195)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031936168670654297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.02002429962158203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.019060850143432617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002415895462036133)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009676218032836914)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007563114166259766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003031015396118164)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009971141815185547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.01145792007446289)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0036766529083251953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009648799896240234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0075740814208984375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008397817611694336)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.013995885848999023)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004008054733276367)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.012951135635375977)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019922256469726562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.010084152221679688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024433135986328125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008657455444335938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002897977828979492)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009180545806884766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007035970687866211)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.008719444274902344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006714820861816406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00797891616821289)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0033218860626220703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009586334228515625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.010398387908935547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003804922103881836)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.013286352157592773)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.03797793388366699)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0230410099029541)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009150266647338867)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.18559813499450684)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_BUTTON_1_UP
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.15804624557495117)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0031495094299316406)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002869129180908203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030019283294677734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009813308715820312)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030078887939453125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009851455688476562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009958744049072266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003357410430908203)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010292530059814453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030260086059570312)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001976490020751953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009765625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022194385528564453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0007815361022949219)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00099945068359375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020194053649902344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019800662994384766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0024361610412597656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0001747608184814453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010082721710205078)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010001659393310547)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019981861114501953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002000093460083008)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010013580322265625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009992122650146484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003036975860595703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017201900482177734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010111331939697266)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0013267993927001953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0010144710540771484)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00099945068359375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001997709274291992)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00200653076171875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019941329956054688)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022423267364501953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0007593631744384766)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019981861114501953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022552013397216797)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003284454345703125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001772165298461914)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00099945068359375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002999544143676758)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004013538360595703)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002018451690673828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = 1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003192424774169922)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009676933288574219)
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
    autohotpy.sleep(0.12005186080932617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.009029150009155273)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.007999658584594727)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00599980354309082)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.006392955780029297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.005637168884277344)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004191160202026367)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003970146179199219)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020003318786621094)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0027806758880615234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020279884338378906)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0030367374420166016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019719600677490234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002390623092651367)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0016016960144042969)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001972675323486328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020287036895751953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020058155059814453)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00217437744140625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0008187294006347656)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002003192901611328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019960403442382812)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0022029876708984375)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0017979145050048828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0012946128845214844)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020074844360351562)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0020012855529785156)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002007007598876953)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019989013671875)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002003192901611328)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0009922981262207031)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019979476928710938)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019991397857666016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019996166229248047)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003107309341430664)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00220489501953125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0019505023956298828)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.002825498580932617)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.001998424530029297)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.003025054931640625)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.00299835205078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.004000186920166016)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0033872127532958984)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0036163330078125)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0063207149505615234)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = -1
    stroke.y = 0
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    autohotpy.sleep(0.0071675777435302734)
    stroke = InterceptionMouseStroke()
    stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_MOVE
    stroke.flags = InterceptionMouseFlag.INTERCEPTION_MOUSE_MOVE_RELATIVE
    stroke.rolling = 0
    stroke.x = 0
    stroke.y = -1
    stroke.information = 0
    autohotpy.sendToDefaultMouse(stroke)
    end = time.time()
    print(end - start)
if __name__=="__main__":
    auto = AutoHotPy()
    auto.registerExit(auto.ESC,exitAutoHotKey)
    auto.registerForKeyDown(auto.F1,recorded_macro)
    auto.start()
