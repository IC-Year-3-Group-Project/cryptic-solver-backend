import easyocr
import pytesseract
import cv2
import re
import numpy as np
import pandas as pd
from functools import reduce
from cryptic_solver.image_processing.transform_image import transform_text_image
# from cryptic_solver_project import settings

# if settings.tesseract_cmd != "":
#     pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

reader = easyocr.Reader(['en'])

def preprocess_original(image):
    image = get_grayscale(image)
    cv2.imwrite('thresh.png', image)
    return image


def preprocess(image):
    gray = get_grayscale(image)
    blurred = remove_noise(gray)
    # image = adaptive_thresholding(image)
    thresh = thresholding(blurred)
    # image = distance_transform(image)

    cv2.imwrite('gray.png', gray)
    cv2.imwrite('blurred.png', blurred)
    cv2.imwrite('thresh.png', thresh)

    image = thresh
    return image


def postprocess_text(text):
    '''
    Changes the misrecognized characters to the expected ones

    Parameters: 
    text: String

    Return:
    replaced_text: String
    '''
    character_replacements = {
        "°": " ",
        "©": "(5)",
        "|": "I",
        "®": "(5",
        "@": "(4)",
    }

    replaced_text = text
    for (k, r) in character_replacements.items():
        replaced_text = replaced_text.replace(k, r)

    # Take care of cases where the lengths of a two-word clue have been stuck together
    for i in range(len(replaced_text)-2):
        if replaced_text[i] == "(" and \
           replaced_text[i + 1] > "1" and \
           replaced_text[i + 1] <= "9" and \
           replaced_text[i + 2] >= "1" and \
           replaced_text[i + 2] <= "9":
            replaced_text = replaced_text[:i + 2] + "," + replaced_text[i + 2:]

    return replaced_text


def distance_transform(image):
    "distance transform"
    return cv2.distanceTransform(image, cv2.DIST_L2, 5)


def adaptive_thresholding(image):
    "thresholding"
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 71, 6)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def remove_noise(image):
    "noise removal"
    image = cv2.GaussianBlur(image, (5, 5), 0)
    # image = cv2.medianBlur(image, 9)
    return cv2.bilateralFilter(image, 9, 65, 75)


def get_grayscale(image):
    "get grayscale image"
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def make_text(a, b):
    if (a[len(a)-1] == ')'):
        return a + '\n\n' + b
    return a + ' ' + b


def read_text_new(image_data, ocr):
    processed = preprocess(image_data)

    # print(pytesseract.image_to_data(processed, config=custom_config))
    # print(reader.readtext(processed)[-2:-1])

    if ocr == "tesseract":
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(processed, config=custom_config)
    elif ocr == "easy_ocr":
        text = reader.readtext(processed, detail=0)
        text = reduce(make_text, text)

    text = pytesseract.image_to_data(
        processed, config=custom_config, output_type='data.frame')
    text = [tuple(x) for x in text[text.conf != -1]
            [['conf', 'text']].to_numpy()]
    # lines = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'] \
    #                                     .apply(lambda x: ' '.join(list(x))).tolist()
    # confs = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['conf'].mean().tolist()
    # line_conf = []
    # for i in range(len(lines)):
    #     if lines[i].strip():
    #         line_conf.append((lines[i], round(confs[i],3)))
    # print("Lines")
    # for i in line_conf:
    #     print(i)
    print(text)

    text = pytesseract.image_to_string(processed, config=custom_config)
    preprocessed_text = postprocess_text(text)
    clues = parse_ocr(preprocessed_text)
    return clues


def read_text_original(image_data):

    processed = preprocess_original(image_data)

    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_data(
        processed, config=custom_config, output_type='data.frame')

    text = text[text.conf > 0]
    lines = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])['text'] \
        .apply(lambda x: ' '.join(list(x))).tolist()
    confs = text.groupby(['page_num', 'block_num', 'par_num', 'line_num'])[
        'conf'].mean().tolist()
    line_conf = []
    for i in range(len(lines)):
        if lines[i].strip():
            line_conf.append((lines[i], round(confs[i], 3)))
    print("Lines")
    for i in line_conf:
        print(i)

    text = pytesseract.image_to_string(processed, config=custom_config)
    preprocessed_text = postprocess_text(text)
    clues = parse_ocr(preprocessed_text)
    return clues


def parse_ocr(text):
    """
    Extract the clues from a given text
    The idea:
        - when a line starts with a number, it"s a new clue 
          (add the currently building clue to clues, make a new one)
        - all text past that is the actual clue
        - if line ends with a number (excluding brackets) 
          then that line ending is the solution pattern
        - replace . with ,

    Parameters:
    text: String

    Return:
    clues: An array of clues with their text, number, lengths    
    """

    clues = []
    clue = {}
    clue_text = ""

    for line in text.split("\n"):
        words = line.split()
        if len(words) == 0:
            continue

        # When a line starts with a number, it's a new clue
        # (add the currently building clue to clues, make a new one)
        if re.match(r"\d+.*", words[0]) and len(words) > 1:
            if clue:
                clue["text"] = clue_text.strip()
                clues.append(clue)
            clue = {}
            clue_text = ""
            clue["number"] = get_int(words[0])
            del words[0]

        # If line ends with a number (excluding brackets)
        # then that line ending is the solution pattern
        if re.match("(\()?\d+((\.,-)?\d+)*(\))?", words[-1]):
            lengths_string = words[-1].replace(".", ",")[1:-1]
            lengths = re.split(",|-", lengths_string)
            clue["lengths"] = lengths

        clue_text += " " + " ".join(words)

    clue["text"] = clue_text.strip()
    clues.append(clue)
    return clues


def read_text(image_data):
    '''
    Extract the text from the given image

    Parameters: 
    image_data: The image data array (ndarray)

    Return:
    clues: An array of clues with their text, number, lengths
    '''
    image_data = transform_text_image(image_data)
    gray = get_grayscale(image_data)

    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, config=custom_config)
    preprocessed_text = postprocess_text(text)
    clues = parse_ocr(preprocessed_text)

    return clues


def get_int(word):
    '''
    Extract a number as int from the beginning of a string

    Parameters: 
    word: String

    Return:
    (int): The integer at the beginning of word
    '''

    result = ""
    for char in word:
        if char.isnumeric():
            result += char

    return int(result)

# Thresholding


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Noise removal


def remove_noise(image):
    return cv2.medianBlur(image, 5)

# Get grayscale image


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


if __name__ == "__main__":
    import sys
    pd.set_option("display.max_rows", 10001)
    img = cv2.imread("inputs/pics/clear/across1.jpg")
    print(read_text_original(img))
    print(read_text(img))
