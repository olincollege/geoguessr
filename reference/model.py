"""Model file"""

import webbrowser
import math
import os
from math import radians, sin, cos, sqrt, atan2
import random


class Setup:
    """
    Setting up each round of the Geoguessr game.

    Attributes:
        current_round (int): the current round number.
        image_index (int):  the index of the round's generated image.
        images_dir (str): the path to the images subfolder in dataset.
        coord_file (str): the path to the coords.csv file.
        html_path (str): the path to the map's html file.
        correct_location (list): the coordinates to the actual location of
        the round's image.
        guess_coords (list): the coordinates to the guess location of the
        round's image.

        stats: all methods and attributes from Stats class.
        gamepins: all methods and attributes from GamePins class.
    """

    def __init__(self, gamepins, guess_coords):
        """
        Initialize related class methods/attributes, coordinate variables,
        scoreboard stats variables, and image and HTML metadata.

        Args:
            stats: Stats class.
            gamePins: GamePins class.
            guess_coords (list): player's guess coordinates.
        """
        self._stats = Stats
        self._gamepins = gamepins

        # Coordinates
        self._guess_coords = guess_coords
        self._correct_location = None

        # Scoreboard stats
        self._score = None
        self._distance = None
        self._average_score = None

        # Image and HTML metadata
        self._image_index = 0
        self._image_path = ""
        self.images_dir = "dataset/images"
        self.coord_file = "dataset/coords.csv"
        self.html_path = "map.html"

    def start_round(self):
        """
        Initialize new round with random location (and corresponding
        image).
        """
        # Clear the map
        self._gamepins.clear_markers()
        # Generate new random image
        images = os.listdir(self.images_dir)
        self._image_index = random.randint(0, len(images) - 1)
        self._image_path = os.path.join(
            self.images_dir, f"{self._image_index}.png"
        )
        # Set correct location
        self.set_correct_location(self._image_index)
        # Generate new map
        self.map.save(self.html_path)
        webbrowser.open(f"file://{os.path.abspath(self.html_path)}", new=0)

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
            if self._image_index >= len(lines):
                raise IndexError(
                    f"Image index {self._image_index} out of range"
                )
            # Parse through line and split into separate coordinates
            line = lines[self.image_index].strip()
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

    def handle_guess(self):
        """
        Process player's guess and return scoreboard stats.

        Raises:
            ValueError: Guess coordinates not set.
            Exception: Unexpected errors during processing.

        Returns:
            distance (int): the distance between the guess and actual
            coordinates.
            score (int): the current round score.
            average_score (int): the average score of the played rounds.
        """
        if not self._guess_coords:
            raise ValueError("No guess coordinates set")

        # if not self.Marker.correct_location:
        #     raise ValueError("Correct location not set")

        # Compute stats
        self.distance = self._stats.calculate_distance(
            self.guess_coords, self.correct_location
        )
        self.score = self._stats.round_score(self.distance)
        self.average_score = self._stats.get_average_score()

        # Draw the correct marker (which will also draw the line)
        self._gamepins.draw_correct_marker(
            self.coord_file, self.images_dir, self.image_index
        )

    @property
    def image_index(self):
        """Make _image_index a property, not a private attribute."""
        return self._image_index

    @property
    def correct_location(self):
        """Make _correct_location a property, not a private attribute."""
        return self._correct_location

    @property
    def guess_coords(self):
        """Make _guess_coords a property, not a private attribute."""
        return self._guess_coords

    @property
    def distance(self):
        """Make _distance a property, not a private attribute."""
        return self._distance

    @property
    def score(self):
        """Make _score a property, not a private attribute."""
        return self._score

    @property
    def average_score(self):
        """Make _average_score a property, not a private attribute."""
        return self._average_score


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
        self._guess_coords = guess_coords
        self._actual_coords = actual_coords
        self._distance = None
        self._score = None
        self._average_score = None

    @property
    def next_guess(self):
        """Make _guess_coords a property, not a private attribute."""
        return self._guess_coords

    @property
    def next_actual(self):
        """Make _actual_coords a property, not a private attribute."""
        return self._actual_coords

    @property
    def distance(self):
        """Make _distance a property, not a private attribute."""
        return self._distance

    @property
    def score(self):
        """Make _score a property, not a private attribute."""
        return self._score

    @property
    def average_score(self):
        """Make _average_score a property, not a private attribute."""
        return self._average_score

    def calculate_distance(self):
        """
        A static method calculating distance in meters between the guess and
        answer.

        Returns:
            distance (int): the distance between the guess and the answer.
        """
        # Haversine formula for distance calculation
        lat1, lon1 = radians(self.next_guess[0]), radians(self.next_guess[1])
        lat2, lon2 = radians(self.next_actual[0]), radians(self.next_actual[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        RADIUS_OF_EARTH = 6371000  # meters
        distance = RADIUS_OF_EARTH * c

        return distance

    def round_score(self, distance):
        """
        Computes round score on a scale of 0 to 5000 points.

        Returns:
            score (int): the round score.
        """
        HIGHEST_SCORE = 5000
        SIGMA = 250000  # Width of bell curve
        score = round(
            HIGHEST_SCORE * math.exp(-0.5 * pow((distance / SIGMA), 2))
        )
        return score

    def get_average_score(self):
        """
        Calculate the average score across all rounds that have been played so
        far.

        Return:
            average_score (int): the player's average score.
        """
        if not self.rounds:
            return 0
        dist = self.calculate_distance()
        score = self.round_score(dist)
        self.rounds.append(score)

        average_score = sum(self.rounds // len(self.rounds))
        return average_score
