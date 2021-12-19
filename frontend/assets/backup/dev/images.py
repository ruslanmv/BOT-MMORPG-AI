import time
import cv2
import mss
import numpy

frame = 1
with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {'top': 40, 'left': 0, 'width': 800, 'height': 640}

    while 'Screen capturing':
        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        img = numpy.array(sct.grab(monitor))

        # Display the picture
        frame += 1    
        name = './imgs/img' + str(frame) + '.png'
        cv2.imwrite(name, img)
        
        # Stop recording when we press 'q'
        if cv2.waitKey(1) == ord('q'):
            break

#        if cv2.waitKey(25) & 0xFF == ord('q'):
#            cv2.destroyAllWindows()
#            break