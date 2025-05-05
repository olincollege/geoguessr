from model import Marker, ScoreBoard
import random
import webbrowser
import os
import traceback


class GameController:
    def __init__(self):
        self.Marker = Marker()
        self.Scoreboard = ScoreBoard()
        self.current_round = 0
        self.image_index = 1
        self.coord_file = "funny_dataset/coord.csv"
        self.image_dir = "funny_dataset/images"
        self.html_path = "map.html"

    def set_correct_location(self, image_index):
        """Helper method to set the correct location from CSV"""
        try:
            with open(self.coord_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if image_index >= len(lines):
                raise IndexError(f"Image index {image_index} out of range")

            line = lines[image_index].strip()
            parts = line.split(",")
            if len(parts) < 2:
                raise ValueError(f"Invalid coordinate format: {line}")

            lat, lon = map(float, parts[:2])
            self.Marker.correct_location = (lat, lon)

        except Exception as e:
            print(f"❌ Error setting correct location: {e}")
            raise

    def start_round(self):
        """Initialize new round with random location"""
        self.Marker.clear_markers()
        images = os.listdir(self.image_dir)
        self.image_index = random.randint(0, len(images) - 1)

        # Set correct location first
        self.set_correct_location(self.image_index)

        self.Marker.draw_guess_marker()
        self.current_round += 1

        self.Marker.map.save(self.html_path)

        webbrowser.open(f"file://{os.path.abspath(self.html_path)}", new=0)

    def handle_guess(self):
        """Process player's guess and return distance and score"""
        if not self.Marker.guess_coords:
            raise ValueError("No guess coordinates set")

        if not self.Marker.correct_location:
            raise ValueError("Correct location not set")

        try:
            distance = self.Scoreboard.calculate_distance(
                self.Marker.guess_coords, self.Marker.correct_location
            )
            score = self.Scoreboard.round_score(distance)

            # Draw the correct marker (which will also draw the line)
            self.Marker.draw_correct_marker(
                self.coord_file, self.image_dir, self.image_index
            )

            self.Scoreboard.add_round(
                self.Marker.guess_coords, self.Marker.correct_location
            )

            average_score = self.Scoreboard.get_average_score()

            return distance, score, average_score

        except Exception as e:
            print(f"❌ Error handling guess: {e}")
            raise

    def get_current_image_path(self):
        """Get path of current round's image"""
        return os.path.join(self.image_dir, f"{self.image_index}.jpg")
