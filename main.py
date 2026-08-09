import arcade

from nodos.render import SimulationWindow

from nodos.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WINDOW_TITLE
)


def main():
    _ = SimulationWindow(
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        title=WINDOW_TITLE
    )
    arcade.run()

if __name__ == '__main__':
    main()
