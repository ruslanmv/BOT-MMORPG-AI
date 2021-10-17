import pyautogui
import time
import cv2
import numpy as np
x = 1
while x < 4:

    capture = pyautogui.screenshot('saved_'+str(x)+'.png')
    capture = cv2.cvtColor(np.array(capture), cv2.COLOR_RGB2BGR)
    cv2.imshow("image",capture)
    cv2.waitKey(0)

    x += 1
    time.sleep(2)