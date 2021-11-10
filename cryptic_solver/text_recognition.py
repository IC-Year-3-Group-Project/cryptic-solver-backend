import pytesseract
import cv2
import re
from cryptic_solver_project import settings

if settings.tesseract_cmd != "":
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd



def preprocess(image):

    image = get_grayscale(image)
    #image = remove_noise(image)
    #image = thresholding(image)

    return image

def preprocess_text(text):
    character_replacements = {"°": " ", "©": "(5)", "|": "I", "®": "(5", "@": "(4)"}

    for (k, r) in character_replacements.items():
        replaced_text = text.replace(k, r)

    # Take care of cases where the lengths of a two-word clue have been stuck together
    for i in range(len(replaced_text)-2):
        if replaced_text[i] == "(" and \
           replaced_text[i + 1] > "1" and \
           replaced_text[i + 1] <= "9" and \
           replaced_text[i + 2] >= "1" and \
           replaced_text[i + 2] <= "9":
            replaced_text = replaced_text[:i + 2] + "," + replaced_text[i + 2:]

    return replaced_text


#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def read_text(image_data):
    #TODO: need to change this to an environment variable for deployment
    #pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

    processed = preprocess(image_data)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)
    preprocessed_text = preprocess_text(text)
    clues = parse_ocr(preprocessed_text)
    return clues

def parse_ocr(text):

    """
    the idea:
        - when a line starts with a number, it's a new clue (add the currently building clue to clues, make a new one)
        - all text past that is the actual clue
        - if line ends with a number (excluding brackets) then that line ending is the solution pattern
        - replace . with ,

    """

    clues = []
    clue = {}
    clue_text = ""

    for line in text.split("\n"):
        words = line.split()
        if len(words) == 0:
            continue

        # when a line starts with a number, it's a new clue (add the currently building clue to clues, make a new one)
        if re.match(r"\d+.*", words[0]) and len(words) > 1:
            if clue:
                clue['text'] = clue_text.strip()
                clues.append(clue)
            clue = {}
            clue_text = ""
            clue['number'] = get_int(words[0])
            del words[0]

        # if line ends with a number (excluding brackets) then that line ending is the solution pattern
        if re.match("(\()?\d+((\.,-)?\d+)*(\))?", words[-1]):
            lengths_string = words[-1].replace('.', ',')[1:-1]
            lengths = lengths_string.split(",")
            clue['lengths'] = lengths
            if len(words) > 0:
                del words[-1]

        clue_text += " " + " ".join(words)

    clue['clue'] = clue_text.strip()
    clues.append(clue)
    return clues

def get_int(word):
    result = ""
    for char in word:
        if char.isnumeric():
            result += char
    return int(result)