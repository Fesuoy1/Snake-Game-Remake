from pygame.math import Vector2

class BaseObject:
    def __init__(self, main) -> None:
        self.main = main
        self.RNG = self.main.RNG
        self.RANGE = self.main.RANGE
        self.TILE_SIZE: int = self.main.TILE_SIZE
        self.position = Vector2(0, 0)

    def get_random_pos(self) -> Vector2:
        x = self.RNG.randrange(self.RANGE[0], self.RANGE[1], self.TILE_SIZE)
        y = self.RNG.randrange(self.RANGE[2], self.RANGE[3], self.TILE_SIZE)
        return Vector2(x, y)
