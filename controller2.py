from model import Setup, Stats
import random
import webbrowser
import os
import traceback


class InteractiveWidgets:
    """
    Connects inputs from interactive widgets (textbox, buttons, markers) to the model.

    Attributes:
        coord_input_text (str): the player's input in the pygame textbox.
        Setup: all methods and attributes from class Setup.
        Stats: all methods and attributes from class Stats.

    """

    def __init__(
        self,
        guess_confirmed,
        coord_input_text,
    ):
        self.coord_input_text = coord_input_text
        self.Setup = Setup()
        self.Stats = Stats()
        # Replace with actual specific class in view
        self.View = View()

    def on_confirm(self):
        """
        On-click function for "confirm guess" button.

        Raises:
            ValueError: If input is missing, two numbers aren't given, or
            coordinates are out of range.
            Exception: Unexpected errors during processing.
        """
        # Should change to be if TRUE since guess_confirmed should change
        if not self.guess_confirmed:
            # try:
            # Define the input_text
            input_text = self.coord_input_text.strip()
            print(f"[DEBUG] Raw input: '{input_text}'")

            # Check that input_text was entered
            if not input_text:
                raise ValueError("No coordinates entered.")

            # Parse input_text for guess coordinates
            parts = [p.strip() for p in input_text.replace(" ", "").split(",")]
            if len(parts) < 2:
                parts = input_text.split()
            # Print out parsed guess coordinates
            print(f"[DEBUG] Parsed parts: {parts}")

            # Check that parsed coordinates have two parts (lat & lon)
            if len(parts) != 2:
                raise ValueError(
                    "Please enter exactly two numbers (lat and lon)."
                )

            # Convert lat and lon to float types
            lat = float(parts[0])
            lon = float(parts[1])

            # Validate coordinate ranges
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinate ranges")

            # Save guess coordinates to class Setup
            input_coords = [lat, lon]
            # Scoreboard stats calculations
            self.Setup.handle_guess(input_coords)

            coord_text = f"Guess: ({lat:.4f}, {lon:.4f})"
            score_text = f"{score} points"
            average_score_text = f"{average_score} points"
            distance_text = f"{distance / 1000:.1f} km"
            guess_confirmed = True

            # Clear input text
            self.coord_input_text = ""

            # return (
            #     coord_text,
            #     score_text,
            #     average_score_text,
            #     distance_text,
            #     guess_confirmed,
            # )

            view.update_display(
                coord_text,
                score_text,
                average_score_text,
                distance_text,
                guess_confirmed,
            )

            # except ValueError as ve:
            #     self.coord_text = f"Error: {str(ve)}"
            #     print(f"❌ Validation error: {ve}")
            # except Exception as e:
            #     self.coord_text = "Error processing guess"
            #     print(f"❌ Unexpected error: {e}\n{traceback.format_exc()}")

    def on_next_round(self):
        """
        On-click function for "next round" button.
        """
        self.Setup.start_round()
        self.score_text = ""
        self.average_score_text = ""
        self.distance_text = ""
        self.guess_confirmed = False

        view.update_display(
            coord_text,
            score_text,
            average_score_text,
            distance_text,
            guess_confirmed,
        )
