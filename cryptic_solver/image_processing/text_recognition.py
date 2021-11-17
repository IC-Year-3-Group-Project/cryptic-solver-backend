import pytesseract
import cv2
import re
import easyocr
from functools import reduce
from transform_image import transform_text_image

reader = easyocr.Reader(['en'])


def preprocess_original(image):
    image = get_grayscale(image)
    return image


def preprocess(image):
    gray = get_grayscale(image)
    blurred = remove_noise(gray)
    thresh = thresholding(blurred)

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


def make_text(a, b):
    if (a[len(a)-1] == ')'):
        return a + '\n\n' + b
    return a + ' ' + b


def read_text_multimodal(image_data, ocr):
    '''
    Extract the text from the given image using multiple OCR models

    Parameters: 
    image_data: The image data array (ndarray)
    ocr: Type of ocr model to perform (string)

    Return:
    clues: An array of clues with their text, number, lengths
    '''

    processed = preprocess(image_data)

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
    transformed = transform_text_image(image_data)
    gray = preprocess_original(transformed)

    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, config=custom_config)
    postprocessed_text = postprocess_text(text)
    clues = parse_ocr(postprocessed_text)

    return clues


def distance_transform(image):
    return cv2.distanceTransform(image, cv2.DIST_L2, 5)


def adaptive_thresholding(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 71, 6)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def remove_noise(image):
    image = cv2.GaussianBlur(image, (5, 5), 0)
    return cv2.bilateralFilter(image, 9, 65, 75)


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


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


if __name__ == "__main__":
    img = cv2.imread("inputs/pics/clear/across1.jpg")
    print(read_text(img))
    print(read_text_multimodal(img))
