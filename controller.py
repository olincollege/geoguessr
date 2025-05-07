"""Controller class of Model, View Controller architecture"""

import sys
import pygame


class Controller:
    def __init__(self, view, model):
        """initialize view"""

        self._view = view
        self._model = model

    def button_events(self):
        """tracks for the two buttons"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if (
                    self._view.next_round_button.collidepoint(event.pos)
                    and self._model.mode == "score"
                ):
                    self._model.next_guess()
                if (
                    self._view.error_button.collidepoint(event.pos)
                    and self._model.mode == "error"
                ):
                    self._model.no_error()

    def get_user_input(self):
        """determines if the box is pressed and if
        the user is putting in text."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    self._view.input_rect.collidepoint(event.pos)
                    and self._model.mode == "score"
                ):
                    self._view.toggle_input_rect()
                elif (
                    self._view.submit_button.collidepoint(event.pos)
                    and self._model.mode == "guess"
                ):
                    try:
                        self._model.get_score()
                    except (ValueError, IndexError):
                        self._model.error()
                else:
                    self._view.toggle_input_rect()

            if self._view.input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self._model.delete_user_text()
                else:
                    self._model.add_user_text(event.unicode)
