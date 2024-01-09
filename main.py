from random import Random
from typing import Dict, List, Tuple
from os import path
from datetime import datetime
from snake import Snake
from food import Food
from particle import ParticleSystem

try:
    import pygame as pg
    from pygame.math import Vector2
    from pygame.font import SysFont
except ModuleNotFoundError:
    input("Please install pygame. Run 'pip install pygame' in the terminal. Press enter to continue.\n")

print("Note: You may experience some unknown bugs while playing the game. If you encounter any, please report it to the developer. Thanks!")


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
        self.BLUE = (0, 0, 255)
        
        self.score_font: SysFont = SysFont(None, 30)
        self.game_over_font: SysFont = SysFont(None, 40)
        self.paused_font: SysFont = SysFont(None, 60)

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

        self.snake_dir: Vector2 = Vector2(0, 0)
        self.score: int = 0
        self.best_score: int = self.get_best_score()
        self.score_inc: int = 1

        self.cheat_mode: bool = False

        # Set up the screen and clock
        self.screen: pg.Surface = pg.display.set_mode((self.width, self.height), pg.SCALED | pg.DOUBLEBUF | pg.HWSURFACE | pg.HWACCEL)

        pg.display.set_caption('Snake Game')
        self.clock: pg.time.Clock = pg.time.Clock()
        self.time: int = 0
        self.time_step: int = 100
        
        self.snake = Snake(self)
        self.foods = Food(self)
        self.particles = ParticleSystem(self)

        self.remaining_foods: int = 5
        self.foods_eaten: int = 0
        
        # Make the cursor invisible
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

        self.last_move_time = 0
        self.move_delay = 80  # milliseconds
        
        self.paused = False

        # Dictionary to map keyboard keys to snake directions
        self.keys: Dict[int, Vector2] = {pg.K_w: Vector2(0, -self.TILE_SIZE),
                                                 pg.K_s: Vector2(0, self.TILE_SIZE),
                                                 pg.K_a: Vector2(-self.TILE_SIZE, 0),
                                                 pg.K_d: Vector2(self.TILE_SIZE, 0),
                                                 pg.K_q: Vector2(-self.TILE_SIZE, -self.TILE_SIZE),
                                                 pg.K_e: Vector2(self.TILE_SIZE, -self.TILE_SIZE),
                                                 pg.K_UP: Vector2(0, -self.TILE_SIZE),
                                                 pg.K_DOWN: Vector2(0, self.TILE_SIZE),
                                                 pg.K_LEFT: Vector2(-self.TILE_SIZE, 0),
                                                 pg.K_RIGHT: Vector2(self.TILE_SIZE, 0)}
        
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


                if (self.time_step == 100 and self.length_inc == 1 and self.length == 1 and self.no_collision_walls is False
                        and self.no_collision_food is False and self.score_inc == 1):
                    print("Note: Cheat Mode will be enabled if any of the values in config.txt are changed.")

                if (self.time_step != 100 or self.length_inc != 1 or self.length != 1 or self.no_collision_walls
                        or self.no_collision_food or self.score_inc != 1):
                    self.cheat_mode: bool = True
                    print("Cheat Mode enabled. Best Scores will not be saved.")
                    print("To disable cheat mode, change the values in config.txt back to default or delete the config.txt file.")
        except Exception as e:
            input(f"Error with config file: {e}\nPress enter to continue.\n")
        #print(f"Snake Speed: {self.time_step}\nSnake Length Increment: {self.length_inc}\n"
        #               f"Score Increment: {self.score_inc}\nSnakes Starting Length: {self.length}\n"
        #               f"Disable Collision With Wall: {self.no_collision_walls}\n"
        #               f"Fix Collision With Self: {self.fix_collision_itself}\n"
        #               f"Disable Collision With Food: {self.no_collision_food}")

    def run(self):
        while True:
            self.snake_dir = self.handle_events(self.snake_dir)
            self.draw_objects(self.foods.foods)
            self.display_scores(self.score, self.best_score, self.foods.foods)

            if self.paused is False:
                self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score = self.handle_collision(self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score)

                if self.no_collision_food is False:
                    self.snake._snake, self.foods.foods, self.length, self.score, self.best_score = self.handle_food_collision(self.snake._snake, self.foods.foods, self.length, self.score, self.best_score)
                    self.foods.check_food_position()
                    self.foods.foods = self.handle_food_in_snake_collision(self.foods.foods, self.snake.segments)

                # if foods list is empty, spawn more
                if len(self.foods.foods) == 0:
                    self.foods.foods = self.foods.initialize_food(self.RNG.randint(4, 15), self.level)
                    self.level += 1
                    self.remaining_foods = len(self.foods.foods)
                    self.food_spawn_sound.play()

                time_now = pg.time.get_ticks()
                if time_now - self.time >= self.time_step:
                    self.time = time_now
                    self.snake.move(self.snake_dir)
            
            pg.display.flip()
            self.clock.tick(60)

            # Check if the snake collides with itself or the walls
            if (self.no_collision_walls is False and (self.snake._snake.left < 0 or self.snake._snake.right > self.width or self.snake._snake.top < 0 or self.snake._snake.bottom > self.height)) or self.snake._snake.collidelist(self.snake.segments[:-1]) != -1:
                self.game_over_screen()
                self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score = self.handle_collision(self.snake._snake, self.foods.foods, self.length, self.snake_dir, self.score, True)


    def game_over_screen(self):
        game_over_text = self.game_over_font.render("Game Over! Press R to Restart or ESC to Quit", True, 'cyan')
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        foods_eaten_text = self.game_over_font.render(f"Total Food Eaten: {self.foods_eaten}", True, 'cyan')
        foods_eaten_rect = foods_eaten_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(foods_eaten_text, foods_eaten_rect)
        pg.display.flip()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.save_best_score(self.best_score)
                    exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.foods_eaten = 0
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
                    self.foods_eaten += 1

                    if len(self.foods.foods) < 1:
                        self.particles.emit(food.center, self.BLUE)
                    else:
                        self.particles.emit(food.center, self.RED)

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
        remaining_foods_text = self.score_font.render(f"Remaining Foods: {len(foods)} / {self.remaining_foods}", True, 'white')
        self.screen.blit(remaining_foods_text, (10, level_text.get_height() + 65))

        if self.paused:
            paused_text = self.paused_font.render("Paused", True, 'white')
            self.screen.blit(paused_text, (self.width // 2 - paused_text.get_width() // 2, self.height // 2 - paused_text.get_height() // 2))

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
        if path.exists('best_score.txt'):
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
                    self.remaining_foods = len(self.foods.foods)
                    
                if event.key == pg.K_SPACE:
                    self.paused = not self.paused

                if event.key in self.keys:
                    if self.paused:
                        continue
                    
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
            self.particles.update()
            self.particles.draw(self.screen)
        except pg.error as e:
            print(f"Error occurred during rendering: {e}")


if __name__ == '__main__':
    SnakeGame().run()
