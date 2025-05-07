"""main file of our game"""

import sys
import pygame

from model import GeoGuessr
from view import View
from controller import Controller

# Initialize everything
pygame.init()
model = GeoGuessr()
view = View(model)
controller = Controller(view, model)

while True:
    # run game
    if model.mode == "guess":
        view.draw_guess()
        controller.get_user_input()
    elif model.mode == "score":
        view.draw_score()
    else:
        view.draw_error()

    controller.button_events()

    pygame.display.update()
