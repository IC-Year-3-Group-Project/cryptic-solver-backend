import pytesseract
import cv2

if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    img = cv2.imread("../everyman 3907 clues.PNG")

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)

    print(text)