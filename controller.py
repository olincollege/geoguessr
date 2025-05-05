from model import Marker, ScoreBoard
import random
import webbrowser
import os


class GameController:
    def __init__(self):
        self.Marker = Marker()
        self.Scoreboard = ScoreBoard()
        self.current_round = 0
        self.image_index = None

        # Hardcoded to use funny_dataset, will change for the other one
        self.coord_file = "funny_dataset/coord.csv"
        self.image_dir = "funny_dataset/images"
        self.html_path = "map.html"

    def start_round(self):
        """Initialize new round with random location from funny_dataset"""
        # Clear previous markers but keep map
        self.Marker.clear_markers()

        self.image_index = random.randint(
            0, len(os.listdir(self.image_dir)) - 1
        )

        # this is the thingie that was making me tweak
        # self.Marker.draw_correct_marker(
        #     self.coord_file, self.image_dir, self.image_index
        # )
        self.Marker.draw_guess_marker()
        self.current_round += 1

        # Save and open the map (right side of screen)
        self.Marker.map.save(self.html_path)
        webbrowser.open(f"file://{os.path.abspath(self.html_path)}", new=0)

    def handle_guess(self):
        """Process player's guess and return distance and score"""
        if not self.Marker.guess_coords:
            return 0, 0

        distance = self.Scoreboard.calculate_distance(
            self.Marker.guess_coords, self.Marker.correct_location
        )
        score = self.Scoreboard.round_score(distance)

        # Reveal solution on existing map
        self.Marker.draw_correct_marker(
            self.coord_file, self.image_dir, self.image_index
        )

        self.Scoreboard.add_round(
            self.Marker.guess_coords, self.Marker.correct_location
        )

        return distance, score

    def get_current_image_path(self):
        """Get path of current round's image"""
        return os.path.join(self.image_dir, f"{self.image_index}.jpg")
