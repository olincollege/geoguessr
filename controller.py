"""Controller class of Model, View Controller architecture"""

import sys
import pygame


class Controller:
    def __init__(self, view, model):
        """initialize view"""
        self._view = view
        self._model = model
        self._guess_lat = 0
        self._guess_lon = 0

    def button_events(self, events):
        """tracks for the two buttons"""
        for event in events:
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

    def get_user_input(self, events):
        """determines if the box is pressed and if the user is putting in text."""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    self._view.input_rect.collidepoint(event.pos)
                    and self._model.mode == "guess"
                ):
                    self._view.toggle_input_rect()
                    self._model.set_input_error(False)  # ← Clear error on focus

                elif (
                    self._view.submit_button.collidepoint(event.pos)
                    and self._model.mode == "guess"
                ):
                    user_input = self._model.user_text.strip().split()
                    if len(user_input) != 2:
                        print("Invalid input: not two values")
                        self._model.set_input_error(True)  # ← Set error
                    else:
                        try:
                            self._guess_lat = float(user_input[0])
                            self._guess_lon = float(user_input[1])
                            self._model.set_guess_coordinates(
                                self._guess_lat, self._guess_lon
                            )
                            self._model.set_input_error(False)  # ← Clear error
                            self._model.get_score()
                        except ValueError:
                            print("Invalid input: not numbers")
                            self._model.set_input_error(True)  # ← Set error
                else:
                    self._view.toggle_input_rect()
                    self._model.set_input_error(False)  # ← Clear error

            if self._view.input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self._model.delete_user_text()
                else:
                    self._model.add_user_text(event.unicode)
                self._model.set_input_error(False)  # ← Clear error on typing
