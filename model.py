"""Model of Model, View, Controller Architecture"""

from math import radians, sin, cos, sqrt, atan2, exp
import random


class GeoGuessr:
    """
    Updates state of Geoguessr based on which round the player is on,
    whether a guess has been made, the stats of that round, and setup
    for the next round.
    """

    def __init__(self):
        self._num_rounds = 0
        self._mode = "guess"
        self._image_path = "dataset/images/9999.png"
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

    def add_user_text(self, user_input):
        """add user text"""
        self._user_text += user_input

    def delete_user_text(self):
        """delete user text"""
        self._user_text = self._user_text[:-1]

    def set_guess_coordinates(self, lat, lon):
        self._guess_lat = lat
        self._guess_lon = lon

    ###### this one is important
    def get_score(self):
        """changes in model after the user makes a guess"""
        # user_input = self._user_text.split()
        # if len(user_input) != 2:
        #     self.error()

        # raise ValueError("Need exactly two numbers")
        # print(f"User input: {user_input}")  # ← DEBUG
        # self._guess_lat = float(user_input[0])
        # self._guess_lon = float(user_input[1])
        self.get_pixels()
        self.calculate_distance()
        self.calculate_score()
        self.calculate_average_score()
        print(
            f"Switching to score mode with score {self._current_score}"
        )  # ← DEBUG
        self._user_text = ""
        self._mode = "score"

    def get_pixels(self):
        """converts coordinates to pixels"""
        MAP_HORIZONTAL_PIXELS = 1021
        MAP_HORIZONTAL_SECTIONS = 24
        MAP_VERTICAL_PIXELS = 510
        MAP_VERTICAL_SECTIONS = 12
        LAT_RANGE = 180
        LON_RANGE = 360

        pixels_per_lat = (MAP_HORIZONTAL_SECTIONS / LON_RANGE) * (
            MAP_HORIZONTAL_PIXELS * MAP_HORIZONTAL_SECTIONS
        )
        pixels_per_lon = (MAP_VERTICAL_SECTIONS / LAT_RANGE) * (
            MAP_VERTICAL_PIXELS * MAP_VERTICAL_SECTIONS
        )

        self._guess_lat_pixels = self._guess_lat * pixels_per_lat
        self._guess_lon_pixels = self._guess_lon * pixels_per_lon
        self._correct_lat_pixels = self._correct_lat * pixels_per_lat
        self._correct_lon_pixels = self._correct_lon * pixels_per_lon

    def calculate_distance(self):
        """
        A method calculating distance between the guess and answer by
        converting the difference in latitude and longitude
        to actual meters.

        Args:
            lat

        Returns:
            distance (int): the distance between the guess and the
            answer.
        """
        # Haversine formula for distance calculation
        lat1, lon1 = radians(self._guess_lat), radians(self._guess_lon)
        lat2, lon2 = radians(self._correct_lat), radians(self._correct_lon)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            sin(delta_lat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        earth_radius = 6371000  # meters
        self._distance = earth_radius * c

    def calculate_score(self):
        """
        Gets the score based on how accurate the user's guess is. The
        points range from 0 to 5000 points, with the score increasing
        as the distance between a user's guess and the answer
        decreases. This scoring follows a Gaussian distribution.
        """
        HIGHEST_SCORE = 5000
        SIGMA = 250000
        self._current_score = round(
            HIGHEST_SCORE * exp(-0.5 * pow((self._distance / SIGMA), 2))
        )

    def calculate_average_score(self):
        """calculate average score"""
        previous_total = self._average_score * self._num_rounds
        new_total = previous_total + self._current_score
        self._num_rounds += 1
        self._average_score = new_total / self._num_rounds

    #### this one is important
    def next_guess(self):
        """
        Generates the next image num and correct
        coordinates so that the user can guess
        again.
        """
        self.get_image_path()
        self.get_correct_coords()
        self._mode = "guess"

    def get_image_path(self):
        """
        finds a random image path
        """
        min_image = 0
        max_image = 9999
        self._image_num = random.randint(min_image, max_image)
        self._image_path = f"dataset/images/{self._image_num}.png"

    def get_correct_coords(self):
        """gets the correct lat lon coords given the image number"""
        # Open coords.csv file and read through lines
        with open("dataset/coords.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Check that image is in range
        if self._image_num >= len(lines):
            raise IndexError(f"Image index {self._image_num} out of range")
        # parse lines and split into coordinates
        line = lines[self._image_num].strip()
        parts = line.split(",")
        # define correct lat and lon
        self._correct_lat = float(parts[0])
        self._correct_lon = float(parts[1])
        print(line, self._correct_lon, self._correct_lat)

    def error(self):
        self._mode = "error"
        self._user_text = ""

    def no_error(self):
        self._mode = "guess"

    @property
    def mode(self):
        """returns mode"""
        return self._mode

    @property
    def image_path(self):
        """returns image path"""
        return self._image_path

    @property
    def distance(self):
        """returns distance"""
        return self._distance

    @property
    def current_score(self):
        """return current score"""
        return self._current_score

    @property
    def average_score(self):
        """returns average score"""
        return self._average_score

    @property
    def user_text(self):
        """returns user text"""
        return self._user_text

    @property
    def guess_lat_pixels(self):
        """returns guess lat pixels"""
        return self._guess_lat_pixels

    @property
    def guess_lon_pixels(self):
        """returns guess lat pixels"""
        return self._guess_lon_pixels

    @property
    def correct_lat_pixels(self):
        """returns guess lat pixels"""
        return self._correct_lat_pixels

    @property
    def correct_lon_pixels(self):
        """returns guess lat pixels"""
        return self._correct_lon_pixels
