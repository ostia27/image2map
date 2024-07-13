import argparse
import glob
from PIL import Image
import numpy as np
from tqdm import tqdm

# Step 1: Create the parser
parser = argparse.ArgumentParser(description='Convert an image to a mosaic of tiles.')

# Step 2: Define arguments
parser.add_argument('input_image', help='Path to the input image file')
parser.add_argument('-o', '--output', default='converted_image.png', help='Path to the output image file')

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
    return Image.open(path).resize((60*20, 60*20))


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

    # Adjust the loop to process 20x20 blocks
    for y in tqdm(range(0, height, tile_size)):
        for x in range(0, width, tile_size):
            # Calculate the average color of the 20x20 block
            block = original_image.crop((x, y, x + tile_size, y + tile_size))
            block_array = np.array(block)
            average_color = block_array.mean(axis=(0, 1))

            # Find the closest tile
            closest_tile = find_closest_color_vectorized(average_color, palette)
            tile_image = Image.open(closest_tile.filepath)

            # Paste the tile image onto the converted image
            converted_image.paste(tile_image, (x, y))

    return converted_image


converted_image = convert_tiles_image(original_image, tiles)
converted_image.save(args.output)
