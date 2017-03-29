# Getting Started

# Need to get this key from https://developers.data.gov.sg/
key = open("data-key.txt").read()
import requests
taxis = requests.get(
    'https://api.data.gov.sg/v1/transport/taxi-availability',
    params = {"date_time": "2017-03-29T00:00:00"},
    headers = {"api-key": key}
).json()

# Explore the `taxis` structure

max(x for (x, y) in taxis['features'][0]['geometry']['coordinates'])
min(x for (x, y) in taxis['features'][0]['geometry']['coordinates'])

# Simple visualization
import math
min_x, max_x, min_y, max_y = math.inf, -math.inf, math.inf, -math.inf

for x, y in taxis['features'][0]['geometry']['coordinates']:
    min_x = min(x, min_x)
    max_x = max(x, max_x)
    min_y = min(y, min_y)
    max_y = max(y, max_y)
    
min_x, max_x, min_y, max_y

w = 40; h = int(w * (max_y - min_y) / (max_x - min_x))

w, h

grid = [[0] * (w+1) for i in range(h+1)]

for x, y in taxis['features'][0]['geometry']['coordinates']:
    cell_x = int((x - min_x) / (max_x - min_x) * w)
    cell_y = int((y - min_y) / (max_y - min_y) * h)
    
    grid[cell_y][cell_x] += 1

for row in reversed(grid):
    print(" ".join([str(n).rjust(3, " ") for n in row]))
    
# Colors
# http://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color

W = '\033[0m'  # white (normal)
R = '\033[31m' # red
G = '\033[32m' # green
O = '\033[33m' # orange
B = '\033[34m' # blue
P = '\033[35m' # purple

colors = [B, G, O, R]


# Basic Colors

non_zero_cells = [
    item
    for row in grid
    for item in row if item != 0
]

sorted_cells = sorted(non_zero_cells)
enumerated = enumerate(sorted_cells)
rankings = {
    value: index / len(non_zero_cells)
    for (index, value) in enumerated
}

for row in reversed(grid):
    strs = []
    for n in row:
        if n == 0:
            strs.append("   ")
        else:
            color_index = int(rankings[n] * len(colors))

            color = colors[color_index]
            strs.append(color + str(n).rjust(3, " ") + W)
    print("".join(strs))
    
# Distributed Colors
# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

import colorsys

for row in reversed(grid):
    strs = []
    for n in row:
        if n == 0:
            strs.append("   ")
        else:

            (r, g, b) = colorsys.hsv_to_rgb(1-rankings[n], 1, 1)
            
            def scale(float_zero_to_one):
                return min(5, int(6 * float_zero_to_one))
                 
            color_index = 16 + 36 * scale(r) + 6 * scale(g) + scale(b)  
            color = "\033[38;5;" + str(color_index) + "m"
            
            strs.append(color + str(n).rjust(3, " ") + W)
    print("".join(strs))

