import pygame
import pygame_widgets
from pygame_widgets.button import Button
from model import Marker, ScoreBoard
from controller import GameController
import os


class GameUI:
    def __init__(self, controller):
        self.Controller = controller
        self.initialize_pygame()
        self.initialize_ui()
        self.guess_confirmed = False
        self.score_text = ""
        self.distance_text = ""

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

    def on_confirm(self):
        """
        this shit not working yet, but this would help with scoreboard stuff and also making the
        confirm button work
        """
        if not self.guess_confirmed:
            distance, score = self.Controller.handle_guess()
            self.score_text = f"Score: {score}"
            self.distance_text = f"Distance: {distance/1000:.1f}km"
            self.guess_confirmed = True
            self.Marker.draw_correct_marker(
                self.coord_file, self.image_dir, self.image_index
            )

    def on_next_round(self):
        """
        when next_round is clicked
        """
        self.Controller.start_round()
        self.score_text = ""
        self.distance_text = ""
        self.guess_confirmed = False

    def display_image(self, image_path):
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (500, 500))

    def update_display(self):
        self.screen.fill(self.background_color)

        # Display current image
        current_image = self.display_image(
            os.path.join(
                "funny_dataset", "images", f"{self.Controller.image_index}.jpg"
            )
        )
        if current_image:
            self.screen.blit(current_image, (200, 50))

        # Display score and distance
        if self.score_text:
            score_surface = self.font.render(self.score_text, True, (0, 0, 0))
            self.screen.blit(score_surface, (50, 650))
        if self.distance_text:
            distance_surface = self.font.render(
                self.distance_text, True, (0, 0, 0)
            )
            self.screen.blit(distance_surface, (300, 650))

        # Update widgets
        events = pygame.event.get()
        pygame_widgets.update(events)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update_display()
            self.clock.tick(60)

        pygame.quit()
