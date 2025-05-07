"""main file of our game"""

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
    events = pygame.event.get()
    controller.button_events(events)
    print(f"Current mode: {model.mode}")

    if model.mode == "guess":
        view.draw_guess()
        controller.get_user_input(events)
    elif model.mode == "score":
        view.draw_score()
    elif model.mode == "error":
        view.draw_error()

    pygame.display.update()
