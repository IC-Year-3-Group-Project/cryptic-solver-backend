import cv2
import numpy as np
import base64
from cryptic_solver.grid_recognition import get_grid_from_image
from cryptic_solver.text_recognition import read_text

# Combine grid and text recognition to produce one 
# object with all crossword data
def recognize_image(b64_grid, b64_across, b64_down, ocr="tesseract"):

    grid = b64ToMatrix(b64_grid)
    across = b64ToMatrix(b64_across)
    down = b64ToMatrix(b64_down)

    grid_dict = get_grid_from_image(grid)
    across_dict = read_text(across, ocr)
    down_dict = read_text(down, ocr)

    grid_clues = grid_dict["clues"]

    for clue in down_dict:
      for grid_clue in grid_clues:
          if grid_clue["direction"] == 1 and grid_clue["number"] == clue.get("number", -1):
            grid_clue["text"] = clue.get("text", "NOT_RECOGNIZED_CORRECTLY")
            grid_clue["lengths"] = list(map(int, clue.get("lengths", [0])))

    for clue in across_dict:
      for grid_clue in grid_clues:
          if grid_clue["direction"] == 0 and grid_clue["number"] == clue.get("number", -1):
            grid_clue["text"] = clue.get("text", "NOT_RECOGNIZED_CORRECTLY")
            grid_clue["lengths"] = list(map(int, clue.get("lengths", [0])))

    grid_dict["clues"].sort(key=lambda c: c["number"])

    return grid_dict

def b64ToMatrix(b64_image):
    im_bytes = base64.b64decode(b64_image)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8) 
    return cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

