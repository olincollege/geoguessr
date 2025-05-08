"""View of Model, View, Controller Architecture"""

import pygame


class View:
    """
    Draws the image, buttons, textbox, scoreboard, and map to the
    screen. Updates the display as the controller's inputs change the
    model state.

    Attributes:
        model (Geoguessr): All model instances.
    """

    def __init__(self, model):
        """
        Initializes all pygame display components.

        Args:
            model (Geoguessr): All model instances.
        """
        self._model = model

        # Screen
        self._width = 1771
        self._height = 700
        self._screen = pygame.display.set_mode((self._width, self._height))

        # Fonts
        self._big_font = pygame.font.Font("bpg-mrgvlovani-webfont.ttf", 50)
        self._medium_font = pygame.font.Font("bpg-mrgvlovani-webfont.ttf", 35)
        self._small_font = pygame.font.Font("bpg-mrgvlovani-webfont.ttf", 20)

        # Colors
        self._black = (0, 0, 0)
        self._blue = (0, 0, 100)
        self._green = (0, 100, 0)
        self._red = (100, 0, 0)
        self._gray = (200, 200, 200)

        # Buttons
        self._submit_button = pygame.Rect((325, 575), (250, 50))
        self._next_round_button = pygame.Rect((325, 575), (250, 50))
        self._error_button = pygame.Rect((325, 575), (250, 50))

        # Map
        self._map_path = "map.jpeg"
        self._map_size = (1021, 510)
        self._map = pygame.image.load(self._map_path)

        # Scoreboard
        self._scoreboard_width = 1021
        self._scoreboard_height = 80
        self._scoreboard = pygame.Surface(
            (self._scoreboard_width, self._scoreboard_height)
        )
        self._scoreboard_title = self._medium_font.render(
            "SCOREBOARD", True, (0, 0, 0)
        )

        # Scoreboard's stats
        self._stats_text = self._small_font.render("", True, (0, 0, 0))
        self._score_text = ""
        self._average_score_text = ""
        self._distance_text = ""
        self._distance_surface = self._small_font.render(
            self._distance_text, True, (0, 0, 0)
        )
        self._score_surface = self._small_font.render(
            self._distance_text, True, (0, 0, 0)
        )
        self._average_surface = self._small_font.render(
            self._distance_text, True, (0, 0, 0)
        )

        # Image
        self._image_size = (600, 600)
        self._image = None

        # User input box
        self._passive_color = (50, 50, 50)
        self._active_color = (250, 250, 250)
        self._input_rect = pygame.Rect((325, 520), (300, 45))
        self._input_active = False

    def draw_guess(self):
        """
        When the user can see the image and map and input a guess.
        """
        self._screen.fill(self._black)
        self.draw_image()
        self.draw_map()
        self.draw_submit_button()
        self.draw_input_rect()

    def draw_score(self):
        """
        When the user can see the image and map and confirm the
        accuracy of their guess with the scoreboard and markers/line
        on the map.
        """
        self._screen.fill(self._black)
        self.draw_image()
        self.draw_map()
        self.draw_guess_marker()
        self.draw_correct_marker()
        self.draw_line()
        self.draw_scoreboard()
        self.draw_next_round_button()

    def draw_error(self):
        """
        When the user can see the image and map and gives an invalid
        input.
        """
        self.draw_error_button()

    def draw_error_button(self):
        """
        Draws a red button for the "error" game mode.
        """
        pygame.draw.rect(self._screen, (255, 0, 0), self._error_button)

    def draw_input_rect(self):
        """
        Draws an input textbox that changes colors depending on if
        its active or not.
        """
        if self._input_active:
            color = self._active_color
        else:
            color = self._passive_color
        text_surface = self._medium_font.render(
            self._model.user_text, True, self._black
        )
        self._input_rect.w = max(100, text_surface.get_width() + 5)
        pygame.draw.rect(self._screen, color, self._input_rect)
        self._screen.blit(
            text_surface, (self._input_rect.x + 2, self._input_rect.y + 2)
        )

    def toggle_input_rect(self):
        """
        Updates whether or not the input textbox is active.
        """
        self._input_active = not self._input_active

    def draw_submit_button(self):
        """
        Draws a blue button for the "guess" game mode.
        """
        color = (255, 0, 0) if self._model.input_error else self._blue
        pygame.draw.rect(self._screen, color, self._submit_button)

    def draw_next_round_button(self):
        """
        Draws a green button for the "score" game mode.
        """
        pygame.draw.rect(self._screen, self._green, self._next_round_button)

    def draw_image(self):
        """
        Draws the image of a random location.
        """
        self._image = pygame.image.load(self._model.image_path)
        self._screen.blit(
            pygame.transform.scale(self._image, self._image_size), (50, 50)
        )

    def draw_map(self):
        """
        Draws the world map scaled to half of its original size.
        """
        self._screen.blit(
            pygame.transform.scale(self._map, self._map_size), (700, 140)
        )

    def draw_guess_marker(self):
        """
        Draws a marker for the user's guess.
        """
        pygame.draw.circle(
            self._screen,
            self._red,
            (
                700 + int(self._model.guess_lon_pixels),  # offset X
                140 + int(self._model.guess_lat_pixels),  # offset Y
            ),
            5,
        )

    def draw_correct_marker(self):
        """
        Draws a marker for the answer.
        """
        pygame.draw.circle(
            self._screen,
            self._green,
            (
                700 + int(self._model.correct_lon_pixels),  # offset X
                140 + int(self._model.correct_lat_pixels),  # offset Y
            ),
            5,
        )

    def draw_line(self):
        """
        Draws a line connecting the user's guess and the answer.
        """
        pygame.draw.line(
            self._screen,
            self._black,
            (
                700 + int(self._model.guess_lon_pixels),
                140 + int(self._model.guess_lat_pixels),
            ),  # Offset to account for map's position on the screen
            (
                700 + int(self._model.correct_lon_pixels),
                140 + int(self._model.correct_lat_pixels),
            ),  # Offset to account for map's position on the screen
            2,
        )

    def get_stats_text(self):
        """
        Collects the stats of the scoreboard as text objects.
        """
        # Collect strings for stats
        self._distance_text = f"Distance: {self._model.distance} meters"
        self._score_text = f"Score: {self._model.current_score} points"
        self._average_score_text = (
            f"Average Score: {self._model.average_score} points"
        )
        # Render strings into surfaces
        self._distance_surface = self._small_font.render(
            self._distance_text, True, (0, 0, 0)
        )
        self._score_surface = self._small_font.render(
            self._score_text, True, (0, 0, 0)
        )
        self._average_surface = self._small_font.render(
            self._average_score_text, True, (0, 0, 0)
        )

    def draw_scoreboard(self):
        """
        Draws the scoreboard with the current round's stats.
        """
        self.get_stats_text()
        self._scoreboard.fill(self._gray)
        self._screen.blit(self._scoreboard, (700, 50))

        # Draw title
        title_rect = self._scoreboard_title.get_rect(topleft=(10, 5))
        self._scoreboard.blit(self._scoreboard_title, title_rect)

        # Draw individual stats below title
        self._scoreboard.blit(self._distance_surface, (10, 50))
        self._scoreboard.blit(self._score_surface, (400, 50))
        self._scoreboard.blit(self._average_surface, (700, 50))

        # Draw the entire scoreboard onto the screen
        self._screen.blit(self._scoreboard, (700, 50))

    @property
    def submit_button(self):
        """Returns submit_button instance."""
        return self._submit_button

    @property
    def next_round_button(self):
        """Returns next_round_button instance."""
        return self._next_round_button

    @property
    def error_button(self):
        """Returns error_button instance."""
        return self._error_button

    @property
    def input_active(self):
        """Returns input_active instance."""
        return self._input_active

    @property
    def input_rect(self):
        """Returns input_rect instance."""
        return self._input_rect
