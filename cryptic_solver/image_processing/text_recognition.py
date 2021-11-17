import pytesseract
import cv2
import re

def preprocess_text(text):
    '''
    Changes the misrecognized characters to the expected ones

    Parameters: 
    text: String

    Return:
    replaced_text: String
    '''
    character_replacements = {"°": " ", "©": "(5)", "|": "I", "®": "(5", "@": "(4)"}

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
    gray = get_grayscale(image_data)

    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, config=custom_config)
    preprocessed_text = preprocess_text(text)
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
    return cv2.medianBlur(image,5)

# Get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
