import pygame


class View:
    def __init__(self, model):
        self._model = model

        # screen
        self._width = 1771
        self._height = 700
        self._screen = pygame.display.set_mode((self._width, self._height))

        # fonts
        self._big_font = pygame.font.Font("bpg-mrgvlovani-webfont.ttf", 50)
        self._medium_font = pygame.font.Font("bpg-mrgvlovani-webfont.ttf", 35)
        self._small_font = pygame.font.Font("bpg-mrgvlovani-webfont.ttf", 20)

        # colors
        self._black = (0, 0, 0)
        self._blue = (0, 0, 100)
        self._green = (0, 100, 0)
        self._red = (100, 0, 0)
        self._cream = (255, 253, 208)

        # buttons
        self._submit_button = pygame.Rect((325, 575), (250, 50))
        self._next_round_button = pygame.Rect((325, 575), (250, 50))
        self._error_button = pygame.Rect((325, 575), (250, 50))

        # map
        self._map_path = "map.jpeg"
        self._map_size = (1021, 510)
        self._map = pygame.image.load(self._map_path)

        # scoreboard
        self._scoreboard = pygame.Surface((510, 80))
        self._scoreboard_title = self._medium_font.render(
            "SCOREBOARD", True, (0, 0, 0)
        )
        self._score_text = ""
        self._average_score_text = ""
        self._distance_text = ""
        self._stats_text = self._small_font.render(
            "",
            True,
            (0, 0, 0),
        )
        print(self._stats_text)

        # image
        self._image_size = (600, 600)
        self._image = None

        # user input box
        self._passive_color = (50, 50, 50)
        self._active_color = (255, 182, 193)
        self._input_rect = pygame.Rect((325, 520), (300, 50))
        self._input_active = False

    def draw_guess(self):
        """when the user can see image and map and can input a guess"""
        self._screen.fill(self._black)
        self.draw_image()
        self.draw_map()
        self.draw_submit_button()
        self.draw_input_rect()
        text = (
            "write ur guess in box. pink is selected. grery is not selected"
            " .click button to see score"
        )
        rendered = self._big_font.render(text, True, (255, 255, 255))
        self._screen.blit(rendered, (40, 40))

    def draw_score(self):
        self._screen.fill(self._black)
        self.draw_image()
        self.draw_map()
        self.draw_guess_marker()
        self.draw_correct_marker()
        self.draw_line()
        self.draw_scoreboard()
        self.draw_next_round_button()
        text = f"score: {self._model.average_score} click to play next round"
        rendered = self._big_font.render(text, True, (255, 255, 255))
        self._screen.blit(rendered, (40, 40))

    def draw_error(self):
        self._screen.fill(self._black)
        self.draw_error_button()
        rendered = self._big_font.render(
            "click to say i read the error message", True, (255, 255, 255)
        )
        self._screen.blit(rendered, (40, 40))

    def draw_error_button(self):
        pygame.draw.rect(self._screen, (255, 0, 0), self._error_button)

    def draw_input_rect(self):
        if self._input_active:
            color = self._active_color
        else:
            color = self._passive_color
        text_surface = self._medium_font.render(
            self._model.user_text, True, (255, 255, 255)
        )
        self._input_rect.w = max(100, text_surface.get_width() + 5)
        pygame.draw.rect(self._screen, color, self._input_rect, 6)
        self._screen.blit(
            text_surface, (self._input_rect.x + 2, self._input_rect.y + 2)
        )

    def toggle_input_rect(self):
        self._input_active = not self._input_active

    def draw_submit_button(self):
        pygame.draw.rect(self._screen, self._blue, self._submit_button)

    def draw_next_round_button(self):
        pygame.draw.rect(self._screen, self._green, self._next_round_button)

    def draw_image(self):
        self._image = pygame.image.load(self._model.image_path)
        self._screen.blit(
            pygame.transform.scale(self._image, self._image_size), (50, 50)
        )

    def draw_map(self):
        self._screen.blit(
            pygame.transform.scale(self._map, self._map_size), (700, 140)
        )

    def draw_guess_marker(self):
        pygame.draw.circle(
            self._map,
            self._red,
            (self._model.guess_lon_pixels, self._model.guess_lat_pixels),
            2,
            0,
        )
        print(
            f"Guess pixels:{self._model.guess_lon_pixels},"
            f" {self._model.guess_lat_pixels}"
        )

    def draw_correct_marker(self):
        pygame.draw.circle(
            self._screen,
            self._red,
            (self._model.correct_lon_pixels, self._model.correct_lat_pixels),
            2,
            0,
        )
        print(
            f"Correct pixels:{self._model.correct_lon_pixels},"
            f" {self._model.correct_lat_pixels}"
        )

    def draw_line(self):
        pygame.draw.line(
            self._screen,
            self._black,
            (self._model.guess_lon_pixels, self._model.guess_lat_pixels),
            (self._model.correct_lon_pixels, self._model.correct_lat_pixels),
            1,
        )

    def get_stats_text(self):
        self._distance_text = f"Distance: {self._model.distance} meters"
        self._score_text = f"Score: {self._model.current_score} points"
        self._average_score_text = (
            f"Average Score: {self._model.average_score} points"
        )
        self._stats_text = self._small_font.render(
            self._distance_text + self._score_text + self._average_score_text,
            True,
            (0, 0, 0),
        )
        print(self._stats_text)

    def draw_scoreboard(self):
        self.get_stats_text()
        self._scoreboard.fill(self._cream)
        self._screen.blit(self._scoreboard, (650, 50))

        title_rect = self._scoreboard_title.get_rect()
        title_rect.topleft = (10, 10)
        self._scoreboard.blit(self._scoreboard_title, title_rect)

        stats_rect = self._stats_text.get_rect()
        stats_rect.topleft = (50, 10)
        self._scoreboard.blit(self._stats_text, stats_rect)

    @property
    def submit_button(self):
        return self._submit_button

    @property
    def next_round_button(self):
        return self._next_round_button

    @property
    def error_button(self):
        return self._error_button

    @property
    def input_active(self):
        return self._input_active

    @property
    def input_rect(self):
        return self._input_rect
