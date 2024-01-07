import os
from random import Random
from typing import Dict, List, Tuple
from os import path
from datetime import datetime
try:
    import pygame as pg
except ModuleNotFoundError:
    input("Please install pygame. Run 'pip install pygame' in the terminal. Press enter to continue.\n")

print("Note: You may experience some unknown bugs while playing the game. If you encounter any, please report it to the developer. Thanks!")

class BaseObject:
    def __init__(self, main) -> None:
        self.main = main
        self.RNG: Random = self.main.RNG
        self.RANGE: Tuple[int, int, int, int] = self.main.RANGE
        self.TILE_SIZE: int = self.main.TILE_SIZE

    def get_random_pos(self) -> Tuple[int, int]:
        x = self.RNG.randrange(self.RANGE[0], self.RANGE[1], self.TILE_SIZE)
        y = self.RNG.randrange(self.RANGE[2], self.RANGE[3], self.TILE_SIZE)
        return x, y

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
    

class Food(BaseObject):
    def __init__(self, main) -> None:
        super().__init__(main)
        self.foods = self.initialize_food(self.RNG.randint(4, 15))

    def initialize_food(self, spawnAmount: int, level: int = 1) -> List[pg.rect.Rect]:
        valid_positions = self.get_valid_positions()
        foods = [self.main.snake.copy_snake(self.main.snake._snake) for _ in range(spawnAmount * level)]
        for food in foods:
            food.center = self.RNG.choice(valid_positions)
        return foods
    
    def get_valid_positions(self) -> List[Tuple[int, int]]:
        if hasattr(self, "_valid_positions"):
            return self._valid_positions
        valid_positions = [(x, y) for x in range(self.RANGE[0], self.RANGE[1], self.TILE_SIZE) for y in range(self.RANGE[2], self.RANGE[3], self.TILE_SIZE)]
        self._valid_positions = valid_positions
        return valid_positions

    def check_food_position(self) -> None:
        for food in self.foods:
            if food.left < self.RANGE[0] or food.right > self.RANGE[1] or food.top < self.RANGE[2] or food.bottom > self.RANGE[3]:
                food.center = self.get_random_pos()

    def draw_food(self, foods: List[pg.rect.Rect]) -> None:
        for food in foods:
            pg.draw.rect(self.main.screen, self.main.RED, food)
        

class SnakeGame:
    def __init__(self) -> None:
        pg.init()
        self.width, self.height = 800, 650
        self.TILE_SIZE: int = 20
        self.RANGE: Tuple[int, int, int, int] = (0, self.width - self.TILE_SIZE, 0, self.height - self.TILE_SIZE)
        self.RNG: Random = Random(datetime.now().microsecond)
        self.GREEN: Tuple[int, int, int] = (0, 205, 0)
        self.DARK_GREEN: Tuple[int, int, int] = (0, 130, 0)
        self.GRAY = (10, 10, 10)
        self.RED = (255, 0, 0)
        
        self.score_font: pg.font.Font = pg.font.SysFont(None, 30)
        self.game_over_font = pg.font.SysFont(None, 40)

        # Variables to control collision behavior
        self.no_collision_walls: bool = False
        self.no_collision_food: bool = False


        self.fix_collision_itself: bool = True


        # Sound Effects
        self.eat_sound: pg.mixer.Sound = pg.mixer.Sound(path.join('assets', 'eat.wav'))
        self.food_spawn_sound: pg.mixer.Sound = pg.mixer.Sound(path.join('assets', 'food_spawn.wav'))

        self.length: int = 1
        self.length_inc: int = 1
        self.level: int = 1

        self.snake_dir: Tuple[int, int] = (0, 0)
        self.score: int = 0
        self.best_score: int = self.get_best_score()
        self.score_inc: int = 1

        self.cheat_mode: bool = False

        # Set up the screen and clock
        self.screen: pg.Surface = pg.display.set_mode((self.width, self.height), pg.SCALED | pg.DOUBLEBUF | pg.HWSURFACE | pg.HWACCEL)

        pg.display.set_caption('Snake Game')
        self.clock: pg.time.Clock = pg.time.Clock()
        self.time: int = 0
        self.time_step: int = 40
        
        self.snake = Snake(self)
        self.foods = Food(self)
        
        # Make the cursor invisible
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

        self.last_move_time = 0
        self.move_delay = 60  # milliseconds

        # Dictionary to map keyboard keys to snake directions
        self.keys: Dict[int, Tuple[int, int]] = {pg.K_w: (0, -self.TILE_SIZE),
                                                 pg.K_s: (0, self.TILE_SIZE),
                                                 pg.K_a: (-self.TILE_SIZE, 0),
                                                 pg.K_d: (self.TILE_SIZE, 0),
                                                 pg.K_q: (-self.TILE_SIZE, -self.TILE_SIZE),
                                                 pg.K_e: (self.TILE_SIZE, -self.TILE_SIZE),
                                                 pg.K_UP: (0, -self.TILE_SIZE),
                                                 pg.K_DOWN: (0, self.TILE_SIZE),
                                                 pg.K_LEFT: (-self.TILE_SIZE, 0),
                                                 pg.K_RIGHT: (self.TILE_SIZE, 0)}
        
        # Check if the config file exists, if not, create it with default values
        if path.exists('config.txt') is False:
            with open('config.txt', 'w') as f:
                f.write(f"Snake Speed: {self.time_step}\nSnake Length Increment: {self.length_inc}\n"
                        f"Score Increment: {self.score_inc}\nSnakes Starting Length: {self.length}\n\nDisable Collision With Wall: No\n"
                        "Fix Collision With Self: Yes\nDisable Collision With Food: No\n\nWarning: "
                        "Cheat Mode will be enabled if any of the values are changed.")

        # Read the config file and update the variables accordingly
        try:
            print("Reading config file...")
            with open('config.txt') as f:
                config: List[str] = f.read().lower().split()
                self.time_step: int = int(config[2])
                self.length_inc: int = int(config[6])
                self.score_inc: int = int(config[9])
                self.length: int = int(config[13])
                self.no_collision_walls: bool = config[18] == 'yes'
                self.fix_collision_itself: bool = config[23] == 'yes'
                self.no_collision_food: bool = config[28] == 'yes'


                if (self.time_step == 40 and self.length_inc == 1 and self.length == 1 and self.no_collision_walls is False
                        and self.no_collision_food is False and self.score_inc == 1):
                    print("Note: Cheat Mode will be enabled if any of the values in config.txt are changed.")

                if (self.time_step != 40 or self.length_inc != 1 or self.length != 1 or self.no_collision_walls
                        or self.no_collision_food or self.score_inc != 1):
                    self.cheat_mode: bool = True
                    print("Cheat Mode enabled. Best Scores will not be saved.")
                    print("To disable cheat mode, change the values in config.txt back to default or delete the config.txt file.")
        except Exception as e:
            input(f"Error with config file: {e}\nPress enter to continue.\n")
        print(f"Snake Speed: {self.time_step}\nSnake Length Increment: {self.length_inc}\n"
                       f"Score Increment: {self.score_inc}\nSnakes Starting Length: {self.length}\n"
                       f"Disable Collision With Wall: {self.no_collision_walls}\n"
                       f"Disable Collision With Self: {self.fix_collision_itself}\n"
                       f"Disable Collision With Food: {self.no_collision_food}")

    def run(self):
        while True:
            self.snake_dir = self.handle_events(self.snake_dir)
            self.draw_objects(self.foods.foods)
            self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score = self.handle_collision(self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score)

            if self.no_collision_food is False:
                self.snake._snake, self.foods.foods, self.length, self.score, self.best_score = self.handle_food_collision(self.snake._snake, self.foods.foods, self.length, self.score, self.best_score)
                self.foods.check_food_position()
                self.foods.foods = self.handle_food_in_snake_collision(self.foods.foods, self.snake.segments)

            # if foods list is empty, spawn more
            if len(self.foods.foods) == 0:
                self.foods.foods = self.foods.initialize_food(self.RNG.randint(4, 15), self.level)
                self.level += 1
                self.food_spawn_sound.play()

            time_now = pg.time.get_ticks()
            if time_now - self.time >= self.time_step:
                self.time = time_now
                self.snake.move(self.snake_dir)
            self.display_scores(self.score, self.best_score, self.foods.foods)
            pg.display.flip()
            self.clock.tick(60)

            # Check if the snake collides with itself or the walls
            if (self.no_collision_walls is False and (self.snake._snake.left < 0 or self.snake._snake.right > self.width or self.snake._snake.top < 0 or self.snake._snake.bottom > self.height)) or self.snake._snake.collidelist(self.snake.segments[:-1]) != -1:
                self.game_over_screen()
                self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score = self.handle_collision(self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score, True)


    def game_over_screen(self):
        game_over_text = self.game_over_font.render("Game Over! Press R to Restart or ESC to Quit", True, 'cyan')
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(game_over_text, game_over_rect)
        pg.display.flip()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.save_best_score(self.best_score)
                    exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        return
                    if event.key == pg.K_ESCAPE:
                        self.save_best_score(self.best_score)
                        exit()
                    


    def handle_collision(self, snake: pg.rect.Rect, foods: List[pg.rect.Rect], length: int, snake_dir: Tuple[int, int], score: int, force_restart: bool = False) -> Tuple[pg.rect.Rect, List[pg.rect.Rect], int, Tuple[int, int], int]:
        snake_in_wall: bool = (snake.left < 0 or snake.right > self.width or snake.top < 0 or snake.bottom > self.height) and self.no_collision_walls is False
        snake_positions = set(segment.center for segment in self.snake.segments[:-1])
        if (snake_in_wall or snake.center in snake_positions) or force_restart or self.fix_collision_itself is False:
            snake.center, foods = self.snake.get_random_pos(), self.foods.initialize_food(self.RNG.randint(4, 15), self.level)
            length, snake_dir = 1, (0, 0)
            score = 0
            self.level = 1
            self.snake.segments = [snake.copy()]
            for food in foods:
                if len(foods) > 15:
                    foods = foods[:15]
                food.center = self.foods.get_random_pos()
        return snake, foods, length, snake_dir, score


    def handle_food_collision(self, snake: pg.rect.Rect, foods: List[pg.rect.Rect], length: int, score: int, best_score: int) -> Tuple[pg.rect.Rect, List[pg.rect.Rect], int, int]:
        if self.no_collision_food is False:
            for food in foods:
                if snake.collidepoint(food.center):
                    foods.remove(food)
                    length += self.length_inc
                    score += self.score_inc
                    self.eat_sound.play()
                    if score >= best_score:
                        best_score = score
            return snake, foods, length, score, best_score

    def handle_food_in_snake_collision(self, foods: List[pg.rect.Rect], segments: List[pg.rect.Rect]) -> List[pg.rect.Rect]:
        new_foods = []
        for food in foods:
            food_in_snake: bool = food.collidelist(segments[:-1]) != -1
            if food_in_snake is False:
                new_foods.append(food)
        return new_foods


    def display_scores(self, score: int, best_score: int, foods: List[pg.rect.Rect]) -> None:
        score_text = self.score_font.render(f"Score: {score}", True, 'white')
        self.screen.blit(score_text, (10, 10))
        best_score_text = self.score_font.render(f"Best Score: {best_score}", True, 'white')
        self.screen.blit(best_score_text, (10, score_text.get_height() + 15))
        level_text = self.score_font.render(f"Level: {self.level}", True, 'white')
        if self.cheat_mode:
            cheat_text = self.score_font.render("Cheat Mode on, You can't save best scores.", True, 'white')
            self.screen.blit(cheat_text, (10, best_score_text.get_height() + 94))
            self.screen.blit(level_text, (10, cheat_text.get_height() + 40))
        self.screen.blit(level_text, (10, best_score_text.get_height() + 40))
        remaining_foods_text = self.score_font.render(f"Remaining Foods: {len(foods)}", True, 'white')
        self.screen.blit(remaining_foods_text, (10, level_text.get_height() + 65))

    def ask_save_best_score(self, best_score: int) -> bool:
        pg.quit()

        best_score_value = self.get_best_score()
        if best_score > best_score_value and self.cheat_mode:
            input("Best scores will not be saved in cheat mode. Press enter to continue.\n")
            return False
        if best_score > best_score_value:
            save = input(f"\nNew Best score: {best_score} - Save to a file? (y/n): ").lower()
            return save == 'y'

    def save_best_score(self, best_score: int) -> None:
        if self.ask_save_best_score(best_score):
            with open('best_score.txt', 'w') as f:
                f.write(f"Best scores will carry over to next session!\n"
                        f"But if you delete this file you will lose your best score and will be 0 next time.\n\nYour best score is: {best_score}")

    def get_best_score(self) -> int:
        if os.path.exists('best_score.txt'):
            with open('best_score.txt') as f:
                return int(f.read().rsplit(maxsplit=1)[1])
        else:
            return 0

    def handle_events(self, snake_dir: Tuple[int, int]) -> Tuple[int, Tuple[int, int]]:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.save_best_score(self.best_score)
                exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.save_best_score(self.best_score)
                    exit()

                if event.key == pg.K_r:
                    snake_dir = (0, 0)
                    for food in self.foods.foods:
                        food.center = self.snake.get_random_pos()
                    self.handle_collision(self.snake._snake, self.foods.foods, self.length, snake_dir, self.score, True)

                if event.key in self.keys:
                    current_time = pg.time.get_ticks()
                    if current_time - self.last_move_time >= self.move_delay:
                        if snake_dir == (-self.keys[event.key][0], -self.keys[event.key][1]) and self.length > 1:
                            continue
                        snake_dir = self.keys[event.key]
                        self.last_move_time = current_time

        return snake_dir

    def draw_objects(self, foods: List[pg.rect.Rect]) -> None:
        try:
            self.screen.fill(self.GRAY)
            self.foods.draw_food(foods)
            self.snake.draw_snake()
        except Exception as e:
            print(f"Error occurred during drawing: {e}")


if __name__ == '__main__':
    SnakeGame().run()
