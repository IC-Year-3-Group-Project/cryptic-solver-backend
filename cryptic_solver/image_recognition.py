import cv2

from grid_recognition import get_grid_from_image
from text_recognition import read_text

# Combine grid and text recognition to produce one 
# object with all crossword data
def recognize_image():
    across = cv2.imread("across.png")
    down = cv2.imread("down.png")
    grid = cv2.imread("grid.png")

    grid_dict = get_grid_from_image(grid)
    across_dict = read_text(across)
    down_dict = read_text(down)

    grid_clues = grid_dict["clues"]

    for clue in down_dict:
      for grid_clue in grid_clues:
          if grid_clue["direction"] == 1 and grid_clue["number"] == clue["number"]:
            grid_clue["text"] = clue["text"]
            grid_clue["lenghts"] = list(map(int, clue["lenghts"]))
    
    for clue in across_dict:
      for grid_clue in grid_clues:
          if grid_clue["direction"] == 0 and grid_clue["number"] == clue["number"]:
            grid_clue["text"] = clue["text"]
            grid_clue["lenghts"] = list(map(int, clue["lenghts"]))

    return grid_dict
