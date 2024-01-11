from pygame.math import Vector2

class BaseObject:
    def __init__(self, main) -> None:
        self.main = main
        self.RNG = self.main.RNG
        self.RANGE = self.main.RANGE
        self.TILE_SIZE: int = self.main.TILE_SIZE
        self.position = Vector2(0, 0)

    def get_random_pos(self) -> Vector2:
        x = self.RNG.randrange(self.RANGE[0] + self.TILE_SIZE, self.RANGE[1] - self.TILE_SIZE, self.TILE_SIZE)
        y = self.RNG.randrange(self.RANGE[2] + self.TILE_SIZE, self.RANGE[3] - self.TILE_SIZE, self.TILE_SIZE)
        return Vector2(x, y)

    def get_valid_positions(self):
        if hasattr(self, "_valid_positions"):
            return self._valid_positions
        # Adjust the range to account for the size of the object
        valid_positions = [(x, y) for x in range(self.RANGE[0], self.RANGE[1] - self.TILE_SIZE, self.TILE_SIZE)
                                  for y in range(self.RANGE[2], self.RANGE[3] - self.TILE_SIZE, self.TILE_SIZE)]
        self._valid_positions = valid_positions
        return valid_positions
