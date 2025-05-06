"""View file"""

import folium
from folium import IFrame
import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from model import Marker, ScoreBoard
from controller import GameController
import os
import traceback


class GamePins:
    def __init__(self, guess_coords):
        self.guess_marker = None
        self.correct_marker = None
        self.line = None
        self.guess_coords = None
        self.correct_location = None
        self.click_control = None

    def draw_correct_marker(
        self, csv_path, image_dir, image_index, guess_coords
    ):
        """Show correct location marker after guess"""
        # If you really meant to reset image_index to 0–9999, do it explicitly:
        image_index = list(range(10000))

        # Remove existing elements if they exist
        if self.correct_marker and self.correct_marker in self.map._children:
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
        self.correct_location = [lat, lon]

        # Add correct marker
        image_path = os.path.join(image_dir, f"{image_index}.png")
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
        if guess_coords and self.correct_location:
            self.line = folium.PolyLine(
                [guess_coords, self.correct_location],
                color="blue",
                weight=2.5,
                opacity=1,
            )
            self.line.add_to(self.map)

        return self.map

    @property
    def guess_coords(self):
        return self._guess_coords

    def clear_markers(self):
        """
        Reset the map to the original clean map (no markers or lines).
        """
        # Reset to original blank map
        self.map_og = folium.Map(location=[0, 0], zoom_start=2)

        # Clear stored data
        self.guess_marker = None
        self.correct_marker = None
        self.line = None
        guess_coords = []
        self.correct_location = []
        self.click_control = None


# class GameRunner:

#     def __init__(self, controller):
#         self.controller = controller

#     def run(
#         self,
#         coords_box,
#         coords_color_active,
#         coords_color_inactive,
#         coord_input_text,
#         update_display,
#         clock,
#     ):
#         running = True
#         while running:
#             events = pygame.event.get()
#             for event in events:
#                 if event.type == pygame.QUIT:
#                     running = False

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     # If the user clicked on the input_box
#                     if coords_box.collidepoint(event.pos):
#                         self.active = True
#                     else:
#                         self.active = False
#                     coords_color = (
#                         coords_color_active
#                         if self.active
#                         else coords_color_inactive
#                     )

#                 if event.type == pygame.KEYDOWN and self.active:
#                     if event.key == pygame.K_RETURN:
#                         print("Pressed Enter: ", coord_input_text)
#                     elif event.key == pygame.K_BACKSPACE:
#                         coord_input_text = coord_input_text[:-1]
#                     else:
#                         coord_input_text += event.unicode

#             update_display(events)
#             clock.tick(60)

#         pygame.quit()


class GameUI:
    """
    Updates display based on user's inputs and game status.
    """

    def __init__(self, image_index, GamePins, Setup):
        self._image_index = image_index
        self._GamePins = GamePins
        self._Setup = Setup

        self.initialize_pygame()
        self.initialize_ui()
        self.guess_confirmed = False
        self.score_text = ""
        self.distance_text = ""
        self.coord_file = "dataset/coord.csv"
        self.images_dir = "dataset/images"
        self.html_path = "map.html"
        coord_input_text = ""

        # textbox variables
        self.coords_box = pygame.Rect(525, 510, 250, 40)
        self.coords_color_inactive = pygame.Color("gray")
        self.coords_color_active = pygame.Color("dodgerblue2")
        self.coords_color = self.coords_color_inactive
        self.active = False
        self.coord_input_text = ""

    def initialize_ui(self):
        self.initialize_pygame(self)
        self.initialize_buttons(self)

    def initialize_pygame(self):
        """
        open the window
        """
        # Set window position to left side of screen
        x, y = 0, 0
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"

        pygame.init()
        self.screen = pygame.display.set_mode((1060, 700))
        pygame.display.set_caption("GeoGuessr")
        self.clock = pygame.time.Clock()
        self.background_color = (245, 245, 245)  # light gray
        self.font = pygame.font.Font(None, 36)

    def initialize_buttons(self):
        # Button Parameters
        button_params = {
            "font": pygame.font.SysFont("Arial", 20),
            "margin": 20,
            "inactiveColour": (100, 150, 200),  # Blue color
            "hoverColour": (80, 130, 180),
            "pressedColour": (60, 110, 160),
            "textColour": (255, 255, 255),  # White text
            "radius": 5,
        }

        # Confirm Guess Button
        self.confirm_button = Button(
            self.screen,
            50,
            600,
            200,
            50,
            text="Confirm Guess",
            **button_params,
            onClick=self.on_confirm,
        )

        # Next Round Button
        self.next_button = Button(
            self.screen,
            300,
            600,
            200,
            50,
            text="Next Round",
            **button_params,
            onClick=self.on_next_round,
        )

    def display_image(self, image_path):
        image = pygame.image.load(self.image_path)
        return pygame.transform.scale(image, (500, 500))

    def update_display(
        self,
        events,
        coords_box,
        coords_color,
        coord_input_text,
        coord_text,
        score_text,
        average_score_text,
        distance_text,
        guess_confirmed,
    ):
        # Clear the screen
        self.screen.fill(self.background_color)

        # --- Display current round's image ---
        current_image = self.display_image(
            os.path.join("funny_dataset", "images", f"{self._image_index}.jpg")
        )
        if current_image:
            self.screen.blit(current_image, (200, 50))  # Adjust as needed

        # --- Display Score and Distance ---
        if self.score_text:
            score_surface = self.font.render(self.score_text, True, (0, 0, 0))
            self.screen.blit(score_surface, (50, 650))
        if self.distance_text:
            distance_surface = self.font.render(
                self.distance_text, True, (0, 0, 0)
            )
            self.screen.blit(distance_surface, (300, 650))

        # Draw input box label
        label_surface = self.font.render(
            "Enter lat & lon (e.g., 42.36, -71.05 OR 42.36 -71.05):",
            True,
            (0, 0, 0),
        )
        self.screen.blit(label_surface, (550, 670))

        # --- Display Input Box ---
        label_surface = self.font.render(
            "Enter coordinates (e.g. lat, lon OR lat lon):",
            True,
            (0, 0, 0),
        )
        self.screen.blit(label_surface, (525, 475))

        # Draw text entered into coords_box
        txt_surface = self.font.render(self.coord_input_text, True, (0, 0, 0))
        width = max(250, txt_surface.get_width() + 10)
        self.coords_box.w = width
        self.screen.blit(
            txt_surface, (self.coords_box.x + 5, self.coords_box.y + 5)
        )

        # Draw the rect for coords_box
        pygame.draw.rect(self.screen, self.coords_color, self.coords_box, 2)

        # --- Update All Widgets ---
        pygame_widgets.update(events)

        # --- Update Display ---
        pygame.display.flip()

    @property
    def coord_text(self):
        return self._coord_text

    @property
    def score_text(self):
        return self._score_text

    @property
    def average_score_text(self):
        return self._average_score_text

    @property
    def distance_text(self):
        return self._distance_text

    @property
    def guess_confirmed(self):
        return self._guess_confirmed
