import folium
from folium import IFrame
from folium import plugins
from branca.element import MacroElement
from jinja2 import Template
import math
import os
from math import radians, sin, cos, sqrt, atan2
import traceback
import random
import webbrowser
from view import Marker


class SetUp:
    """
    Setting up each round of the Geoguessr game.

    Attributes:
        current_round (int): the current round number.
        image_index (int):  the index of the round's generated image.
        images_dir (str): the path to the images subfolder in dataset.
        coord_file (str): the path to the coords.csv file.
        html_path (str): the path to the map's html file.
        correct_location (list): the coordinates to the actual location of the round's image.
        guess_coords (list): the coordinates to the guess location of the round's image.
    """

    def __init__(self):
        # Initiating rounds
        self.current_round = 0
        self.image_index = 0
        self.images_dir = "dataset/images"
        self.coord_file = "dataset/coords.csv"
        self.html_path = "map.html"
        self.correct_location = None
        self.guess_coords = None

        self.Marker = Marker()
        self.Stats = Stats(self.guess_coords, self.correct_location)

    def get_current_image_path(self):
        """
        Get path of current round's image.

        Returns:
            String containing image path.
        """
        return os.path.join(self.images_dir, f"{self.image_index}.png")

    def set_correct_location(self, image_index):
        """
        Set correct location of image generated for given round.

        Args:
            image_index (int): index of randomly generated round image.

        Raises:
            IndexError: Image index out of range.
            ValueError: Coordinates not split into two parts.
            Exception: Unexpected errors during processing.
        """
        try:
            # Open coords.csv file and read through lines
            with open(self.coord_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Check that image is in range
            if image_index >= len(lines):
                raise IndexError(f"Image index {image_index} out of range")
            # Parse through line and split into separate coordinates
            line = lines[image_index].strip()
            parts = line.split(",")
            # Check that coordinates are split into 2 parts
            if len(parts) < 2:
                raise ValueError(f"Invalid coordinate format: {line}")
            # Define latitude and longitude tuple
            lat, lon = map(float, parts[:2])
            self.correct_location = [lat, lon]
        # Check for other errors
        except Exception as e:
            print(f"❌ Error setting correct location: {e}")
            raise

    def start_round(self):
        """
        Initialize new round with random location (and corresponding image).

        Returns:
            image_path (f str): the path to the randomly generated image for the new round.
        """
        self.current_round += 1

        # Clear the map
        self.Marker.clear_markers()
        # Generate new random image
        images = os.listdir(self.images_dir)
        self.image_index = random.randint(0, len(images) - 1)
        image_path = f"dataset/images/{self.image_index}.png"
        # Set correct location
        self.set_correct_location(self.image_index)
        # Generate new map
        self.Marker.map.save(self.html_path)
        webbrowser.open(f"file://{os.path.abspath(self.html_path)}", new=0)

        return image_path

        # self.Marker.draw_guess_marker()

    def handle_guess(self):
        """
        Process player's guess and return distance and score

        Raises:
            ValueError: Guess coordinates not set.
            Exception: Unexpected errors during processing.

        """
        if not self.Marker.guess_coords:
            raise ValueError("No guess coordinates set")

        # if not self.Marker.correct_location:
        #     raise ValueError("Correct location not set")

        try:
            # Compute stats
            distance = self.Stats.calculate_distance(
                self.guess_coords, self.correct_location
            )
            score = self.Stats.round_score(distance)
            self.Stats.get_average_score()

            average_score = self.Stats.get_average_score()

            # Draw the correct marker (which will also draw the line)
            self.Marker.draw_correct_marker(
                self.coord_file, self.images_dir, self.image_index
            )

            return distance, score, average_score

        except Exception as e:
            print(f"❌ Error handling guess: {e}")
            raise


class Stats:
    """
    Computing metrics for scoreboard tracking player's accuracy of guesses.

    Attributes:
        rounds (list): saved score for every round played.
        guess_coords (list): player's guess coordinates.
        actual_coords (list): location's actual coordinates.
    """

    def __init__(self, guess_coords, actual_coords):
        self.rounds = []
        self.guess_coords = guess_coords
        self.actual_coords = actual_coords

    def get_average_score(self):
        """
        Calculate the average score across all rounds that have been played so far.

        Return:
            average_score (int): the player's average score.
        """
        if not self.rounds:
            return 0
        dist = self.calculate_distance(self.guess_coords, self.actual_coords)
        score = self.round_score(dist)
        self.rounds.append(score)

        average_score = sum(self.rounds // len(self.rounds))
        return average_score

    @staticmethod
    def calculate_distance(guess_coords, actual_coords):
        """
        A static method calculating distance between the guess and answer.

        Returns:
            distance (int): the distance between the guess and the answer.
        """
        # Haversine formula for distance calculation
        lat1, lon1 = radians(guess_coords[0]), radians(guess_coords[1])
        lat2, lon2 = radians(actual_coords[0]), radians(actual_coords[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        RADIUS_OF_EARTH = 6371000  # meters
        distance = RADIUS_OF_EARTH * c

        return distance

    @staticmethod
    def round_score(distance_meters):
        """
        Computes round score on a scale of 0 to 5000 points.

        Returns:
            score (int): the round score.
        """
        HIGHEST_SCORE = 5000
        SIGMA = 250000  # Width of bell curve
        score = round(
            HIGHEST_SCORE * math.exp(-0.5 * pow((distance_meters / SIGMA), 2))
        )
        return score
