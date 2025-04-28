"""Main function for running game loop"""

import sys
import os
import shutil
import random
import kagglehub
import pygame as pg
import pygame_widgets
from pygame_widgets.button import ButtonArray
import pandas as pd

# Setup windows position to make pygame pop-up on the left-hand side
x = 0
y = 0
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (x, y)

# Setup pygame display
pg.init()
screen = pg.display.set_mode((1000, 720))
clock = (
    pg.time.Clock()
)  # keeps track of time could be good if we implement a timer


# NEED TO UPDATE ONCLICK FUNCTIONS
# Can change pressed color and visuals later
# Creates an array of buttons
buttonArray = ButtonArray(
    # Mandatory Parameters
    screen,  # Surface to place button array on
    50,  # X-coordinate
    575,  # Y-coordinate
    500,  # Width
    100,  # Height
    (2, 1),  # Shape: 2 buttons wide, 2 buttons tall
    border=10,  # Distance between buttons and edge of array
    texts=(
        "Confirm Guess",
        "Next Round",
    ),  # Sets the texts of each button (counts left to right then top to bottom)
    colour=(210, 210, 180),  # Background color of array
    # When clicked, print number
    onClicks=(
        lambda: print("1"),
        lambda: print("2"),
        lambda: print("3"),
        lambda: print("4"),
    ),
)


def main():
    image, image_index = generate_image()
    RUNNING = True
    while RUNNING:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                RUNNING = False
                sys.exit()
        screen.fill("dark blue")
        screen.blit(image, (50, 40))
        pygame_widgets.update(events)
        pg.display.update()


# DOES NOT WORK --> src folder is not right
def street_view_dataset():
    """
    Download Google Street View image dataset by Paul Chambaz by
    calling Kagglehub's API.

    Args:
        None.

    Returns:
        None.
    """
    # Download dataset into set folder
    dataset_path = kagglehub.dataset_download(
        "paulchambaz/google-street-view/versions/1/"
    )
    img_src_folder = os.path.join(dataset_path + "/images")
    coord_src_folder = os.path.join(dataset_path)
    # Create destination folder to move images to if it doesn't already exist
    img_dest_folder = "actual_dataset/images"
    os.makedirs(img_dest_folder, exist_ok=True)
    # Create destination folder to move coordinates to if it doesn't already exist
    coord_dest_folder = "actual_dataset/"
    os.makedirs(coord_dest_folder, exist_ok=True)
    # Copy image files from source to destination
    # Copying instead of moving to preserve metadata
    for file in os.listdir(img_src_folder):
        img_src_path = os.path.join(img_src_folder, file)
        img_dest_path = os.path.join(img_dest_folder, file)
        if file.endswith(".png"):
            shutil.copy2(img_src_path, img_dest_path)
    # Copying coordinate file from source to destination
    for file in os.listdir(coord_src_folder):
        coord_src_path = os.path.join(img_src_folder, file)
        coord_dest_path = os.path.join(img_dest_folder, file)
        if file.endswith(".csv"):
            shutil.copy2(coord_src_path, coord_dest_path)
    print(
        f"Images copied to {img_dest_folder} and coordinates copied to"
        f" {coord_dest_folder}"
    )


# street_view_dataset()


def read_coord_csv(csv_file="coord.csv"):
    """
    Read coord.csv file as a pandas dataframe.

    Args:
        file: a .csv file containing the longitude and latitude for
        each corresponding image index.

    Returns:
        A pandas dataframe.
    """
    coords = pd.read_csv("test_dataset/" + csv_file, header=None)
    return coords


def generate_image(round_number, coords):
    """
    Generate an image of a random location for the round.

    Args:
        None.

    Returns:
        Resized image (.jpg for test and .png for actual)
        Integer representing index of image in coords.csv
    """
    # Download random image
    image_index = random.randint(0, 2)
    round_image = pg.image.load(f"test_dataset/images/{image_index}.jpg")
    # Resize image to 500 x 500
    IMAGE_SIZE = (500, 500)
    round_image = pg.transform.scale(round_image, IMAGE_SIZE)
    # Find and save coordinates for generated image by its index
    round_answers = {}
    round_answers[round_number] = [round_image, coords[image_index]]

    return round_image, image_index


main()
