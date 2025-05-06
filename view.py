"""Manipulates all UI"""

import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from model import Marker, ScoreBoard
from controller import GameController
import os
import traceback


class GameUI:
    """
    Updates display based on user's inputs and game status.

    Attributes:
        Controller: all methods and attributes from class Controller.
        Marker: all methods and attributes from class Model.
        guess_confirmed (bool): whether or not a valid guess has been
        confirmed.
        score_text (str): points earned from a given round.
        average_score (str): mean score earned across the rounds played.
        distance_text (str): distance between the user's guess and the
        correct location.
        coord_file (str): path to the coords.csv file.
        image_dir (str): path to the Google Street View images
        subfolder.
        html_path (str): html path to the folium map.
        coord_text (str): inputted guess coordinates.
        image_index (int): index of the generated image.

        coords_box (pygame.Rect): rectangle textbox for users to input their
        guess coordinates.
        coords_color_inactive (pygame.Color): textbox color when inactive.
        coords_color_active (pygame.Color): textbox color when active.
        coords_color (pygame.Color): current textbox color.
        active (bool): whether or not the user has clicked on the textbox.
        coord_input_text (str): textbox input coordinates

        screen (pygame.Surface): pygame window.
        clock (pygame.time): frame rate of pygame window.
        background_color (tuple): tuple of 3 integers for RGB of pygame window.
        font (pygame.font): font style of text objects.

        confirm_button (Button): button to confirm user's guess.
        next_button (Button): button to move to the next round.


    """

    def __init__(self, controller):
        """
        Loads necessary classes. Defines scoreboard and image/map attributes to
        reflect model state.
        """
        # Load necessary classes
        self.Controller = GameController()
        self.Marker = Marker()

        # Initialize guess_confirmed boolean
        self.guess_confirmed = False

        # Initialize scoreboard stats
        self.score_text = ""
        self.average_score_text = ""
        self.distance_text = ""

        # Initialize image path and index
        self.coord_file = "dataset/coord.csv"
        self.image_dir = "dataset/images"
        self.image_index = 1
        # Initalize map path
        self.html_path = "map.html"

        self.coord_text = ""

        # Set textbox variables
        self.coords_box = pygame.Rect(525, 510, 250, 40)
        self.coords_color_inactive = pygame.Color("gray")
        self.coords_color_active = pygame.Color("dodgerblue2")
        self.coords_color = self.coords_color_inactive
        self.active = False
        self.coord_input_text = ""

        # Start the round
        self.Controller.start_round()

        # Intialize the UI
        self.initialize_ui()

    def initialize_ui(self):
        """
        Initializes pygame window and unchanging objects (textbox, buttons).
        """
        self.initialize_pygame()
        self.initialize_buttons()

    def initialize_pygame(self):
        """
        Opens pygame window.
        """
        # Set window position to left side of screen
        x, y = 0, 0
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
        # Set window variables
        pygame.init()
        self.screen = pygame.display.set_mode((1060, 700))
        pygame.display.set_caption("GeoGuessr")
        self.clock = pygame.time.Clock()
        self.background_color = (245, 245, 245)  # light gray
        self.font = pygame.font.Font(None, 36)

    def initialize_buttons(self):
        """
        Creates "confirm guess" and "next round" buttons.
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

        # # this is for the textbox for the lat and long thingie
        # self.coord_box = TextBox(
        #     self.screen,
        #     550,
        #     700,
        #     250,
        #     40,
        #     fontSize=20,
        #     borderColour=(0, 0, 0),
        #     textColour=(0, 0, 0),
        #     # placeholderText="Paste coordinates like: 42.36, -71.05",
        # )

    # def on_confirm(self):
    #     """
    #     this shit not working yet, but this would help with scoreboard stuff and also making the
    #     confirm button work
    #     """
    #     if not self.guess_confirmed:
    #         distance, score = self.controller.handle_guess()
    #         self.score_text = f"Score: {score}"
    #         self.distance_text = f"Distance: {distance/1000:.1f}km"
    #         self.guess_confirmed = True

    #     self.Marker.draw_correct_marker(
    #         self.coord_file, self.image_dir, self.image_index
    #     )

    def on_confirm(self):
        """
        On-click function for "confirm guess" button.

        Raises:
            ValueError: If input is missing, two numbers aren't given, or
            coordinates are out of range.
            Exception: Unexpected errors during processing.
        """
        if not self.guess_confirmed:
            try:
                input_text = self.coord_input_text.strip()
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
                self.Controller.Marker.guess_coords = (lat, lon)

                # This will handle the distance calculation and marker drawing
                distance, score, average_score = self.Controller.handle_guess()

                self.coord_text = f"Guess: ({lat:.4f}, {lon:.4f})"
                self.score_text = f"{score} points"
                self.average_score_text = f"{average_score} points"
                self.distance_text = f"{distance / 1000:.1f} km"
                self.guess_confirmed = True

                # Clear input
                self.coord_input_text = ""

            except ValueError as ve:
                self.coord_text = f"Error: {str(ve)}"
                print(f"❌ Validation error: {ve}")
            except Exception as e:
                self.coord_text = "Error processing guess"
                print(f"❌ Unexpected error: {e}\n{traceback.format_exc()}")

    def on_next_round(self):
        """
        On-click function for "next round" button.
        """
        self.Controller.start_round()
        self.score_text = ""
        self.average_score_text = ""
        self.distance_text = ""
        self.guess_confirmed = False

    def load_image(self, image_path):
        """
        Loads round image.

        Args:
            image_path (str): path to randomly generated image for a given
            round.
        """
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (450, 500))

    def update_display(self, events):
        """
        Updates display after user inputs.
        """
        # Clear the screen
        self.screen.fill(self.background_color)

        # --- Display current round's image ---
        current_image = self.load_image(
            os.path.join(
                "dataset", "images", f"{self.Controller.image_index}.png"
            )
        )
        if current_image:
            self.screen.blit(current_image, (50, 50))  # Adjust as needed

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

    def run(self):
        """
        Runs the pygame loop.
        """
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box, update coords_box
                    # status to active
                    if self.coords_box.collidepoint(event.pos):
                        self.active = True
                    else:
                        self.active = False
                    self.coords_color = (
                        self.coords_color_active
                        if self.active
                        else self.coords_color_inactive
                    )
                if event.type == pygame.KEYDOWN and self.active:
                    # If user pressed return, enter the input text
                    if event.key == pygame.K_RETURN:
                        print("Pressed Enter: ", self.coord_input_text)
                    # If user pressed backspace, delete last character of input
                    elif event.key == pygame.K_BACKSPACE:
                        self.coord_input_text = self.coord_input_text[:-1]
                    else:
                        self.coord_input_text += event.unicode

            self.update_display(events)
            self.clock.tick(60)

        pygame.quit()
