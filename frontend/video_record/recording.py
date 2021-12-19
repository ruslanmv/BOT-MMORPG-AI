# importing the required packages
import pyautogui
import cv2
import numpy as np
import time
from datetime import datetime

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized


print(" Recording your screen")
print(" Press q to quit the program")

# Specify resolution
resolution = (1920, 1080)

# Specify video codec
codec = cv2.VideoWriter_fourcc(*"XVID")

# Specify name of Output file
filename = "Recording.avi"
# Specify frames rate. We can choose any
# value and experiment with it
fps = 2.0
fpsLimit = 1 # throttle limit
startTime = time.time()
# Creating a VideoWriter object
#out = cv2.VideoWriter(filename, codec, fps, resolution)

# Create an Empty window
cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
# Resize this window
cv2.resizeWindow("Live", 480, 270)


cnt = 1
while True:
    #while (1):
    #while cnt < 4:
    # Take screenshot using PyAutoGUI
    #img = pyautogui.screenshot()
    #capture = pyautogui.screenshot('saved_'+str(cnt)+'.png')
    capture = pyautogui.screenshot()
    # Convert the screenshot to a numpy array
    #frame = np.array(img)
    # Convert it from BGR(Blue, Green, Red) to
    # RGB(Red, Green, Blue)
    #image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    capture = cv2.cvtColor(np.array(capture), cv2.COLOR_RGB2BGR)
    
    
    
    # Resize this window
    cv2.resizeWindow("Live", 480, 270)
    
    #
    capture = image_resize(capture, height = 160)
    
    #
    # Write it to the output file
    ##    ret, frame = cap.read()
    ##    image_rgb = fgbg.apply(frame)
    ##    cv2.imshow('frame',image_rgb)
    #cv2.imshow("image",capture)
    nowTime = time.time()
    if (int(nowTime - startTime)) > fpsLimit:
        timestamp ="./IMG/gameplay_"+datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]+ ".jpg"
        print(timestamp)
       # cv2.imwrite("./IMG/frame" + str(cnt) + ".jpg", capture)
        cv2.imwrite(timestamp, capture)
        #cv2.waitKey(0)
        cnt += 1
        #time.sleep(2)

        #out.write(frame)
       

        # Optional: Display the recording screen
        cv2.imshow('Live', capture)
        
        startTime = time.time() # reset time
            
            
        # Stop recording when we press 'q'
        if cv2.waitKey(1) == ord('q'):
            break
# Release the Video writer
#out.release()

# Destroy all windows
cv2.destroyAllWindows()
