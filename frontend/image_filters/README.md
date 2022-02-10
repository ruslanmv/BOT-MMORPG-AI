# How to analyze  images from video-games  like Genshin Impact with OpenCV

Today we are going to study some filters that we will use to develop our Neural Network, in order to do that, first we need to understand how to work the single images.


The first step is load the needed libraries


```python
import io
import cv2
import numpy as np
from IPython.display import clear_output, Image, display
import PIL.Image
from matplotlib import pyplot as plt
from numpy import load
```

Let us define a function that can display the images in the notebook


```python
def showarray(a, fmt='jpeg'):
    a_n = np.uint8(np.clip(a, 0, 255))
    try :
        f = io.BytesIO()
        PIL.Image.fromarray(a_n).save(f, fmt)
        display(Image(data=f.getvalue()))
    except:
        #a = a[:, :, ::-1] # convert image from RGB (skimage) to BGR (opencv)
        # display image   
        plt.imshow(a)
        plt.show()  
```

### DAY WAY IDENTIFICATION


```python
# load array
img = cv2.imread('way-day.png',1)
```

The first image that we will use is the following


```python
showarray(img)
```


​    
![jpeg](output_9_0.jpg)
​    


## Simple threshold
 If the pixel value is less than the threshold value, set it to 0, otherwise set it to the maximum value.  The function used to set the threshold is the following:
### cv.threshold(img,parameter1,parameter2,cv.type)
 The first parameter is the gray level image of the source image, the second parameter is the threshold used to classify the pixel values, and the third parameter is the maximum value allocated to the pixel values beyond the threshold. 

 OpenCV provides different types of thresholds, which are given by the fourth parameter of the function.


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('way-day.png',1)
ret,thresh1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
ret,thresh2 = cv.threshold(img,127,255,cv.THRESH_BINARY_INV)
ret,thresh3 = cv.threshold(img,127,255,cv.THRESH_TRUNC)
ret,thresh4 = cv.threshold(img,127,255,cv.THRESH_TOZERO)
ret,thresh5 = cv.threshold(img,127,255,cv.THRESH_TOZERO_INV)
titles = ['Original Image','BINARY','BINARY_INV','TRUNC','TOZERO','TOZERO_INV']
images = [img, thresh1, thresh2, thresh3, thresh4, thresh5]
for i in range(6):
    plt.subplot(2,3,i+1),plt.imshow(images[i],'gray',vmin=0,vmax=255)
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.show()
```


​    
![png](output_11_0.png)
​    


## Adaptive threshold
If an image has different illumination conditions in different areas. In this case, the adaptive threshold can help, and the algorithm determines the threshold of the pixel according to the small area around the pixel. Therefore, for different regions of the same image, we get different thresholds, and for different illumination images, we get better results. In addition to the areas described above, cv.adaptiveThreshold The function also needs three other parameters.


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('way-day.png',1)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv.medianBlur(img,5)
ret,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,\
            cv.THRESH_BINARY,11,2)
th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,11,2)
titles = ['Original Image', 'Global Thresholding (v = 127)',
            'Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
images = [img, th1, th2, th3]
for i in range(4):
    plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.show()
```


​    
![png](output_13_0.png)
​    



```python
# load array
img = cv2.imread('way-day.png',1)
```

If we want to understad what is an image in terms of opencv, an image in opencv it is just a simple array, as you can see


```python
print(img)
```

    [[[124 193 150]
      [126 196 152]
      [128 195 153]
      ...
      [131 109  82]
      [128 104  76]
      [128 104  77]]
    
     [[145 198 166]
      [147 198 168]
      [149 198 168]
      ...
      [128 103  76]
      [126 101  72]
      [126 101  72]]
    
     [[154 199 173]
      [156 199 172]
      [160 199 175]
      ...
      [124  99  70]
      [124  98  68]
      [124  97  68]]
    
     ...
    
     [[161 212 222]
      [161 213 222]
      [160 212 221]
      ...
      [159 210 222]
      [159 209 222]
      [158 209 221]]
    
     [[158 211 222]
      [158 211 222]
      [160 211 222]
      ...
      [159 210 222]
      [160 210 223]
      [160 210 223]]
    
     [[158 211 221]
      [158 211 221]
      [159 212 222]
      ...
      [161 212 224]
      [160 211 224]
      [161 211 224]]]


## 1. Simple threshold

The first filter that we want to deal is the  Simple threshold


```python
def process_threshold(img):
    # Simple threshold
    ret, processed_img = cv.threshold(img,100,255,cv.THRESH_BINARY) #night/day
    return processed_img
pro_img = process_threshold(img)
showarray(pro_img)
```


​    
![jpeg](output_19_0.jpg)
​    


## 2. Median Blur

The second filter that we want to deal is the  median filter is used to suppress image noise.
The edge of the signal can be protected from blurring while noise is filtered out.


```python
def process_median(img):
    # Median filter is used to suppress image noise. 
    processed_img  = cv.medianBlur(img,9)
    return processed_img
pro_img = process_median(img)
showarray(pro_img)
```


​    
![jpeg](output_22_0.jpg)
​    


## 3. Edge detection

The third filter that we want to deal is the Edge detection


```python
def process_edge(img):
    # edge detection
    processed_img = cv2.Sobel(img,cv2.CV_64F,0 ,1, ksize=5) #Horizontal Gradient
    return processed_img
pro_img = process_edge(img)
showarray(pro_img)
```


​    
![jpeg](output_25_0.jpg)
​    


As you can see it a bit complex , how to identify a correct filter to get the appopiate filter.
In addition you can mix of different filters

## 4. Median Blur+ Threshold+ Edge detection(Sobel)


```python
def process_horizontal(img):
    # Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
    img = cv.medianBlur(img,9)
    # Simple threshold
    ret, frame = cv.threshold(img,100,255,cv.THRESH_BINARY) #night/day
    # edge detection
    processed_img = cv2.Sobel(frame,cv2.CV_64F,0 ,1, ksize=5) #Horizontal Gradient
    return processed_img
pro_img = process_horizontal(img)
showarray(pro_img)
```


​    
![jpeg](output_28_0.jpg)
​    


## 5. Median Blur+ Threshold+ Edge detection(Canny)


```python
def process_imagen(img):
    # Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
    img = cv.medianBlur(img,9)
    # Simple threshold
    ret, frame = cv.threshold(img,100,255,cv.THRESH_BINARY) #night/day
    # edge detection
    processed_img = cv2.Canny(frame, threshold1 = 200, threshold2=300)
    return processed_img
pro_img = process_imagen(img)
showarray(pro_img)
```


​    
![jpeg](output_30_0.jpg)
​    


## 6. Get the red source 


```python
def process_red(img):
    # Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
    img = cv.medianBlur(img,5)
    # Simple threshold
    #ret,th1 = cv.threshold(img,121,255,cv.THRESH_BINARY) #day
    #ret,th1 = cv.threshold(img,61,255,cv.THRESH_BINARY) #night
    ret,th1 = cv.threshold(img,100,255,cv.THRESH_BINARY) #night/day
    frame=th1
    y= cv2.Sobel(frame,cv2.CV_64F,0 ,1, ksize=5) #Horizontal Gradient
    #edge= cv2.Canny(frame, 100, 200)#Edge Detection
    src =y
    #print(src.shape)
    # extract red channel
    red_channel = src[:,:,2]
    # create empty image with same shape as that of src image
    red_img = np.zeros(src.shape)
    #assign the red channel of src to empty image
    red_img[:,:,2] = red_channel
    return red_img
red_img = process_red(img)
showarray(red_img)
```


​    
![jpeg](output_32_0.jpg)
​    


### 8. Find the best Thresholding parameter

As you could see there are some parameters that you have to add to the filter that you can identify by doing a loop
with different values of Thresholding paramter


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('day.png',0)
#img= cv.imread('night.png',1)
# convert to gray
#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
img = cv.medianBlur(img,5)
# Simple threshold
lst = [i for i in range(1,200+20,20)]
for x in lst:  
    ret,th1 = cv.threshold(img,x,255,cv.THRESH_BINARY)
    plt.imshow(th1,'gray')
    titles = ['Original Image', 'Global Thresholding v='+str(x)]
    images = [img, th1]
    for i in range(2):
        plt.subplot(1,2,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()
```


​    
![png](output_35_0.png)
​    




![png](output_35_1.png)
    




![png](output_35_2.png)
    




![png](output_35_3.png)
    




![png](output_35_4.png)
    




![png](output_35_5.png)
    




![png](output_35_6.png)
    




![png](output_35_7.png)
    




![png](output_35_8.png)
    




![png](output_35_9.png)
    




![png](output_35_10.png)
    


From the previous analysis we could identify that at v=200 you can identify the way of the game during the day


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
frame= cv.imread('way-day.png',1)
# Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
frame = cv.medianBlur(frame,5)
# Simple threshold
ret,frame = cv.threshold(frame,200,255,cv.THRESH_BINARY)
plt.imshow(frame,'gray')
```




    <matplotlib.image.AxesImage at 0x2bbbbff0c50>




​    
![png](output_37_1.png)
​    


As you see in the previous picture, the path is depicted with the cyan color.

We can test this output with different filters


```python
a= cv2.Laplacian(frame,cv2.CV_64F) #Laplacian
x= cv2.Sobel(frame,cv2.CV_64F,1 ,0, ksize=5)#Vertical Gradient
y= cv2.Sobel(frame,cv2.CV_64F,0 ,1, ksize=5) #Horizontal Gradient
edge= cv2.Canny(frame, 200, 200)#Edge Detection
showarray(a)
showarray(x)
showarray(y)
showarray(edge)
```


​    
![jpeg](output_40_0.jpg)
​    




![jpeg](output_40_1.jpg)
    




![jpeg](output_40_2.jpg)
    




![jpeg](output_40_3.jpg)
    


## NIGHT WAY IDENTIFICATION

For the night unfortunatelly the filters does not match as the day ones. So we need to find new parameters for the night.
At the end we should develop a function that find the best threshold parameter depending the weather conditions.


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from numpy import load
# load array
img = cv.imread('way-night.png',1)
```


```python
showarray(img)
```


​    
![jpeg](output_44_0.jpg)
​    


The first thing that want to do is identify the way where you are walking.
So first we need to identify it

## 9 K-means color quantization

Let is use a method to reduce the number of colors of the picture by using the color quantization procedure


```python
import cv2
import numpy as np
def kmeans_color_quantization(image, clusters=4, rounds=1):
    h, w = image.shape[:2]
    samples = np.zeros([h*w,3], dtype=np.float32)
    count = 0

    for x in range(h):
        for y in range(w):
            samples[count] = image[x][y]
            count += 1

    compactness, labels, centers = cv2.kmeans(samples,
            clusters, 
            None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001), 
            rounds, 
            cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    return res.reshape((image.shape))
```


```python
image = cv2.imread('way-night.png')
result = kmeans_color_quantization(image, clusters=4)
showarray(result)
#cv2.imshow('result', result)
#cv2.waitKey()
```


​    
![jpeg](output_49_0.jpg)
​    



```python
# declare lists
numbers = []
cubes = []
# start and end numbers
start = 1 
end = 10 
# run a loop from start to end+1 
for count in range (start, end+1) :
    numbers.append (count)
    cubes.append (count**3)
# print the lists
print("numbers: ",numbers)
print("cubes  : ",cubes)
```

    numbers:  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    cubes  :  [1, 8, 27, 64, 125, 216, 343, 512, 729, 1000]


## 9. Reduce color space

Let us consider reduction to 8 colors


```python
import numpy as np
import cv2 as cv
def is_cube(n):
    cbrt = np.cbrt(n)
    return cbrt ** 3 == n, int(cbrt)
def reduce_color_space(img, n_colors=8):
    n_valid, cbrt = is_cube(n_colors)
    if not n_valid:
        print("n_colors should be a perfect cube")
        return
    n_bits = int(np.log2(cbrt))
    if n_bits > 8:
        print("Can't generate more colors")
        return
    bitmask = int(f"{'1' * n_bits}{'0' * (8 - n_bits)}", 2)
    return img & bitmask
```


```python
img = cv.imread("way-night.png")
img_reduced=reduce_color_space(img)
showarray(img_reduced)
#cv.imshow("orig", img)
#cv.imshow("reduced", reduce_color_space(img))
#cv2.waitKey(0)
#cv2.destroyAllWindows()

```


​    
![jpeg](output_54_0.jpg)
​    


## 10.  Color reduction with sklearn


```python
# import the necessary packages
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import argparse
import cv2
```


```python
# load the image and grab its width and height
```


```python
image = cv2.imread('way-night.png')
#image = cv2.imread('way-day.png')
(h, w) = image.shape[:2]
```

 convert the image from the RGB color space to the L*a*b*
 color space -- since we will be clustering using k-means
 which is based on the euclidean distance, we'll use the
 L*a*b* color space where the euclidean distance implies
 perceptual meaning


```python

image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
```


```python
# reshape the image into a feature vector so that k-means
# can be applied
image = image.reshape((image.shape[0] * image.shape[1], 3))
```


```python
clusters=4
```


```python
# apply k-means using the specified number of clusters and
# then create the quantized image based on the predictions
clt = MiniBatchKMeans(n_clusters = clusters)
labels = clt.fit_predict(image)
quant = clt.cluster_centers_.astype("uint8")[labels]
```


```python
# reshape the feature vectors to images
quant = quant.reshape((h, w, 3))
image = image.reshape((h, w, 3))
```


```python
# convert from L*a*b* to RGB
quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
```


```python
showarray(np.hstack([image, quant]))
# display the images and wait for a keypress
#cv2.imshow("image", np.hstack([image, quant]))
#cv2.waitKey(0)
```


​    
![jpeg](output_66_0.jpg)
​    



```python
from skimage import io
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np
import time
import sys
```


```python
def _extract_features(img):
    h, w, ch = img.shape
    features = img.reshape((h*w, ch))
    return features
def _clusterize(colors, n_clusters):
    t = time.time()
    kmeans = MiniBatchKMeans(n_clusters=n_clusters,
                             random_state=0,
                             batch_size=2**12).fit(colors)
    print('Time to clusterize: {} s'.format(time.time() - t))

    return kmeans.labels_, kmeans.cluster_centers_
def _reduce_colors(output_shape, labels, labels_colors):
    out = np.zeros((labels.size, 3))
  
    for label, color in enumerate(labels_colors):
        out[labels == label] = color

    out = out.reshape(output_shape).astype(np.uint8)
    return out
```


```python
#img = io.imread(input_path).astype(np.float32)
img = cv2.imread('way-night.png')
colors = _extract_features(img)
```


```python
n_colors=3
```


```python
labels, labels_colors = _clusterize(colors, n_colors)
```

    Time to clusterize: 0.14699697494506836 s



```python
out = _reduce_colors(img.shape, labels, labels_colors)
```


```python
type(out) 
```




    numpy.ndarray




```python
showarray(out)
```


​    
![png](output_74_0.png)
​    



```python
from skimage import io
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np
import time
import sys
def _extract_features(img):
    h, w, ch = img.shape
    features = img.reshape((h*w, ch))
    return features
def _clusterize(colors, n_clusters):
    t = time.time()
    kmeans = MiniBatchKMeans(n_clusters=n_clusters,
                             random_state=0,
                             batch_size=2**12).fit(colors)
    print('Time to clusterize: {} s'.format(time.time() - t))

    return kmeans.labels_, kmeans.cluster_centers_
def _reduce_colors(output_shape, labels, labels_colors):
    out = np.zeros((labels.size, 3))
  
    for label, color in enumerate(labels_colors):
        out[labels == label] = color

    out = out.reshape(output_shape).astype(np.uint8)
    return out
def color_quantization(img, n_colors=3):
    colors = _extract_features(img)
    labels, labels_colors = _clusterize(colors, n_colors)
    out = _reduce_colors(img.shape, labels, labels_colors)
    return  out
```


```python
img = cv2.imread('way-night.png')
```


```python
img_quantized=color_quantization(img)
```

    Time to clusterize: 0.14100027084350586 s



```python
showarray(img_quantized)
```


​    
![png](output_78_0.png)
​    



```python
#cv2.imshow("Red Image", imm)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
```


```python
import cv2
import numpy as np
img = cv2.imread('way-night.png')
def process(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)
    img_blur = cv2.GaussianBlur(thresh, (5, 5), 2)
    img_canny = cv2.Canny(img_blur, 0, 0)
    return img_canny

def get_contours(img):
    contours, _ = cv2.findContours(process(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    r1, r2 = sorted(contours, key=cv2.contourArea)[-3:-1]
    x, y, w, h = cv2.boundingRect(np.r_[r1, r2])
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
```


```python
get_contours(img)
#cv2.imshow("img_processed", img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
```


```python
import cv2
def process(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 163, 255, cv2.THRESH_BINARY)
    img_canny = cv2.Canny(thresh, 0, 0)
    img_dilate = cv2.dilate(img_canny, None, iterations=7)
    return cv2.erode(img_dilate, None, iterations=7)

def get_contours(img):
    contours, _ = cv2.findContours(process(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)


```


```python
img = cv2.imread('way-night.png')
get_contours(img)
#cv2.imshow("img_processed", img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
showarray(img)
```


​    
![png](output_83_0.png)
​    



```python
def process_horizontal(img):
    # Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
    #img = cv2.medianBlur(img,1)
    # Simple threshold
    ret, frame = cv2.threshold(img,100,100,cv2.THRESH_BINARY) #night/day
    # edge detection
    processed_img = cv2.Sobel(frame,cv2.CV_64F,0 ,1, ksize=5) #Horizontal Gradient
    return processed_img
img = cv2.imread('way-night.png')

pro_img = process_horizontal(img)
#cv2.imshow("img_processed", pro_img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
showarray(pro_img)
```

    Clipping input data to the valid range for imshow with RGB data ([0..1] for floats or [0..255] for integers).




![png](output_84_1.png)
    



```python
import cv2
# read the image
image = cv2.imread('way-day.png')
# B, G, R channel splitting
blue, green, red = cv2.split(image)
# detect contours using blue channel and without thresholding
contours1, hierarchy1 = cv2.findContours(image=blue, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
# draw contours on the original image
image_contour_blue = image.copy()
cv2.drawContours(image=image_contour_blue, contours=contours1, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
# see the results
print('Contour detection using blue channels only')
showarray(image_contour_blue)
#cv2.imshow('Contour detection using blue channels only', image_contour_blue)
#cv2.waitKey(0)
#cv2.imwrite('blue_channel.jpg', image_contour_blue)
#cv2.destroyAllWindows()
# detect contours using green channel and without thresholding
contours2, hierarchy2 = cv2.findContours(image=green, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
# draw contours on the original image
image_contour_green = image.copy()
cv2.drawContours(image=image_contour_green, contours=contours2, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
# see the results
print('Contour detection using green channels only')
showarray(image_contour_green)
#cv2.imshow('Contour detection using green channels only', image_contour_green)
#cv2.waitKey(0)
#cv2.imwrite('green_channel.jpg', image_contour_green)
#cv2.destroyAllWindows()
# detect contours using red channel and without thresholding
contours3, hierarchy3 = cv2.findContours(image=red, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
# draw contours on the original image
image_contour_red = image.copy()
cv2.drawContours(image=image_contour_red, contours=contours3, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
# see the results
print('Contour detection using red channels only')
#cv2.imshow('Contour detection using red channels only', image_contour_red)
#cv2.waitKey(0)
#cv2.imwrite('red_channel.jpg', image_contour_red)
#cv2.destroyAllWindows()
showarray(image_contour_red)
```

    Contour detection using blue channels only




![png](output_85_1.png)
    


    Contour detection using green channels only




![png](output_85_3.png)
    


    Contour detection using red channels only




![png](output_85_5.png)
    



```python
# to actually visualize the effect of `CHAIN_APPROX_SIMPLE`, we need a proper image
# read the image
image1 = cv2.imread('way-night.png')
img_gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

ret, thresh1 = cv2.threshold(img_gray1, 150, 255, cv2.THRESH_BINARY)
contours2, hierarchy2 = cv2.findContours(thresh1, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
image_copy2 = image1.copy()
cv2.drawContours(image_copy2, contours2, -1, (0, 255, 0), 2, cv2.LINE_AA)
#IMPLE Approximation contours
showarray(image_copy2)
#cv2.imshow('SIMPLE Approximation contours', image_copy2)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
image_copy3 = image1.copy()
for i, contour in enumerate(contours2): # loop over one contour area
       for j, contour_point in enumerate(contour): # loop over the points
           # draw a circle on the current contour coordinate
            cv2.circle(image_copy3, ((contour_point[0][0], contour_point[0][1])), 2, (0, 255, 0), 2, cv2.LINE_AA)
showarray(image_copy3)
```


​    
![png](output_86_0.png)
​    




![png](output_86_1.png)
    



```python
# see the results
print('CHAIN_APPROX_SIMPLE Point only')
showarray(image_copy3)
#cv2.imshow('CHAIN_APPROX_SIMPLE Point only', image_copy3)
#cv2.waitKey(0)
#cv2.imwrite('contour_point_simple.jpg', image_copy3)
#cv2.destroyAllWindows()
```

    CHAIN_APPROX_SIMPLE Point only




![png](output_87_1.png)
    



```python
def contour_search(image1):
    img_gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(img_gray1, 100, 255, cv2.THRESH_BINARY)
    contours2, hierarchy2 = cv2.findContours(thresh1, cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)
    image_copy2 = image1.copy()
    cv2.drawContours(image_copy2, contours2, -1, (0, 255, 0), 2, cv2.LINE_AA)
    return image_copy2
   
```


```python
image_copy2=contour_search(image1)
print('SIMPLE Approximation contours')
showarray(image_copy2)
#cv2.imshow('SIMPLE Approximation contours', image_copy2)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
```

    SIMPLE Approximation contours




![png](output_89_1.png)
    



```python
def contour_find(image1,parameter1, parameter2):
    img_gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(img_gray1, parameter1, parameter2, cv2.THRESH_BINARY)
    contours2, hierarchy2 = cv2.findContours(thresh1, cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)
    image_copy2 = image1.copy()
    cv2.drawContours(image_copy2, contours2, -1, (0, 255, 0), 2, cv2.LINE_AA)
    return image_copy2
```


```python
image1 = cv2.imread('way-day.png')
# Median filter is used to suppress image noise. The edge of the signal can be protected from blurring while noise is filtered out.
image1 = cv.medianBlur(image1,5)
image_copy2=contour_find(image1,100,255)

print('SIMPLE Approximation contours')
showarray(image_copy2)
#cv2.imshow('SIMPLE Approximation contours', image_copy2)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
```

    SIMPLE Approximation contours




![png](output_91_1.png)
    



```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
# Simple threshold
lst = [i for i in range(50,150+1,5)]
img1 = cv2.imread('way-night.png')
for x in lst: 
    th1=contour_find(image1,x,255)
    plt.imshow(th1,'gray')
    titles = ['Original Image', 'Thresholding 1='+str(x)]
    images = [img, th1]
    for i in range(2):
        plt.subplot(1,2,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()
```


​    
![png](output_92_0.png)
​    




![png](output_92_1.png)
    




![png](output_92_2.png)
    




![png](output_92_3.png)
    




![png](output_92_4.png)
    




![png](output_92_5.png)
    




![png](output_92_6.png)
    




![png](output_92_7.png)
    




![png](output_92_8.png)
    




![png](output_92_9.png)
    




![png](output_92_10.png)
    




![png](output_92_11.png)
    




![png](output_92_12.png)
    




![png](output_92_13.png)
    




![png](output_92_14.png)
    




![png](output_92_15.png)
    




![png](output_92_16.png)
    




![png](output_92_17.png)
    




![png](output_92_18.png)
    




![png](output_92_19.png)
    




![png](output_92_20.png)
    



```python
import cv2

image = cv2.imread('way-day.png')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray,200, 255,cv2.THRESH_BINARY_INV)[1]
cnts, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

label = '1'
count = 0

# Get inner list of hierarchy
for layer in zip(cnts, h[0]):
    contour = layer[0]
    hierarchy = layer[1]

    # If we find new contour (not inner) reset label
    if hierarchy[1] >= 0:
        label = '1'
    # Ensure that we only have outer contour
    if count % 2 == 0:
        cv2.drawContours(image, [contour], -1, (36, 255, 12), 2)
        x,y,w,h = cv2.boundingRect(contour)
        cv2.putText(image, label, (x +50,y+ 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36,255,12), 3)
        label = str(int(label) * -1)

    count += 1

print('thresh')
showarray(thresh)
print('image')
showarray(image)   
#cv2.imshow('thresh', thresh)
#cv2.imshow('image', image)
#cv2.waitKey()
#cv2.destroyAllWindows()
```

    thresh




![png](output_93_1.png)
    


    image




![png](output_93_3.png)
    



```python
import cv2
image = cv2.imread('way-night.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray,90, 255,cv2.THRESH_BINARY_INV)[1]
cnts, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
label = '1'
count = 0
# Get inner list of hierarchy
for layer in zip(cnts, h[0]):
    contour = layer[0]
    hierarchy = layer[1]

    # If we find new contour (not inner) reset label
    if hierarchy[1] >= 0:
        label = '1'
    # Ensure that we only have outer contour
    if count % 2 == 0:
        cv2.drawContours(image, [contour], -1, (36, 255, 12), 2)
        x,y,w,h = cv2.boundingRect(contour)
        cv2.putText(image, label, (x +50,y+ 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36,255,12), 3)
        label = str(int(label) * -1)

    count += 1

print('thresh')
showarray(thresh)
print('image')
showarray(image)  
#cv2.imshow('thresh', thresh)
#cv2.imshow('image', image)
#cv2.waitKey()
#cv2.destroyAllWindows()
```

    thresh




![png](output_94_1.png)
    


    image




![png](output_94_3.png)
    


### Analisis of the day


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
#img = cv.imread('noisy2.png',0)
#img = load('data.npy') #Original
img = cv2.imread('way-day.png')
#img = cv2.imread('way-night.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# global thresholding
#ret1,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
ret1,th1 = cv.threshold(img,200,255,cv.THRESH_BINARY) # day
#ret1,th1 = cv.threshold(img,90,255,cv.THRESH_BINARY) # night
# Otsu's thresholding
ret2,th2 = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# Otsu's thresholding after Gaussian filtering
blur = cv.GaussianBlur(img,(5,5),0)
# The threshold must be set to 0.
ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# plot all the images and their histograms
images = [img, 0, th1,
          img, 0, th2,
          blur, 0, th3]
titles = ['Original Noisy Image','Histogram','Global Thresholding (v=200)',
          'Original Noisy Image','Histogram',"Otsu's Thresholding",
          'Gaussian filtered Image','Histogram',"Otsu's Thresholding"]

```

## Filter of Day v=200 with Day Image


```python
for i in range(3):
    plt.subplot(3,3,i*3+1),plt.imshow(images[i*3],'gray')
    plt.title(titles[i*3]), plt.xticks([]), plt.yticks([])
    plt.subplot(3,3,i*3+2),plt.hist(images[i*3].ravel(),256)
    plt.title(titles[i*3+1]), plt.xticks([]), plt.yticks([])
    plt.subplot(3,3,i*3+3),plt.imshow(images[i*3+2],'gray')
    plt.title(titles[i*3+2]), plt.xticks([]), plt.yticks([])
```


​    
![png](output_98_0.png)
​    



```python
#plt.hist(images[3].ravel(),256)
```


```python
for i in range(1):
    plt.hist(images[3].ravel(),256)

```


​    
![png](output_100_0.png)
​    



```python
len(images[3].ravel())
```




    2073600




```python
showarray(images[3])
```


​    
![png](output_102_0.png)
​    



```python
images[3]
```




    array([[172, 175, 175, ..., 103,  98,  99],
           [182, 183, 183, ...,  98,  95,  95],
           [186, 186, 187, ...,  93,  92,  91],
           ...,
           [209, 210, 209, ..., 208, 207, 207],
           [208, 208, 208, ..., 208, 208, 208],
           [208, 208, 209, ..., 210, 209, 209]], dtype=uint8)




```python
plt.hist(images[3].ravel())
```




    (array([  2439.,  18295.,  60282., 164733., 100166.,  88087., 455993.,
            488123., 668348.,  27134.]),
     array([  1. ,  26.4,  51.8,  77.2, 102.6, 128. , 153.4, 178.8, 204.2,
            229.6, 255. ]),
     <BarContainer object of 10 artists>)




​    
![png](output_104_1.png)
​    


### Analisis of the night


```python
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
#img = cv.imread('noisy2.png',0)
#img = load('data.npy') #Original
#img = cv2.imread('way-day.png')
img = cv2.imread('way-night.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# global thresholding
#ret1,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
#ret1,th1 = cv.threshold(img,200,255,cv.THRESH_BINARY) # day
ret1,th1 = cv.threshold(img,90,255,cv.THRESH_BINARY) # night
# Otsu's thresholding
ret2,th2 = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# Otsu's thresholding after Gaussian filtering
blur = cv.GaussianBlur(img,(5,5),0)
# The threshold must be set to 0.
ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# plot all the images and their histograms
images = [img, 0, th1,
          img, 0, th2,
          blur, 0, th3]
titles = ['Original Noisy Image','Histogram','Global Thresholding (v=90)',
          'Original Noisy Image','Histogram',"Otsu's Thresholding",
          'Gaussian filtered Image','Histogram',"Otsu's Thresholding"]

```

## Filter of Night v=90 with Night Image


```python
for i in range(3):
    plt.subplot(3,3,i*3+1),plt.imshow(images[i*3],'gray')
    plt.title(titles[i*3]), plt.xticks([]), plt.yticks([])
    plt.subplot(3,3,i*3+2),plt.hist(images[i*3].ravel(),256)
    plt.title(titles[i*3+1]), plt.xticks([]), plt.yticks([])
    plt.subplot(3,3,i*3+3),plt.imshow(images[i*3+2],'gray')
    plt.title(titles[i*3+2]), plt.xticks([]), plt.yticks([])
plt.show()
```


​    
![png](output_108_0.png)
​    


# Analisis of the Picture

## Spectrum Analisis


```python
img = cv2.imread('way-day.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
oned=img.ravel()
for i in range(1):
    plt.hist(oned,256)
```


​    
![png](output_111_0.png)
​    



```python
plt.hist(oned)
```




    (array([  2439.,  18295.,  60282., 164733., 100166.,  88087., 455993.,
            488123., 668348.,  27134.]),
     array([  1. ,  26.4,  51.8,  77.2, 102.6, 128. , 153.4, 178.8, 204.2,
            229.6, 255. ]),
     <BarContainer object of 10 artists>)




​    
![png](output_112_1.png)
​    



```python
y, x, _ = plt.hist(oned)
```


​    
![png](output_113_0.png)
​    



```python
print(x.max())
print(y.max())
```

    255.0
    668348.0



```python
from matplotlib import pyplot as plt
```


```python
img = cv2.imread('way-day.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
oned=img.ravel()
y, x, _ = plt.hist(oned)
print(x.max())
print(y.max())
```

    255.0
    668348.0




![png](output_116_1.png)
    



```python
import numpy as np
img = cv2.imread('way-day.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
oned=img.ravel()
histog=np.histogram(oned)
y, x = histog[0],histog[1]
# Get the maximum element from a Numpy array
y_max = np.amax(y)
print('Y Max element from Numpy Array : ', y_max )
# Get the indices of maximum element in numpy array
result = np.where(y == np.amax(y))
print('Returned tuple of arrays :', result)
print('List of Indices of maximum element :', result[0])
position_max=result[0].item()
x_max=x[position_max]
print('x Max element from Numpy Array : ', x_max )
print('Max point (x_max,y_max) = (',  x_max ,',' ,y_max,')'  )
```

    Y Max element from Numpy Array :  668348
    Returned tuple of arrays : (array([8], dtype=int64),)
    List of Indices of maximum element : [8]
    x Max element from Numpy Array :  204.2
    Max point (x_max,y_max) = ( 204.2 , 668348 )



```python
img = cv2.imread('way-night.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
oned=img.ravel()
y, x, _ = plt.hist(oned)
print(x.max())
print(y.max())
```

    255.0
    1258968.0




![png](output_118_1.png)
    



```python
import numpy as np
img = cv2.imread('way-night.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
oned=img.ravel()
histog=np.histogram(oned)
y, x = histog[0],histog[1]
# Get the maximum element from a Numpy array
y_max = np.amax(y)
print('Y Max element from Numpy Array : ', y_max )
# Get the indices of maximum element in numpy array
result = np.where(y == np.amax(y))
print('Returned tuple of arrays :', result)
print('List of Indices of maximum element :', result[0])
position_max=result[0].item()
x_max=x[position_max]
print('x Max element from Numpy Array : ', x_max )
print('Max point (x_max,y_max) = (',  x_max ,',' ,y_max,')'  )
```

    Y Max element from Numpy Array :  1258968
    Returned tuple of arrays : (array([3], dtype=int64),)
    List of Indices of maximum element : [3]
    x Max element from Numpy Array :  77.19999999999999
    Max point (x_max,y_max) = ( 77.19999999999999 , 1258968 )



```python
point1 = [77.19, 90]
point2 = [204.2, 200]
x_values = [point1[0], point2[0]]
#gather x-values
y_values = [point1[1], point2[1]]
#gather y-values
plt.plot(x_values, y_values)
```




    [<matplotlib.lines.Line2D at 0x2bb84864048>]




​    
![png](output_120_1.png)
​    



```python
from numpy import ones,vstack
from numpy.linalg import lstsq
points = [(77.19, 90),(204.2, 200)]
x_coords, y_coords = zip(*points)
A = vstack([x_coords,ones(len(x_coords))]).T
m, c = lstsq(A, y_coords)[0]
print("Line Solution is y = {m}x + {c}".format(m=m,c=c))
```

    Line Solution is y = 0.8660735375167304x + 23.147783639083652


    C:\Anaconda3\envs\pygta5\lib\site-packages\ipykernel_launcher.py:6: FutureWarning: `rcond` parameter will change to the default of machine precision times ``max(M, N)`` where M and N are the input matrix dimensions.
    To use the future default and silence this warning we advise to pass `rcond=None`, to keep using the old, explicitly pass `rcond=-1`.


​    


```python
import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(0,200,100)
y = 0.8660735375167304*x + 23.147783639083652
plt.plot(x, y, '-r', label='y = 0.86x + 23.14')
plt.title('Graph of y = 0.86x + 23.14')
plt.xlabel('x', color='#1C2833')
plt.ylabel('y', color='#1C2833')
plt.legend(loc='upper left')
plt.grid()
plt.show()
```


​    
![png](output_122_0.png)
​    


# Filter function 

Now that we have identifed which is the function than can optimize the filter parameter we define it


```python
def parmeterv(x):
    y= 0.8660735375167304*x + 23.147783639083652
    return y
```


```python
def parameter(img):
    #img = cv2.imread('way-night.png')
    #img = cv2.imread('way-day.png')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    oned=img.ravel()
    #y, x, _ = plt.hist(oned)
    histog=np.histogram(oned)
    y, x = histog[0],histog[1]
    # Get the maximum element from a Numpy array
    y_max = np.amax(y)
    # Get the indices of maximum element in numpy array
    result = np.where(y == np.amax(y))
    position_max=result[0].item()
    x_max=x[position_max]
    #print(x_max)
    intensity = parmeterv(x_max)
    return  intensity
```

We check if the it is provided the correct parameters


```python
# For the day should be v=200
img = cv2.imread('way-day.png')
parameter(img)
```




    200.0




```python
# For the nigth should be v=90
img = cv2.imread('way-night.png')
parameter(img)
```




    90.00866073537523




```python
def process_black_contour(img):
    image = img
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)   
    #thresh = cv2.threshold(gray,90, 255,cv2.THRESH_BINARY_INV)[1] # only for night
    #thresh = cv2.threshold(gray,200, 255,cv2.THRESH_BINARY_INV)[1] # only for day  
    intensity=parameter(image)
    thresh = cv2.threshold(gray,intensity, 255,cv2.THRESH_BINARY_INV)[1] # any time or weather
    cnts, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    label = '1'
    count = 0
    # Get inner list of hierarchy
    for layer in zip(cnts, h[0]):
        contour = layer[0]
        hierarchy = layer[1]
        # If we find new contour (not inner) reset label
        if hierarchy[1] >= 0:
            label = '1'
        # Ensure that we only have outer contour
        if count % 2 == 0:
            cv2.drawContours(image, [contour], -1, (36, 255, 12), 2)
            x,y,w,h = cv2.boundingRect(contour)
            cv2.putText(image, label, (x +50,y+ 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36,255,12), 3)
            label = str(int(label) * -1)
        count += 1
    return thresh
```

### For the day we identify the way


```python
img = cv2.imread('way-day.png')
img_prepro_day=process_black_contour(img)
showarray(img_prepro_day)
```


​    
![png](output_132_0.png)
​    


### For the night we identify the way


```python
img = cv2.imread('way-night.png')
img_prepro_night=process_black_contour(img)
showarray(img_prepro_night)
```


​    
![png](output_134_0.png)
​    



```python
#cv2.imshow('Day', img_prepro_day)
#cv2.imshow('Night', img_prepro_night)
#cv2.waitKey()
#cv2.destroyAllWindows()
```

We can use this latest filters to start develop our ML models.
