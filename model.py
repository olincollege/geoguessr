"""Model of Model, View, Controller Architecture"""

from math import radians, sin, cos, sqrt, atan2, exp
import random


class GeoGuessr:
    """
    Geoguessr game logic and structure.

    Attributes:
        num_rounds (int): number of rounds played.
        mode (str): which stage of the round the player is in
        (guessing, seeing their score, or not giving a valid guess).
        image_path (str): the path to the generated image.
        image_num (int): index of image in coords.csv file.
        average_score (int): average score of rounds played.
        current_score (int): player's score for the current round
        played.
        user_text (str): unprocessed player's text input of guess
        coordinates.
        guess_lat (float): player's guess latitude.
        guess_lon (float): player's guess longitude.
        correct_lat (float): generated image's actual latitude.
        correct_lon (float): generated image's actual longitude.
        guess_lat_pixels (float): converted y coordinate of guess_lat
        on map in pixels.
        guess_lon_pixels (float): converted x coordinate of guess_lat
        on map in pixels.
        correct_lat_pixels (float): converted y coordinate of correct_lat
        on map in pixels.
        correct_lon_pixels (float): converted x coordinate of correct_lat
        on map in pixels.
        distance (int): distance between player's guess and answer in
        meters.
        input_error (bool): whether or not input was valid.
    """

    def __init__(self):
        """
        Initializes necessary attributes for tracking mode and state of score,
        generated image, mpa, and inputs.
        """
        self._num_rounds = 0
        self._mode = "guess"
        self._image_path = (  # Set default image path for first round
            "dataset/images/9999.png"
        )
        self._image_num = 0
        self._average_score = 0
        self._current_score = 0
        self._user_text = ""
        self._guess_lat = 0
        self._guess_lon = 0
        self._correct_lat = 0
        self._correct_lon = 0
        self._guess_lat_pixels = 0
        self._guess_lon_pixels = 0
        self._correct_lat_pixels = 0
        self._correct_lon_pixels = 0
        self._distance = 0
        self._input_error = False

    def add_user_text(self, user_input):
        """
        Adds text from typing to user's full input.

        Args:
            user_input (str): parsed coordinates from user input to
            textbox.
        """
        self._user_text += user_input

    def delete_user_text(self):
        """
        Deletes last character from user_text when pressing
        backspace.
        """
        self._user_text = self._user_text[:-1]

    def set_guess_coordinates(self, lat, lon):
        """
        Sets guess coordinates based on parsed inputs from textbox.

        Args:
            lat (float): player's guess latitude validated by
            Controller.
            lon (float): player's guess latitude validated by
            Controller.
        """
        self._guess_lat = lat
        self._guess_lon = lon

    def get_score(self):
        """
        Gets stats for scoreboard and updates game state after valid
        input received and submitted.
        """
        self.get_pixels()
        self.calculate_distance()
        self.calculate_score()
        self.calculate_average_score()
        self._user_text = ""
        self._mode = "score"

    def get_pixels(self):
        """
        Converts latitude and longitude to x and y pixel positions on
        the map that shows an equirectangular projection of the world.
        """
        MAP_WIDTH = 1021  # Total horizontal pixels of the map image
        MAP_HEIGHT = 510  # Total vertical pixels of the map image

        # Longitude → X
        self._guess_lon_pixels = ((self._guess_lon + 180) / 360) * MAP_WIDTH
        self._correct_lon_pixels = ((self._correct_lon + 180) / 360) * MAP_WIDTH

        # Latitude → Y (invert because top is +90° and bottom is -90°)
        self._guess_lat_pixels = ((90 - self._guess_lat) / 180) * MAP_HEIGHT
        self._correct_lat_pixels = ((90 - self._correct_lat) / 180) * MAP_HEIGHT

    def calculate_distance(self):
        """
        Calculates distance between player's guess coordinates and
        the correct location using the Haversine formula.
        """
        lat1, lon1 = radians(self._guess_lat), radians(self._guess_lon)
        lat2, lon2 = radians(self._correct_lat), radians(self._correct_lon)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            sin(delta_lat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        EARTH_RADIUS = 6371000  # meters
        self._distance = round(EARTH_RADIUS * c)

    def calculate_score(self):
        """
        Calculates score of the current round based on the accuracy
        of the player's guess. 5000 points is the highest possible
        score and 0 points is the lowest. Scoring is based on
        Gaussian distribution.
        """
        HIGHEST_SCORE = 5000
        SIGMA = 500000
        self._current_score = round(
            HIGHEST_SCORE * exp(-0.5 * pow((self._distance / SIGMA), 2))
        )

    def calculate_average_score(self):
        """
        Calculates the average score of the rounds played thus far.
        """
        previous_total = self._average_score * self._num_rounds
        new_total = previous_total + self._current_score
        self._num_rounds += 1
        self._average_score = round(new_total / self._num_rounds)

    def next_guess(self):
        """
        Prepares the game state for the next round by generating a
        new image, finding its correct coordinates, and resetting the
        game mode to "guess".
        """
        self.get_image_path()
        self.get_correct_coords()
        self._mode = "guess"

    def get_image_path(self):
        """
        Randomly generates the image path of a new location of a
        given round.
        """
        min_image = 0
        max_image = 9999
        self._image_num = random.randint(min_image, max_image)
        self._image_path = f"dataset/images/{self._image_num}.png"

    def get_correct_coords(self):
        """
        Finds the tagged coordinates of the randomly generated image
        by parsing through the coords.csv file.

        Raises:
            IndexError: Image index is out of the range of
            coords.csv so the image doesn't exist.
        """
        with open("dataset/coords.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
        while self._image_num >= len(lines):
            self.get_image_path()
        line = lines[self._image_num].strip()
        parts = line.split(",")
        self._correct_lat = float(parts[0])
        self._correct_lon = float(parts[1])
        print(line, self._correct_lon, self._correct_lat)

    def no_error(self):
        """
        Resets the game mode to "guess" when no errors are raised.
        """
        self._mode = "guess"

    def set_input_error(self, value: bool):
        """
        Updates input_error value based on whether or not the given
        input was valid.
        """
        self._input_error = value

    @property
    def input_error(self):
        """Return input_error instance."""
        return self._input_error

    @property
    def user_text(self):
        """Return user_text instance."""
        return self._user_text

    @property
    def mode(self):
        """Return mode instance."""
        return self._mode

    @property
    def image_path(self):
        """Return image_path instance."""
        return self._image_path

    @property
    def distance(self):
        """Return distance instance."""
        return self._distance

    @property
    def current_score(self):
        """Return current_score instance."""
        return self._current_score

    @property
    def average_score(self):
        """Return average_score instance."""
        return self._average_score

    @property
    def guess_lat_pixels(self):
        """Return guess_lat_pixels instance."""
        return self._guess_lat_pixels

    @property
    def guess_lon_pixels(self):
        """Return guess_lon_pixels instance."""
        return self._guess_lon_pixels

    @property
    def correct_lat_pixels(self):
        """Return correct_lat_pixels instance."""
        return self._correct_lat_pixels

    @property
    def correct_lon_pixels(self):
        """Return correct_lon_pixels instance."""
        return self._correct_lon_pixels
