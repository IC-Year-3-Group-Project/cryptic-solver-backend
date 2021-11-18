import pytesseract
import cv2
import re
import easyocr
from functools import reduce
# TODO change when merged to master
if __name__ != "__main__":
    from cryptic_solver.image_processing.transform_image import transform_text_image

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
            "1" < replaced_text[i + 1] <= "9" and \
           "1" <= replaced_text[i + 2] <= "9":
            replaced_text = replaced_text[:i + 2] + "," + replaced_text[i + 2:]

    return replaced_text


def postprocess_text_with_conf(text):
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

    replaced_texts = []

    for replaced_text, conf, line_no in text:
        for (k, r) in character_replacements.items():
            replaced_text = replaced_text.replace(k, r)

        # Take care of cases where the lengths of a two-word clue have been stuck together
        for i in range(len(replaced_text)-2):
            if replaced_text[i] == "(" and \
                "1" < replaced_text[i + 1] <= "9" and \
                    "1" <= replaced_text[i + 2] <= "9":
                replaced_text = replaced_text[:i +
                                              2] + "," + replaced_text[i + 2:]
        replaced_texts.append((replaced_text, conf, line_no))

    return replaced_texts


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

    custom_config = r"--oem 3 --psm 6"
    if ocr == "original":
        # Preprocessing: returns preprocessed image
        processed = preprocess_original(image_data)

        # OCR processing: extract (string, conf, line number) from image
        text = pytesseract.image_to_data(
            processed, config=custom_config, output_type='data.frame')
        text = text[text.conf > 0]
        text = [tuple(x) for x in text[text.conf != -1]
                [['text', 'conf', 'line_num']].to_numpy()]

        # Postprocessing: filters badly processed text
        postprocessed_text = postprocess_text_with_conf(text)

        # Parse into clues: number, length, text and conf
        clues = parse_ocr_with_conf(postprocessed_text)

        print("\n\nRead Text Original\n")
    elif ocr == "tesseract":
        # Preprocessing
        processed = preprocess(image_data)

        # OCR processing
        text = pytesseract.image_to_data(
            processed, config=custom_config, output_type='data.frame')
        text = [tuple(x) for x in text[text.conf != -1]
                [['text', 'conf', 'line_num']].to_numpy()]

        # Postprocessing
        postprocessed_text = postprocess_text_with_conf(text)

        # Parse into clues
        clues = parse_ocr_with_conf(postprocessed_text)

        print("\n\nRead Text New Preprocess\n")
    elif ocr == "easy_ocr":
        # Preprocessing
        processed = preprocess(image_data)

        # OCR processing
        text = [(x[-2], 10*x[-1], ([x[0][0][1], x[0][2][1]]))
                for x in reader.readtext(processed)]
        text_with_line_no = []
        last_topdown = (-2, -1)
        line_no = 0
        for word, conf, curr_topdown in text:
            if not sufficiently_overlap(last_topdown, curr_topdown):
                line_no += 1
            text_with_line_no.append((word, conf, line_no))
            last_topdown = curr_topdown
        text = text_with_line_no

        # Postprocessing
        postprocessed_text = postprocess_text_with_conf(text)

        # Parse into clues
        clues = parse_ocr_with_conf(postprocessed_text)

        print("\n\nRead Text Easy OCR\n")
    return clues


def sufficiently_overlap(last_topdown, curr_topdown):
    last_width = last_topdown[1] - last_topdown[0]
    curr_width = curr_topdown[1] - curr_topdown[0]
    if last_topdown[1] < curr_topdown[0] or last_topdown[0] > curr_topdown[1]:
        return False
    if last_topdown[1] >= curr_topdown[0]:
        inner_width = last_topdown[1] - curr_topdown[0]
        return inner_width / curr_width > 0.75 or inner_width / last_width > 0.75
    if last_topdown[0] <= curr_topdown[1]:
        inner_width = curr_topdown[1] - last_topdown[0]
        return inner_width / curr_width > 0.75 or inner_width / last_width > 0.75
    return False


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


def parse_ocr_with_conf(text):
    clues = []
    clue = {}
    clue_text = ""
    total_conf = 0
    no_of_strings = 0

    line = ""
    line_builder = []
    last_line_no = 1
    for i, (string, conf, line_no) in enumerate(text):
        # if not gone onto new line or reached last parsed text
        if not (line_no != last_line_no or i == len(text)-1):
            line_builder.append(string)
            total_conf += conf
            no_of_strings += 1
            continue

        last_line_no = line_no
        if i == len(text)-1:
            line_builder.append(string)
        line = " ".join(line_builder)
        line_builder = [string]

        words = line.split()
        if len(words) == 0:
            continue

        # When a line starts with a number, it's a new clue
        # (add the currently building clue to clues, make a new one)
        if re.match(r"\d+.*", words[0]) and len(words) > 1:
            if clue:
                clue["text"] = clue_text.strip()
                clue["conf"] = round(total_conf / no_of_strings, 3)
                clues.append(clue)
            clue = {}
            clue_text = ""
            total_conf = 0
            no_of_strings = 0
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
    clue["conf"] = round(total_conf / no_of_strings, 3)
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
    return read_text_multimodal(image_data, "original")


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
    from transform_image import transform_text_image
    img = cv2.imread("inputs/pics/clear/across1.jpg")
    print(read_text_multimodal(img, "original"))
    print(read_text_multimodal(img, "tesseract"))
    print(read_text_multimodal(img, "easy_ocr"))
