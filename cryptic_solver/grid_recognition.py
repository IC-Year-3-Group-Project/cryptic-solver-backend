import cv2
import math
import numpy as np

# Define constants to use later
square_factor = 2.0 / 3.0
min_area = 5.5
area_factor = 2.0 / 3.0
epsilon = 0.0005

# Get the grid in a dictionary format from an image
def get_grid_from_image():

    # Read image into a matrix
    image = cv2.imread("crossword.png")

    # Convert RGB to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold image to black and white
    flag, thresh = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour_list = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Make sure contours are vaguely square
        if w < h * square_factor or w * square_factor > h:
            continue

        # Make sure contours are of a certain area
        contour_area = cv2.contourArea(contour)
        if contour_area < min_area or contour_area < area_factor * w * h:
            continue

        # Contour list is in ascending order
        contour_list.append(contour)

        median_area = sorted(map(cv2.contourArea, contour_list))[
            math.floor(len(contour_list) / 2)]
        median_perimeter = sorted([cv2.arcLength(c, True) for c in contour_list])[
            math.floor(len(contour_list) / 2)]

    temp = []
    for contour in contour_list:
        if abs(cv2.contourArea(contour) - median_area) > median_area / 2.0 and \
                abs(cv2.arcLength(contour, True) - median_perimeter) < median_perimeter / 2.0:
            continue
        if abs(cv2.arcLength(contour, True) - median_perimeter) >= median_perimeter / 2.0:
            continue

        temp.append(contour)

    contour_list = temp

    average_side_length = median_perimeter / 4

    rectangles = list(map(cv2.boundingRect, contour_list))

    xs = sorted(map(lambda c: c[0], rectangles))
    ys = sorted(map(lambda c: c[1], rectangles))

    x_bounds = []
    y_bounds = []

    prev_x = -10000
    prev_y = -10000

    for x in xs:
        if x - prev_x > average_side_length / 2:
            x_bounds.append(x)
        prev_x = x

    for y in ys:
        if y - prev_y > average_side_length / 2:
            y_bounds.append(y)
        prev_y = y

    grid = create_grid(x_bounds, y_bounds, rectangles)

    fill_clue_numbers(grid)
    fill_clue_lengths(grid)

    grid_as_json = get_grid_as_json(grid)

    return grid_as_json


# Initialize the grid as an array containing the
# location and sizes of the cells
def create_grid(x_bounds, y_bounds, rectangles):

    x_bounds_len = len(x_bounds)
    y_bounds_len = len(y_bounds)

    grid = np.full((y_bounds_len, x_bounds_len), None)

    for i in range(len(rectangles)):
        j = 0
        k = 0

        x, y, _, _ = rectangles[i]
        while j < y_bounds_len-1 and y_bounds[j + 1] <= y + epsilon:
            j = j + 1

        while k < x_bounds_len-1 and x_bounds[k + 1] <= x + epsilon:
            k = k + 1

        grid[j][k] = {"can_go_to": []}

    return grid

# A function that uses the can_go_to attribute of the grid to assign
# numbers to the cells from which you can only go down or right
def fill_clue_numbers(grid):
    clue_number = 1
    m, n = np.shape(grid)

    for j in range(m):
        for k in range(n):
            if grid[j][k] == None:
                continue

            if (j + 1 < m and grid[j + 1][k] != None):
                grid[j + 1][k].get("can_go_to").append("top")
                grid[j][k].get("can_go_to").append("bottom")

            if (k + 1 < n and grid[j][k + 1] != None):
                grid[j][k + 1].get("can_go_to").append("left")
                grid[j][k].get("can_go_to").append("right")

            can_go_to = grid[j][k].get("can_go_to")

            is_clue = False
            if not "top" in can_go_to and "bottom" in can_go_to:
                grid[j][k]["is_down"] = True
                grid[j][k]["clue_number"] = clue_number
                is_clue = True

            if not "left" in can_go_to and "right" in can_go_to:
                grid[j][k]["is_across"] = True
                grid[j][k]["clue_number"] = clue_number
                is_clue = True

            if (is_clue):
                clue_number = clue_number + 1

# Fill the lengths of the clues according to
# whether it they are going down or accross
def fill_clue_lengths(grid):
    m, n = np.shape(grid)

    for j in range(m-1, -1, -1):
        for k in range(n-1, -1, -1):
            if (grid[j][k] == None):
                continue

            down = 1
            right = 1

            if (j + 1 < m):
                if (grid[j + 1][k] != None):
                    down += grid[j + 1][k]["down"]

            if (k + 1 < n):
                if (grid[j][k + 1] != None):
                    right += grid[j][k + 1]["right"]

            grid[j][k]["down"] = down
            grid[j][k]["right"] = right


# Create a JSON object from the grid
def get_grid_as_json(grid):
    clues = []
    m, n = np.shape(grid)

    for j in range(m-1, -1, -1):
        for k in range(n-1, -1, -1):
            if (grid[j][k] == None):
                continue

            if (grid[j][k]["down"] > 1 and "is_down" in grid[j][k]):
                write_clue(grid, clues, j, k, "down")

            if (grid[j][k]["right"] > 1 and "is_across" in grid[j][k]):
                write_clue(grid, clues, j, k, "right")

    grid_as_json = {
        "clues": clues,
        "rows": m,
        "columns": n,
    }

    return grid_as_json

# Add a clue to the clues array
def write_clue(grid, clues, j, k, direction):
    direction_number = direction == (1 if "down" else 0)

    if "clue_number" in grid[j][k]:
        clues.append({
            "number": grid[j][k]["clue_number"],
            "direction": direction_number,
            "text": "TODO",
            "total_length": grid[j][k][direction],
            "lengths": [grid[j][k][direction]],
            "x": k,
            "y": j,
        })