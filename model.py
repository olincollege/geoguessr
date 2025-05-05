import folium
from folium import IFrame
from folium import plugins
from branca.element import MacroElement
from jinja2 import Template
import math
import os
from math import radians, sin, cos, sqrt, atan2
import traceback


class ScoreBoard:
    """Scoreboard tracking game rounds and scores."""

    def __init__(self):
        self.rounds = []
        self.current_round = 0
        self.total_score = 0

    def add_round(self, guess_coords, actual_coords):
        self.current_round += 1
        dist = self.calculate_distance(guess_coords, actual_coords)
        score = self.round_score(dist)
        self.rounds.append(
            {"round": self.current_round, "distance": dist, "score": score}
        )
        self.total_score += score
        return dist, score

    def get_average_score(self):
        if not self.rounds:
            return 0
        return self.total_score / len(self.rounds)

    @staticmethod
    def calculate_distance(guess_coords, actual_coords):
        """Haversine formula for distance calculation."""
        lat1, lon1 = radians(guess_coords[0]), radians(guess_coords[1])
        lat2, lon2 = radians(actual_coords[0]), radians(actual_coords[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        RADIUS_OF_EARTH = 6371000  # meters
        return RADIUS_OF_EARTH * c

    @staticmethod
    def round_score(distance_meters):
        """Computes round score on a scale of 0 to 5000 points."""
        HIGHEST_SCORE = 5000
        SIGMA = 250000  # Width of bell curve
        score = HIGHEST_SCORE * math.exp(
            -0.5 * pow((distance_meters / SIGMA), 2)
        )
        return round(score)


class Marker:
    def __init__(self, zoom_start=2):
        self.zoom_start = zoom_start
        self.map_og = folium.Map(
            location=[0, 0], zoom_start=self.zoom_start
        )  # inital map to go back on
        self.map = folium.Map(location=[0, 0], zoom_start=self.zoom_start)

        # all of the stupid variables
        self.guess_marker = None
        self.correct_marker = None
        self.line = None
        self.guess_coords = None
        self.correct_location = None
        self.click_control = None

    def draw_guess_marker(self):
        """
        Adds a basic LatLngPopup that shows coordinates when user clicks.
        User will then copy and paste those into the game.
        """
        self.map = folium.Map(location=[0, 0], zoom_start=self.zoom_start)
        self.map.add_child(folium.LatLngPopup())  # Built-in coordinate popup
        return self.map

    # def draw_guess_marker(self):
    #     """
    #     this is when you make your guess to put the marker down
    #     """
    #     map_var = self.map.get_name()
    #     icon_url = "https://cdn-icons-png.flaticon.com/512/684/684908.png"

    #     tpl = Template(
    #         f"""
    #     {{% macro script(this, kwargs) %}}
    #       var guessIcon = L.icon({{
    #         iconUrl: "{icon_url}",
    #         iconSize: [25, 41],
    #         iconAnchor: [12, 41],
    #         popupAnchor: [1, -34]
    #       }});

    #       var guessMarker;
    #       {map_var}.on('click', function(e) {{
    #         if (guessMarker) {{
    #           guessMarker.setLatLng(e.latlng)
    #                      .setIcon(guessIcon)
    #                      .openPopup();
    #         }} else {{
    #           guessMarker = L.marker(e.latlng, {{icon: guessIcon}})
    #                            .addTo({map_var})
    #                            .bindPopup("Your Guess:")
    #                            .openPopup();
    #         }}
    #         document.getElementById('guess_coords').textContent =
    #           JSON.stringify([e.latlng.lat, e.latlng.lng]);
    #       }});
    #     {{% endmacro %}}
    #     """
    #     )

    #     self.click_control = MacroElement()
    #     self.click_control._template = tpl

    #     # if self.click_control:
    #     #     self.map.remove_child(self.click_control)

    #     self.map.add_child(self.click_control)

    #     self.map.add_child(folium.LatLngPopup())

    #     return self.map

    def draw_correct_marker(self, csv_path, image_dir, image_index):
        """Show correct location marker after guess"""
        try:
            # Remove existing elements if they exist
            if (
                self.correct_marker
                and self.correct_marker in self.map._children
            ):
                self.map.remove_child(self.correct_marker)
            if self.line and self.line in self.map._children:
                self.map.remove_child(self.line)

            # Get correct location
            with open(csv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if image_index >= len(lines):
                raise IndexError("Image index out of range in coordinates file")

            line = lines[image_index].strip()
            parts = line.split(",")
            if len(parts) < 2:
                raise ValueError("Invalid coordinate format in CSV")

            lat, lon = map(float, parts[:2])
            self.correct_location = (lat, lon)  # Set the correct location

            # Add correct marker
            image_path = os.path.join(image_dir, f"{image_index}.jpg")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            html = f'<img src="{image_path}" width="300">'
            iframe = IFrame(html, width=320, height=240)

            self.correct_marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(iframe, max_width=320),
                icon=folium.Icon(color="red", icon="pushpin"),
            )
            self.correct_marker.add_to(self.map)

            # Only draw line if we have both points
            if self.guess_coords and self.correct_location:
                self.line = folium.PolyLine(
                    [self.guess_coords, self.correct_location],
                    color="blue",
                    weight=2.5,
                    opacity=1,
                )
                self.line.add_to(self.map)

            return self.map

        except Exception as e:
            print(f"❌ Error drawing correct marker: {e}")
            raise

    def clear_markers(self):
        """
        Reset the map to the original clean map (no markers or lines).
        """
        # Reset to original blank map
        self.map_og = folium.Map(location=[0, 0], zoom_start=self.zoom_start)

        # Clear stored data
        self.guess_marker = None
        self.correct_marker = None
        self.line = None
        self.guess_coords = None
        self.correct_location = []
        self.click_control = None
