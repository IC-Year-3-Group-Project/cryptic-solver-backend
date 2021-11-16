import cv2
import imutils
import numpy as np
import PIL.Image
import pytesseract
import re
# pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
# !!! Tesseract command different on every machine

def black_treshold(r, g, b):
    return r < 100 and g < 100 and b < 100

def thicken_black_contours(cv2_img):
    '''
    Makes the black lines in the image thicker so that
    they could be more easily recognized.

    Parameters: 
    image_path: The string path of the image

    Return:
    img2: Image with thickened black contours
    '''
 
    # Load the image and a copy of it to modify as a PIL images
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    img = PIL.Image.fromarray(cv2_img)
    img2 = PIL.Image.fromarray(cv2_img)
    width, height = img.size
    pix = img.load()
    pix2 = img2.load()


    # Change the neighbourhood pixels of the black pixels to
    # black where there is threshold for classifying as black
    for x in range(5, width - 5):
        for y in range(5, height - 5):
            (r, g, b) = pix[x, y]
            if black_treshold(r, g, b):
                pix2[x, y] = (0, 0, 0)
                for i in range(5):
                    for j in range(5):
                        pix2[x+i, y+j] = (0, 0, 0)

    # Change the non-black pixels to white where there is
    # threshold for classifying as black
    for x in range(width):
        for y in range(height):
            (r, g, b) = pix2[x, y]
            if not black_treshold(r, g, b):
                pix2[x, y] = (255, 255, 255)

    img2.save("out/black.png")
    return img2


def transform_to_cornersangle(image, points):
    '''
    Transforms the image to a rectangle with sides parallel
    and perpendicular to the horizontal

    Parameters: 
    image: Image data array
    points: 4x2 array that contains the coordinates of the
           corners of the tilted grid

    Return:
    img2: Image with thickened black contours
    '''

    # Get the array of 4 corners of the grid and move a bit towards
    # the corners of the whole image to allow for some white space
    # around the image after cropping
    corners = np.array([points[0][0], points[3][0], points[2]
                       [0], points[1][0]], dtype="float32")

    corners[0][0] -= 50
    corners[0][1] -= 50

    corners[1][0] += 50
    corners[1][1] -= 50

    corners[2][0] += 50
    corners[2][1] += 50

    corners[3][0] -= 50
    corners[3][1] += 50

    (tl, tr, br, bl) = corners

    # Use the Pythagorean Theorem to find the approximate sides of the
    # tilted grid so that we can use them later to keep the same size
    right_height = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    left_height = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    height = max(int(right_height), int(left_height))

    bottom_width = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    top_width = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    width = max(int(bottom_width), int(top_width))

    # Construct an array with the expected corners of the non-tilted image
    dst_corners = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1],
                            [0, height - 1]], dtype="float32")

    transform_matrix = cv2.getPerspectiveTransform(corners, dst_corners)
    rectangular_image = cv2.warpPerspective(
        image, transform_matrix, (width, height))

    return rectangular_image


def process_grid_image(cv2_img):
    '''
    Detects the corners of the grid and rotates it to a rectangle 
    with sides parallel and perpendicular to the horizontal

    Parameters: 
    path: The path tho the image

    Return:
    rectangular_image: The image with non-tilted grid inside
    '''

    pil_image = thicken_black_contours(cv2_img)
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # We need to resize the image to be able to find the contours
    # so we need to save the original one and how we resized
    resize_height = 500
    original_image = image.copy()
    image = imutils.resize(image, height=resize_height)

    # Turn to grayscale and perform Gaussian blur to find the
    # edges in the grid more easily
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)

    cv2.imwrite("out/edged.png", edged)

    # Find the contours and extract the 5 longest contours
    contours = cv2.findContours(
        edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    # Go through the longest contours and if the current one
    # has detectable 4 corners of a rectangle, then use it
    for c in contours:
        contour_length = cv2.arcLength(c, True)
        approx_corners = cv2.approxPolyDP(c, 0.04 * contour_length, True)
        if len(approx_corners) == 4:
            corners = approx_corners
            break

    cv2.drawContours(image, [corners], -1, (0, 255, 0), 2)
    cv2.imwrite("out/out.png", image)

    corner_points = corners * \
        np.shape(original_image)[0] / (1.0 * resize_height)
    rectangular_image = transform_to_cornersangle(
        original_image, corner_points)
    cv2.imwrite("out/warped.png", rectangular_image)

    return rectangular_image

# Takes a cv2 image
def transform_text_image(image):
    print(pytesseract.image_to_osd(image))
    angle = 360 - int(re.search('(?<=Rotate: )\d+', pytesseract.image_to_osd(image)).group(0))
    height, width = image.shape[:2]

    # Perform the rotation
    M = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (width, height))
    
    cv2.imwrite("out/rotated.png", rotated)
    return rotated



