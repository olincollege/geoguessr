"""View of Model, View, Class Architecture"""

import pygame


class View:
    def __init__(self, model):
        self._model = model

        # screen
        self._width = 1760
        self._height = 700
        self._screen = pygame.display.set_mode((self._width, self._height))

        # fonts
        self._big_font = pygame.font.Font(None, 50)
        self._medium_font = pygame.font.Font(None, 35)
        self._small_font = pygame.font.Font(None, 20)

        # colors
        self._black = (0, 0, 0)
        self._blue = (0, 0, 100)
        self._green = (0, 100, 0)
        self._red = (100, 0, 0)

        # buttons
        self._submit_button = pygame.Rect((75, 500), (450, 100))
        self._next_round_button = pygame.Rect((75, 500), (450, 100))
        self._error_button = pygame.Rect((75, 500), (450, 100))

        # map
        self._map_path = "map.jpeg"
        self._map_size = (1021, 510)
        self._map = pygame.image.load(self._map_path)

        # round image
        self._image_size = (600, 600)
        self._image = None

        # user input variables
        self._passive_color = (50, 50, 50)
        self._active_color = (255, 182, 193)
        self._input_rect = pygame.Rect((400, 400), (60, 30))
        self._input_active = False

    def draw_guess(self):
        """when the user can see image and map
        and can input a guess"""
        self._screen.fill(self._black)
        self._model.next_guess()
        self._image = pygame.image.load(self._model.image_path)
        self._screen.blit(
            pygame.transform.scale(self._image, self._image_size), (50, 50)
        )
        self._screen.blit(
            pygame.transform.scale(self._map, self._map_size), (600, 50)
        )
        self.draw_submit_button()
        self.draw_input_rect()
        text = (
            "write ur guess in box. pink is selected. grery is not selected"
            " .click button to see score"
        )
        rendered = self._big_font.render(text, True, (255, 255, 255))
        self._screen.blit(rendered, (40, 40))

    def draw_score(self):
        """when the user can see their score
        and can press next round"""
        self._screen.fill(self._black)
        self._image = pygame.image.load(self._model.image_path)
        self._screen.blit(
            pygame.transform.scale(self._image, self._image_size), (50, 50)
        )
        self._screen.blit(
            pygame.transform.scale(self._map, self._map_size), (600, 50)
        )
        self._map.blit(self.draw_guess_marker())
        self._map.blit(self.draw_correct_marker(), (600, 50))
        self._map.blit(self.draw_line(), (600, 50))
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
        pygame.draw.rect(self._screen, (255, 0, 0), self._submit_button)

    def draw_input_rect(self):
        """draws input_rect"""
        if self._input_active:
            color = self._active_color
        else:
            color = self._passive_color
        text_surface = self._small_font.render(
            self._model.user_text, True, (255, 255, 255)
        )
        self._input_rect.w = max(100, text_surface.get_width() + 10)
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

    # def scale_map(self):
    #     pygame.transform.scale(self._map, self._map_size)

    def draw_guess_marker(self):
        pygame.draw.circle(
            self._map,
            self._red,
            (self._model.guess_lon_pixels, self._model.guess_lat_pixels),
            2,
            0,
        )

    def draw_correct_marker(self):
        pygame.draw.circle(
            self._screen,
            self._red,
            (self._model.correct_lon_pixels, self._model.correct_lat_pixels),
            2,
            0,
        )

    def draw_line(self):
        pygame.draw.line(
            self._screen,
            self._black,
            (self._model.guess_lon_pixels, self._model.guess_lat_pixels),
            (self._model.correct_lon_pixels, self._model.correct_lat_pixels),
        )

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
