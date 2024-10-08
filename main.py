import argparse
import glob
import numpy as np
from PIL import Image
from tqdm import tqdm

# Step 1: Create the parser
parser = argparse.ArgumentParser(description='Convert an image to a mosaic of tiles.')

# Step 2: Define arguments
parser.add_argument('input_image', help='Path to the input image file')
parser.add_argument('-o', '--output', default='converted_image.png', help='Path to the output image file')
parser.add_argument('-s', '--size', default='60x60', help='Output image size in format WIDTHxHEIGHT')

args = parser.parse_args()
width, height = map(int, args.size.split('x'))


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
    return Image.open(path).resize((width * 20, height * 20))


original_image = load_image(args.input_image)


def find_closest_color_vectorized2(color, palette):
    r, g, b = color
    color_diffs = []
    for color in palette:
        cr, cg, cb = color.average_color
        color_diff = np.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


def convert_image(original_image, palette):
    width, height = original_image.size
    converted_image = Image.new('RGB', (width, height))

    for y in tqdm(range(height)):
        for x in range(width):
            original_pixel = original_image.getpixel((x, y))
            closest_color = find_closest_color_vectorized2(original_pixel, palette)
            converted_image.putpixel((x, y), tuple(closest_color.average_color.astype(int)))

    return converted_image


def convert_tiles_image(original_image, palette, tile_size=20):
    width, height = original_image.size
    converted_image = Image.new('RGB', (width, height))

    # Adjust the loop to process 20x20 blocks
    for y in tqdm(range(0, height, tile_size)):
        for x in range(0, width, tile_size):
            # Calculate the average color of the 20x20 block
            block = original_image.crop((x, y, x + tile_size, y + tile_size)).convert('RGB')
            block_array = np.array(block)
            average_color = block_array.mean(axis=0).mean(axis=0)

            # Find the closest tile
            closest_tile = find_closest_color_vectorized2(average_color, palette)
            tile_image = Image.open(closest_tile.filepath)
            # Paste the tile image onto the converted image
            converted_image.paste(tile_image, (x, y))

    return converted_image


converted_image = convert_tiles_image(original_image, tiles)
converted_image.save(args.output)
