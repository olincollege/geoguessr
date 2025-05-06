"""View file"""

import os
import folium
from folium import IFrame
import pygame
import pygame_widgets
from pygame_widgets.button import Button
from model2 import Setup
from controller2 import InteractiveWidgets


class GamePins:
    """
    Displaying marker for correct location for a given round on Folium map.

    Attributes:
        InteractiveWidgets: All attributes and methods from InteractiveWidgets class.
        guess_coords (list): Player's guess coordinates.
    """

    def __init__(self, InteractiveWidgets, guess_coords):
        self._InteractiveWidgets = InteractiveWidgets
        self.guess_coords = []

    def draw_correct_marker(self, csv_path, image_dir, image_index):
        """
        Show correct location marker after guess

        Args:
            csv_path (str): the path to coords.csv in dataset.
            image_dir (str): the path to the image directory in dataset.
            image_index (int): the index of the generated round image.

        Raises:
            IndexError: Image index out of range of coords.csv.
            ValueError: Coordinates not split into lat and lon.
            FileNotFoundError: Image path not found.
        """
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
        self.guess_coords = []
        self.correct_location = []
        self.click_control = None


class GameRunner:
    """
    Runs pygame.

    Attributes:
        InteractiveWidgets: all attributes and methods from InteractiveWidgets
        class.
        GameUI: all attributes and methods from InteractiveWidgets
        class.
    """

    def __init__(self, InteractiveWidgets, GameUI):
        self.InteractiveWidgets = InteractiveWidgets
        self.GameUI = GameUI

    def run(
        self,
        coords_box,
        coords_color_active,
        coords_color_inactive,
        coord_input_text,
        clock,
    ):
        """
        Loop through pygame.

        Args:
            coords_box (pygame.Rect): textbox to input guess coordinates.
            coords_color_active (pygame.Color): color for active textbox.
            coords_color_inactive (pygame.Color): color for inactive textbox.
            coords_input_text (str): player's inputted guess coordinates.
        """
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

            self.GameUI.update_display(events)
            clock.tick(60)

        pygame.quit()


class GameUI:
    """
    Setup for pygame display (buttons, textbox, scoreboard, image).

    AttributesL
        image_index (int): index of the generated round image.
        GamePins: all attributes and methods from GamePins class.
        Setup: all attributes and methods from Setup class.
        InteractiveWidgets: all attributes and methods from Interactive
        Widgets class.
    """

    def __init__(self, image_index, GamePins, Setup, InteractiveWidgets):
        self._image_index = image_index

        self._GamePins = GamePins
        self._Setup = Setup
        self._InteractiveWidgets = InteractiveWidgets

        # self.guess_confirmed = False
        self._score_text = None
        self._average_score_text = None
        self._distance_text = None

        # textbox variables
        self.coords_box = pygame.Rect(550, 700, 250, 40)
        self.coords_color_inactive = pygame.Color("gray")
        self.coords_color_active = pygame.Color("dodgerblue2")
        self.coords_color = self.coords_color_inactive
        self.active = False
        self._coord_input_text = None

        self.initialize_buttons()
        self.initialize_pygame()

    @property
    def coord_text(self):
        return self._coord_input_text

    @property
    def score_text(self):
        return self._score_text

    @property
    def average_score_text(self):
        return self._average_score_text

    @property
    def distance_text(self):
        return self._distance_text

    def initialize_pygame(self):
        """
        Initialize the pygame window.
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

    def initialize_buttons(self):
        """
        Initialize buttons on display.
        """
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
            onClick=self._InteractiveWidgets.on_confirm,
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
            onClick=self._InteractiveWidgets.on_next_round,
        )

    def display_image(self, image_path):
        """
        Displays generated round image onto screen.

        Returns:
            pygame.image object to show location to user.
        """
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (500, 500))

    def update_display(self, events):
        """
        Updates display based on events.

        Args:
            events occuring within pygame loop.
        """
        # Clear the screen
        self.screen.fill(self.background_color)

        # --- Display ScoreBoard ---
        # Draw the scoreboard
        scoreboard_surface = pygame.Surface((400, 400))
        scoreboard_surface.fill((255, 253, 208))

        # Draw the title
        title_surface = self.font.render("SCOREBOARD", True, (0, 0, 0))
        title_rect = title_surface.get_rect()
        title_rect.topleft = (25, 25)
        scoreboard_surface.blit(title_surface, title_rect)

        # Draw the distance
        distance_surface = self.font.render(
            "Distance: " + self.distance_text, True, (0, 0, 0)
        )
        distance_rect = distance_surface.get_rect()
        distance_rect.topleft = (25, 100)
        scoreboard_surface.blit(distance_surface, distance_rect)

        # Draw the score
        score_surface = self.font.render(
            "Round Score: " + self.score_text, True, (0, 0, 0)
        )
        score_rect = score_surface.get_rect()
        score_rect.topleft = (25, 175)
        scoreboard_surface.blit(score_surface, score_rect)

        # Draw the average score
        average_score_surface = self.font.render(
            "Average Score: " + self.average_score_text, True, (0, 0, 0)
        )
        average_score_rect = average_score_surface.get_rect()
        average_score_rect.topleft = (25, 250)
        scoreboard_surface.blit(average_score_surface, average_score_rect)

        # Blit the components and display onto the pygame window
        self.screen.blit(scoreboard_surface, (525, 50))

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
