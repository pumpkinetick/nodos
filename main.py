import arcade

from nodos.render import SimulationWindow

from nodos.logging_config import setup_logging
from nodos.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WINDOW_TITLE
)


def main():
    setup_logging()
    _ = SimulationWindow(
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        title=WINDOW_TITLE
    )
    arcade.run()

if __name__ == '__main__':
    main()
