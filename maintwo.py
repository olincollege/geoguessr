import os
import sys
from controller import GameController
from view import GameUI


def main():
    try:
        # Initialize controller (no arguments needed)
        controller = GameController()
        # Start first round
        controller.start_round()
        # Initialize UI
        ui = GameUI(controller)
        # Run game
        ui.run()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure dataset directory exists with:")
        print("- dataset/coord.csv")
        print("- dataset/images/*.jpg")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
