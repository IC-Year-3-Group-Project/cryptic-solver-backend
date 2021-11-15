import cv2
import imutils
import numpy as np

import PIL.Image

def thicken_black_contours(image_path):

  img = PIL.Image.open(image_path) 
  img2 = PIL.Image.open(image_path) 
  width, height = img.size
  pix = img.load()
  pix2 = img2.load()

  for x in range(5, width - 5):
    for y in range(5, height - 5):
        (r,g,b) = pix[x,y]
        if r < 100 and g < 100 and b < 100:
            pix2[x,y] = (0, 0, 0)
            for i in range(5):
                for j in range(5):
                    pix2[x+i, y+j] = (0, 0, 0)

  for x in range(width):
    for y in range(height):
        (r,g,b) = pix2[x,y]
        if r >= 100 or g >= 100 or b >= 100:
            pix2[x,y] = (255,255,255)

  img2.save("out/black.png")
  return img2


def transform_to_cornersangle(image, pts):
  corners = np.array([pts[0][0], pts[3][0], pts[2][0], pts[1][0]], dtype="float32")

  corners[0][0] -= 50
  corners[0][1] -= 50

  corners[1][0] += 50
  corners[1][1] -= 50

  corners[2][0] += 50
  corners[2][1] += 50

  corners[3][0] -= 50
  corners[3][1] += 50

  (tl, tr, br, bl) = corners

  widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
  widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
  maxWidth = max(int(widthA), int(widthB))

  heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
  heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
  maxHeight = max(int(heightA), int(heightB))

  dst = np.array([
    	[0, 0],
    	[maxWidth - 1, 0],
    	[maxWidth - 1, maxHeight - 1],
    	[0, maxHeight - 1]], dtype = "float32")

  M = cv2.getPerspectiveTransform(corners, dst)
  warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

  return warped

def detect_edges(path):

  pil_image = thicken_black_contours(path)
  image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

  ratio = image.shape[0] / 500.0
  original_image = image.copy()
  image = imutils.resize(image, height = 500)

  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  gray = cv2.GaussianBlur(gray, (5, 5), 0)
  edged = cv2.Canny(gray, 75, 200)

  cv2.imwrite("out/edged.png", edged)

  cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

  cnts = imutils.grab_contours(cnts)
  cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

  for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
    if len(approx) == 4:
      screenCnt = approx
      break

  cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
  cv2.imwrite("out/out.png", image)

  warped = transform_to_cornersangle(original_image, screenCnt * ratio)
  cv2.imwrite("out/warped.png", warped)


detect_edges('out/IMG_0146 (1).png')
