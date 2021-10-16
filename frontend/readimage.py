import cv2
 
image = cv2.imread('C:/Users/N/Desktop/Test.jpg')
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
cv2.imwrite('C:/Users/N/Desktop/Test_gray.jpg', image_gray)