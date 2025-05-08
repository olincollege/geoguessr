"""Controller class of Model, View Controller architecture"""

import sys
import pygame


class Controller:
    """
    Updates Geoguessr model state and View based on inputs from
    buttons and textbox. Determines whether or not inputs are valid.

    Attributes:
        view (View): all View instances.
        model (Geoguessr): all Geoguessr instances.
        guess_lat (float): the user's guess latitude.
        guess_lon (float): the user's guess longitude.
    """

    def __init__(self, view, model):
        """
        Initialize necessary instance imports and user inputs
        to track.

        Args:
            view (View): all View instances.
            model (Geoguessr): all Geoguessr instances.
        """
        self._view = view
        self._model = model
        self._guess_lat = 0
        self._guess_lon = 0

    def button_events(self, events):
        """
        Handles user interaction with buttons based on pygame
        events. This tracks whether or not the user wants to confirm
        their guess, move on to the next round, or if the two former
        options are not possible (due to an invalid input).

        Args:
            events (list): pygame events to process.
        """
        # Loop through all events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Checks if mouse was pressed on the button
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Reset model state for the next round after scores
                # for previous round given
                if (
                    self._view.next_round_button.collidepoint(event.pos)
                    and self._model.mode == "score"
                ):
                    self._model.next_guess()
                # Reset model mode to "guess" after error has been
                # processed for invalid inputs
                if (
                    self._view.error_button.collidepoint(event.pos)
                    and self._model.mode == "error"
                ):
                    self._model.no_error()

    def get_user_input(self, events):
        """
        Determines if the text box is pressed and if the user is
        putting in text. Checks that user's inputs are valid, then
        calls model to calculate scores.

        Args:
            events (list): pygame events to process.
        """
        # Loop through all events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check if mouse was pressed on text box
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Update textbox color if clicked
                if (
                    self._view.input_rect.collidepoint(event.pos)
                    and self._model.mode == "guess"
                ):
                    self._view.toggle_input_rect()
                    self._model.set_input_error(False)
                # Input given to text box
                elif (
                    self._view.submit_button.collidepoint(event.pos)
                    and self._model.mode == "guess"
                ):
                    user_input = self._model.user_text.strip().split()
                    # Check that latitude/longitude are both given
                    if len(user_input) != 2:
                        print("Invalid input: not two values")
                        self._model.set_input_error(True)
                    else:
                        # Get scores for processed latitude/longitude
                        try:
                            self._guess_lat = float(user_input[0])
                            self._guess_lon = float(user_input[1])
                            self._model.set_guess_coordinates(
                                self._guess_lat, self._guess_lon
                            )
                            self._model.set_input_error(False)
                            self._model.get_score()
                        # Check that latitude/longitude inputs are actual numbers
                        except ValueError:
                            print("Invalid input: not numbers")
                            self._model.set_input_error(True)
                # Nothing changes if the text box is not clicked
                else:
                    self._view.toggle_input_rect()
                    self._model.set_input_error(False)

            # Adds and deletes text when user uses backspace or types on keyboard
            if self._view.input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self._model.delete_user_text()
                else:
                    self._model.add_user_text(event.unicode)
                self._model.set_input_error(False)
