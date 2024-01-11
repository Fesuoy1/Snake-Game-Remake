from base_object import BaseObject
import pygame as pg

class Food(BaseObject):
    def __init__(self, main) -> None:
        super().__init__(main)
        self.foods = self.spawn_food(5)

    def spawn_food(self, spawnAmount: int, level: int = 1):
        valid_positions = self.get_valid_positions()
        snake_positions = {segment.center for segment in self.main.snake.segments}
        foods = []

        for _ in range(spawnAmount * level):
            # Find a position that is not occupied by the snake
            food_position = self.RNG.choice(valid_positions)
            while food_position in snake_positions:
                food_position = self.RNG.choice(valid_positions)
            
            food = self.main.snake.copy_snake(self.main.snake._snake)
            food.center = food_position
            foods.append(food)

        return foods

    def check_food_position(self) -> None:
        for food in self.foods:
            if food.left < self.RANGE[0] or food.right > self.RANGE[1] or food.top < self.RANGE[2] or food.bottom > self.RANGE[3]:
                food.center = self.get_random_pos()

    def draw_food(self, foods) -> None:
        food_surface = pg.Surface((self.RANGE[1], self.RANGE[3]))
        food_color = self.main.BLUE if len(foods) == 1 else self.main.RED
        for food in foods:
            pg.draw.rect(food_surface, food_color, food)
        self.main.screen.blit(food_surface, (0, 0))