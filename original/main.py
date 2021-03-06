import cv2
import numpy as np
import pdb
import serial
import picamera
import picamera.array

import time
    
print('start')
time.sleep(3)

ser = serial.Serial("/dev/ttyACM0", 9600)
if ser is None:
  ser = serial.Serial("/dev/ttyACM1", 9600)

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
zf = 0.2
camera.zoom = (0+zf, 0+zf, 1-2*zf, 1-2*zf)
rawCapture = picamera.array.PiRGBArray(camera, size = (640, 480))
time.sleep (0.1)
for frame in camera.capture_continuous (rawCapture, format = "bgr", use_video_port = True):
    image = frame.array
    image = cv2.resize(image,(640,480))
    # Convert to grayscale
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Gussian blur
    blurred = cv2.GaussianBlur(imgray, (5, 5), 0)
 
    # Color thresholding
    ret,thresh = cv2.threshold(blurred,60,255,cv2.THRESH_BINARY_INV)

    # Find the contours of the frame
    contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

    # Find the biggest contour (if detected)
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        cv2.line(image,(cx,0),(cx,720),(255,0,0),1)
        cv2.line(image,(0,cy),(1280,cy),(255,0,0),1)
        cv2.drawContours(image, contours, -1, (0,255,0), 1)

        print (cx)
        print (cy)

        # 좌회전
        if cx >= 1100:
          ser.write(chr(4).encode())
          print ("Turn Left!")
        # 직진
        if cx < 1100 and cx > 800:
          ser.write(chr(3).encode())
          print ("On Track!")
        # 우회전
        if cx <= 800:
          ser.write(chr(1).encode())
          print ("Turn Right!")
    # 후진
    else:
      ser.write(chr(2).encode())
      print("Reverse")


    #Display the resulting frame
    cv2.imshow('frame',image)
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      print("Stopped!")
      break

# Closes all the frames
cv2.destroyAllWindows()