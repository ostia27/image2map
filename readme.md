# image2map

This project converts an input image into a brawl map. The resulting image is saved to an output file.

## Features

- Load input images and resize them.
- Load tile images from a specified directory.
- Calculate the average color of each tile image.
- Convert the input image to a mosaic using the closest matching tiles based on color.
- Save the converted mosaic image.
- Optionally, print the mosaic image data as JSON.

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the script, use the following command:
    
 ```bash
 python main.py <input_image> -o <output_image> -s <size>
 ```
