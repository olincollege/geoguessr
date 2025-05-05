import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from model import Marker, ScoreBoard
from controller import GameController
import os


class GameUI:
    def __init__(self, controller):
        self.controller = controller
        self.Marker = Marker()
        self.initialize_pygame()
        self.initialize_ui()
        self.guess_confirmed = False
        self.score_text = ""
        self.distance_text = ""
        self.coord_file = "funny_dataset/coord.csv"
        self.image_dir = "funny_dataset/images"
        self.html_path = "map.html"
        self.coord_text = ""

        self.image_index = 1

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
        if not self.guess_confirmed:
            try:
                input_text = self.coord_input_text.strip()
                print(f"[DEBUG] Raw input: '{input_text}'")

                # Reject completely empty input
                if not input_text:
                    raise ValueError("No coordinates entered.")

                # Normalize separators
                if "," in input_text:
                    parts = [p.strip() for p in input_text.split(",")]
                else:
                    parts = [p.strip() for p in input_text.split()]

                print(f"[DEBUG] Parsed parts: {parts}")

                if len(parts) != 2 or not all(parts):
                    raise ValueError(
                        "Please enter two valid numbers (lat and lon)."
                    )

                lat = float(parts[0])
                lon = float(parts[1])

                # Save guess
                self.controller.Marker.guess_coords = (lat, lon)

                # Handle guess (distance, score)
                distance, score = self.controller.handle_guess()
                self.coord_text = f"Guess: ({lat:.4f}, {lon:.4f})"
                self.score_text = f"Score: {score}"
                self.distance_text = f"Distance: {distance / 1000:.1f} km"
                self.guess_confirmed = True

                # Save updated map
                self.controller.Marker.map.save(self.controller.html_path)

                # Clear input
                self.coord_input_text = ""

            except ValueError as ve:
                self.coord_text = f"Input error: {ve}"
            except Exception as e:
                print("❌ Unexpected error confirming guess:", e)
                self.coord_text = (
                    "Invalid coordinates! Try format: 42.36, -71.05"
                )

    def on_next_round(self):
        """
        when next_round is clicked
        """
        self.controller.start_round()
        self.score_text = ""
        self.distance_text = ""
        self.guess_confirmed = False

    def display_image(self, image_path):
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (500, 500))

    def update_display(self, events):
        # Clear the screen
        self.screen.fill(self.background_color)

        # --- Display current round's image ---
        current_image = self.display_image(
            os.path.join(
                "funny_dataset", "images", f"{self.controller.image_index}.jpg"
            )
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
        txt_surface = self.font.render(self.coord_input_text, True, (0, 0, 0))
        width = max(250, txt_surface.get_width() + 10)
        self.coords_box.w = width
        self.screen.blit(
            txt_surface, (self.coords_box.x + 5, self.coords_box.y + 5)
        )

        # Draw the rect
        pygame.draw.rect(self.screen, self.coords_color, self.coords_box, 2)

        # --- Update All Widgets ---
        pygame_widgets.update(events)

        # --- Update Display ---
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box
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
                    if event.key == pygame.K_RETURN:
                        print("Pressed Enter: ", self.coord_input_text)
                    elif event.key == pygame.K_BACKSPACE:
                        self.coord_input_text = self.coord_input_text[:-1]
                    else:
                        self.coord_input_text += event.unicode

            self.update_display(events)
            self.clock.tick(60)

        pygame.quit()
