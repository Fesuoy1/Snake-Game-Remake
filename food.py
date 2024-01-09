from base_object import BaseObject
import pygame as pg

class Food(BaseObject):
    def __init__(self, main) -> None:
        super().__init__(main)
        self.foods = self.initialize_food(5)

    def initialize_food(self, spawnAmount: int, level: int = 1):
        valid_positions = self.get_valid_positions()
        foods = [self.main.snake.copy_snake(self.main.snake._snake) for _ in range(spawnAmount * level)]
        for food in foods:
            food.center = self.RNG.choice(valid_positions)
        return foods
    
    def get_valid_positions(self):
        if hasattr(self, "_valid_positions"):
            return self._valid_positions
        valid_positions = [(x, y) for x in range(self.RANGE[0], self.RANGE[1], self.TILE_SIZE) for y in range(self.RANGE[2], self.RANGE[3], self.TILE_SIZE)]
        self._valid_positions = valid_positions
        return valid_positions

    def check_food_position(self) -> None:
        for food in self.foods:
            if food.left < self.RANGE[0] or food.right > self.RANGE[1] or food.top < self.RANGE[2] or food.bottom > self.RANGE[3]:
                food.center = self.get_random_pos()

    def draw_food(self, foods) -> None:
        for food in foods:
            pg.draw.rect(self.main.screen, self.main.RED, food)

            # Draw the food in blue if there is only one left
            if len(foods) == 1:
                pg.draw.rect(self.main.screen, self.main.BLUE, food)