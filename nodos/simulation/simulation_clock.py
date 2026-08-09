import logging

logger = logging.getLogger(__name__)


class SimulationClock:
    def __init__(self,
                 tick_length: float = 1.0,
                 start_tick: int = 0,
                 start_time: float = 0.0
                 ):
        self.tick_length = tick_length
        self.current_tick: int = start_tick
        self.time: float = start_time

    def tick(self):
        self.current_tick += 1
        self.time += float(self.tick_length)
        logger.debug(
            'Clock advanced to tick %d (time=%s)', self.current_tick, self.time
        )

    def reset(self,
              tick: int = 0,
              time: float = 0.0
              ):
        self.current_tick = tick
        self.time = time
