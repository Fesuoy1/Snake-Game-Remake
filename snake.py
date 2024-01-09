import pygame as pg
from base_object import BaseObject

class Snake(BaseObject):
    def __init__(self, main) -> None:
        super().__init__(main)
        self._snake = pg.rect.Rect((0, 0, self.TILE_SIZE, self.TILE_SIZE))
        self._snake.center = self.get_random_pos()
        self.segments = [self._snake.copy()]

    def move(self, snake_dir) -> None:
        self._snake.move_ip(snake_dir)
        self.segments.append(self._snake.copy())
        self.segments = self.segments[-self.main.length:]

    def draw_snake(self) -> None:
        # Draw snake head
        pg.draw.rect(self.main.screen, self.main.DARK_GREEN, self._snake)
        # Draw snake segments
        for segment in self.segments[0:-1]:
            pg.draw.rect(self.main.screen, self.main.GREEN, segment)

    @staticmethod
    def copy_snake(snake: pg.rect.Rect) -> pg.rect.Rect:
        return snake.copy()
    