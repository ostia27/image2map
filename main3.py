import argparse
import glob
import json

from PIL import Image
import numpy as np
from tqdm import tqdm

images = {
    "clear.png": ".",
    "barrel_1.png": "C",
    "bones_1.png": "B",
    "cactus.png": "T",
    "crate_1.png": "Y",
    "crate_powerup.png": "4",
    "crate_tnt.png": "XT",
    "grass_3.png": "F",
    "poison_gas.png": "x",
    "slow_down.png": "z",
    "spawn_blue.png": "1",
    "spawn_red.png": "2",
    "speed_up.png": "w",
    "spikes.png": "v",
    "wall_rock_1.png": "M",
    "water.png": "W",
}

# Step 1: Create the parser
parser = argparse.ArgumentParser(description='Convert an image to a mosaic of tiles.')

# Step 2: Define arguments
parser.add_argument('input_image', help='Path to the input image file')
parser.add_argument('-s', '--size', default='60x60', help='Output image size in format WIDTHxHEIGHT')

args = parser.parse_args()


class Tile:
    def __init__(self, filepath, average_color):
        self.filepath = filepath
        self.average_color = average_color


tiles = []
for file in glob.glob("assets/*"):
    barrel = Image.open(file).convert("RGB")
    image_array = np.array(barrel)
    tiles.append(Tile(file, image_array.mean(axis=0).mean(axis=0)))


def load_image(path):
    return Image.open(path).resize((60 * 20, 60 * 20))


original_image = load_image(args.input_image)


def find_closest_color_vectorized(color, palette):
    # Assuming palette is a list of Tile objects and Tile.average_color is a NumPy array
    colors_matrix = np.array([tile.average_color for tile in palette])
    color_diffs = colors_matrix - color
    distances = np.sum(color_diffs ** 2, axis=1)
    closest_index = np.argmin(distances)
    return palette[closest_index]


def convert_image(original_image, palette):
    width, height = original_image.size
    converted_image = Image.new('RGB', (width, height))

    for y in tqdm(range(height)):
        for x in range(width):
            original_pixel = original_image.getpixel((x, y))
            closest_color = find_closest_color_vectorized(original_pixel, palette)
            converted_image.putpixel((x, y), tuple(closest_color.average_color.astype(int)))

    return converted_image


def convert_tiles_image(original_image, palette, tile_size=20):
    width, height = original_image.size
    converted_image = Image.new('RGB', (width, height))
    tiles_image = [[''] * 60 for _ in range(60)]

    # Adjust the loop to process 20x20 blocks
    for y in tqdm(range(0, height, tile_size)):
        for x in range(0, width, tile_size):
            # Calculate the average color of the 20x20 block
            block = original_image.crop((x, y, x + tile_size, y + tile_size)).convert('RGB')
            block_array = np.array(block)
            average_color = block_array.mean(axis=(0, 1))

            # Find the closest tile
            closest_tile = find_closest_color_vectorized(average_color, palette)
            tiles_image[y // tile_size][x // tile_size] = images[closest_tile.filepath.split('\\')[-1]]

    return tiles_image


print(json.dumps(convert_tiles_image(original_image, tiles)))
