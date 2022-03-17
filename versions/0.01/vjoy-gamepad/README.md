





# vjoy-gamepad

vjoy is a module that emulates a generic controller.  Combine this with x360ce, which takes your generic controller and makes it emulate an xbox360 controller, and voila, you have xbox 360 controller emulation. 

I've actually employed this in game and it does work, I just have yet to find a good algorithm to apply to the network output to actually improve the driving performance. 

At the very least, however, I think coming up with something for the throttle control will be wise. Haven't had much time to mess with this, but it's definitely an option now. s

step 1: https://sourceforge.net/projects/vjoystick/files/latest/download

step 2: SDK: http://vjoystick.sourceforge.net/site/index.php/component/weblinks/weblink/13-uncategorised/11-redirect-vjoy2sdk?task=weblink.go

step 3: CONST_DLL_VJOY = "vJoyInterface.dll" ...KEEP .DLL local? 

step 4: http://www.x360ce.com/, 64 bit download

step 5: run, should auto-detect vjoy, test with example make sure it works.

step 6: CLOSE the app, run game. Test with example to see if works.

SOURCE: https://gist.github.com/Flandan/fdadd7046afee83822fcff003ab47087#file-vjoy-py

"Pointy's Joystick Test App" is very useful when testing vJoy and this library: http://www.planetpointy.co.uk/joystick-test-application/

### How to use



```python
import pandas as pd
```


```python
from vjoy2 import *
```


```python
ultimate_release()
```


```python
#Testing keys
test1()
```


```python
#XY Axis up and down
test2()
```

    vj opening
    sending axes
    vj closing



```python
ultimate_release()
```

### Analizing the important buttons in the gamepad

# Right Thumbstick


```python
#RX min
look_rx_left()
```

<img src="img/left-r.jpg" width="700">


```python
#RX max
look_rx_right()

```

<img src="img/right-r.jpg" width="700">


```python
#RY min
look_ry_up()
```

<img src="img/up-r.jpg" width="700">


```python
#RY max
look_ry_down()
```

<img src="img/down-r.jpg" width="700">


```python
ultimate_release()
```


#   Left Thumbstick  


```python
#left
game_lx_left()
```


```python
#right
game_lx_right()
```


```python
#up
game_ly_up()
```


```python
#left
game_ly_down()
```


```python
ultimate_release()
```

# LT and RT  


```python
#Z max
gamepad_lt()
```


```python
#Z min
gamepad_rt()
```


```python
ultimate_release()
```


# RZ


```python
#RZ max
throttle_max()
```


```python
#RZ max
throttle_min()
```

# Buttons A, B, X, Y,


```python
#Button 1 = A    
def button_A():
    vj.open()
    btn = 1
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_A()
```


```python
#Button 2 = B    
def button_B():
    vj.open()
    btn = 2
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_B()
```


```python
#Button 3 = AB   
def button_AB():
    vj.open()
    btn = 3
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_AB()
```


```python
#Button 4 = X   
def button_X():
    vj.open()
    btn = 4
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_X()
```


```python
#Button 5 = AX   
def button_AX():
    vj.open()
    btn = 5
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_AX()
```


```python
#Button 6 = BX   
def button_BX():
    vj.open()
    btn = 6
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_BX()
```


```python
#Button 7 = ABX  
def button_ABX():
    vj.open()
    btn = 7
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_ABX()
```


```python
#Button 8 = Y  
def button_Y():
    vj.open()
    btn = 8
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_Y()
```


```python
#Button 9 = AY  
def button_AY():
    vj.open()
    btn = 9
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_AY()
```


```python
#Button 10 = BY  
def button_BY():
    vj.open()
    btn = 10
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_BY()
```


```python
#Button 11 = ABY  
def button_ABY():
    vj.open()
    btn = 11
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_ABY()
```


```python
#Button 12 = XY  
def button_XY():
    vj.open()
    btn = 12
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_XY()
```


```python
#Button 13 = AXY  
def button_AXY():
    vj.open()
    btn = 13
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_AXY()
```


```python
#Button 14 = BXY  
def button_BXY():
    vj.open()
    btn = 14
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_BXY()
```


```python
#Button 15 = ABXY  
def button_ABXY():
    vj.open()
    btn = 15
    vj.sendButtons(btn)
    time.sleep(0.25)
    vj.sendButtons(0)
    vj.close() 
```


```python
button_ABXY()
```

