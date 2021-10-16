# importing the required packages
import pyautogui
import cv2
import numpy as np
import time
# Specify resolution
resolution = (1920, 1080)

# Specify video codec
codec = cv2.VideoWriter_fourcc(*"XVID")

# Specify name of Output file
filename = "Recording.avi"
# Specify frames rate. We can choose any
# value and experiment with it
fps = 2.0


# Creating a VideoWriter object
out = cv2.VideoWriter(filename, codec, fps, resolution)

# Create an Empty window
cv2.namedWindow("Live", cv2.WINDOW_NORMAL)

# Resize this window
cv2.resizeWindow("Live", 480, 270)
cnt = 1
#while True:
#while (1):
while cnt < 4:
	# Take screenshot using PyAutoGUI
	#img = pyautogui.screenshot()
    capture = pyautogui.screenshot('saved_'+str(cnt)+'.png')
	# Convert the screenshot to a numpy array
#	frame = np.array(img)
	# Convert it from BGR(Blue, Green, Red) to
	# RGB(Red, Green, Blue)
	#image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    capture = cv2.cvtColor(np.array(capture), cv2.COLOR_RGB2BGR)


	# Write it to the output file
##    ret, frame = cap.read()
##    image_rgb = fgbg.apply(frame)
##    cv2.imshow('frame',image_rgb)
    cv2.imshow("image",capture)
    #cv2.imwrite("frame" + str(cnt) + ".jpg", image_rgb)
    cv2.waitKey(0)
    cnt += 1
    #time.sleep(2)
    
	#out.write(frame)
	
	# Optional: Display the recording screen
	#cv2.imshow('Live', frame)
	
	# Stop recording when we press 'q'
	#if cv2.waitKey(1) == ord('q'):
	#	break
# Release the Video writer
#out.release()

# Destroy all windows
cv2.destroyAllWindows()
