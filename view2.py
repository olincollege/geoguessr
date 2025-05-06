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
    def __init__(self, controller, guess_coords):
        self.controller = controller
        self.guess_coords = []

    def draw_correct_marker(
        self, csv_path, image_dir, image_index, guess_coords
    ):
        """Show correct location marker after guess"""
        image_index = list(range(10000))
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

        except Exception as e:
            print(f"❌ Error drawing correct marker: {e}")
            raise

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


class GameRunner:

    def __init__(self, controller):
        self.controller = controller

    def run(
        self,
        coords_box,
        coords_color_active,
        coords_color_inactive,
        coord_input_text,
        update_display,
        clock,
    ):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box
                    if coords_box.collidepoint(event.pos):
                        self.active = True
                    else:
                        self.active = False
                    coords_color = (
                        coords_color_active
                        if self.active
                        else coords_color_inactive
                    )

                if event.type == pygame.KEYDOWN and self.active:
                    if event.key == pygame.K_RETURN:
                        print("Pressed Enter: ", coord_input_text)
                    elif event.key == pygame.K_BACKSPACE:
                        coord_input_text = coord_input_text[:-1]
                    else:
                        coord_input_text += event.unicode

            update_display(events)
            clock.tick(60)

        pygame.quit()


class GameUI:
    def __init__(self, image_index, GamePins, Setup, GameUI):
        self._image_index = image_index
        self._GamePins = GamePins
        self._Setup = Setup
        self._GameUI = GameUI

        self.initialize_pygame()
        self.initialize_ui()
        self.guess_confirmed = False
        self.score_text = ""
        self.distance_text = ""
        self.coord_file = "funny_dataset/coord.csv"
        self.images_dir = "dataset/coords.csv"
        self.html_path = "map.html"
        coord_input_text = ""

        # textbox variables
        self.coords_box = pygame.Rect(550, 700, 250, 40)
        self.coords_color_inactive = pygame.Color("gray")
        self.coords_color_active = pygame.Color("dodgerblue2")
        self.coords_color = self.coords_color_inactive
        self.active = False
        self.coord_input_text = ""

    def initialize_pygame(self):
        """
        open the window
        """
        # Set window position to left side of screen
        x, y = 0, 0
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"

        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("GeoGuessr")
        self.clock = pygame.time.Clock()
        self.background_color = (245, 245, 245)  # light gray
        self.font = pygame.font.Font(None, 36)

    def initialize_ui(self):
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
            700,
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
            700,
            200,
            50,
            text="Next Round",
            **button_params,
            onClick=self.on_next_round,
        )

    def on_confirm(self, coord_input_text):
        if not self.guess_confirmed:
            try:
                input_text = coord_input_text.strip()
                print(f"[DEBUG] Raw input: '{input_text}'")

                if not input_text:
                    raise ValueError("No coordinates entered.")

                # Parse coordinates
                parts = [
                    p.strip() for p in input_text.replace(" ", "").split(",")
                ]
                if len(parts) < 2:
                    parts = input_text.split()

                print(f"[DEBUG] Parsed parts: {parts}")

                if len(parts) != 2:
                    raise ValueError(
                        "Please enter exactly two numbers (lat and lon)."
                    )

                lat = float(parts[0])
                lon = float(parts[1])

                # Validate coordinate ranges
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Invalid coordinate ranges")

                # Save guess
                self._GamePins.guess_coords = [lat, lon]

                # This will handle the distance calculation and marker drawing
                distance, score = self._Setup.handle_guess()

                coord_input_text = f"Guess: ({lat:.4f}, {lon:.4f})"
                self.score_text = f"Score: {score}"
                self.distance_text = f"Distance: {distance / 1000:.1f} km"
                self.guess_confirmed = True

                # Clear input
                coord_input_text = ""

            except ValueError as ve:
                coord_input_text = f"Error: {str(ve)}"
                print(f"❌ Validation error: {ve}")
            except Exception as e:
                coord_input_text = "Error processing guess"
                print(f"❌ Unexpected error: {e}\n{traceback.format_exc()}")

    # @property
    # def coord_input_text(self):
    #     return self._coord_input_text

    def on_next_round(self):
        """
        when next_round is clicked
        """
        self._Setup.start_round()
        self.score_text = ""
        self.distance_text = ""
        self.guess_confirmed = False

    def display_image(self, image_path):
        image = pygame.image.load(image_path)
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

        # Draw text entered
        txt_surface = self.font.render(coord_input_text, True, (0, 0, 0))
        width = max(250, txt_surface.get_width() + 10)
        coords_box.w = width
        self.screen.blit(txt_surface, (coords_box.x + 5, coords_box.y + 5))

        # Draw the rect
        pygame.draw.rect(self.screen, coords_color, coords_box, 2)

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
