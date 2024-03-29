import pygame as pg
from pygame.math import Vector2

class ParticleSystem:
    def __init__(self, game):
        self.game = game

        # Particle settings
        self.particle_count = 20
        self.particle_lifetime = 40
        self.particle_speed = 1

        self.particles = []

    def emit(self, pos, color):
        for _ in range(self.particle_count):
            particle = self.get_particle()
            particle.reset(pos, color)
            self.particles.append(particle)

    
    def get_particle(self):
        for particle in self.particles:
            if particle.lifetime <= 0:
                return particle
        return Particle(self, (0, 0), self.game, (0, 0, 0))  # Default particle

    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


class Particle(pg.sprite.Sprite):
    def __init__(self, system: ParticleSystem, pos: tuple, game, color):
        super().__init__()
        self.image = pg.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = Vector2(*pos)
        self.color = color
        self.system = system

        self.lifetime = self.system.particle_lifetime
        self.vel = Vector2(game.RNG.uniform(-self.system.particle_speed, self.system.particle_speed),
                           game.RNG.uniform(-self.system.particle_speed, self.system.particle_speed))
        self.size = 4
        self.game = game
    
    def __hash__(self) -> int:
        return hash((self.pos, self.color))

    def update(self):
        self.vel *= 0.97
        self.pos += self.vel
        self.lifetime -= 1

    def reset(self, pos, color):
        self.pos = pos
        self.color = color
        self.lifetime = self.system.particle_lifetime
        self.vel = Vector2(self.game.RNG.uniform(-self.system.particle_speed, self.system.particle_speed),
                           self.game.RNG.uniform(-self.system.particle_speed, self.system.particle_speed))

    def draw(self, surface):
        pg.draw.ellipse(surface, self.color, pg.Rect(self.pos, (self.size, self.size)))
