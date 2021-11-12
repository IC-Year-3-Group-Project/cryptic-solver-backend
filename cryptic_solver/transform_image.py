import cv2
import imutils
import numpy as np

def detect_edges():

  image = cv2.imread("image4.jpg")

  # INCREASE THE CONTRAST
  #-----Converting image to LAB Color model----------------------------------- 
  lab= cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
  lab = imutils.resize(lab, height = 500)

  #-----Splitting the LAB image to different channels-------------------------
  l, a, b = cv2.split(lab)

  #-----Applying CLAHE to L-channel-------------------------------------------
  clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
  cl = clahe.apply(l)

  #-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
  limg = cv2.merge((cl,a,b))

  #-----Converting image from LAB Color model to RGB model--------------------
  final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
  final = imutils.resize(final, height = 500)

  ratio = image.shape[0] / 500.0
  orig = image.copy()
  image = imutils.resize(image, height = 500)

  gray = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (5, 5), 0)
  edged = cv2.Canny(gray, 75, 200)

  print("STEP 1: Edge Detection")
  cv2.imwrite("edged.png", edged)

  # find the contours in the edged image, keeping only the
  # largest ones, and initialize the screen contour
  cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
  print(len(cnts))
  # loop over the contours
  for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
    print(len(approx))
    if len(approx) == 4:
      screenCnt = approx
      break
  # show the contour (outline) of the piece of paper
  print("STEP 2: Find contours of paper")
  cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
  cv2.imwrite("out.png", image)

detect_edges()
