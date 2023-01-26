import random

import pygame
from math import sin, pi


class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'ground'

        ground_surf = pygame.image.load('data/sprites/ground.png').convert_alpha()
        self.image = pygame.transform.scale(ground_surf, pygame.math.Vector2(ground_surf.get_size()) * scale_factor)
        self.rect = self.image.get_rect(bottomleft=(0, 800))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.mask = pygame.mask.from_surface(self.image)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, direction):
        super().__init__(groups)
        self.sprite_type = 'obstacle'

        self.direction = direction
        self.scale_factor = scale_factor
        file = f'data/sprites/spike_left.png' if direction == 'left' else f'data/sprites/spike_right.png'
        surf = pygame.image.load(file).convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)

        self.rect = self.image.get_rect(midtop=(0, 35 + random.randint(0, 9) * 70))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.pos.x = 480 if direction == 'right' else -30
        self.rect.x = self.pos.x

        self.mask = pygame.mask.from_surface(self.image)

    def slide(self, dt, direction):
        if direction == 1:
            self.pos.x += (dt * 150)
            self.rect.x = self.pos.x
        else:
            self.pos.x -= (dt * 150)
            self.rect.x = self.pos.x


class Bird(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        self.next_spikes = '1000000000'
        self.dead = False

        surf = pygame.image.load('data/sprites/bird.png').convert_alpha()
        self.normal_image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)

        jsurf = pygame.image.load('data/sprites/birdFly.png').convert_alpha()
        self.jump_image = pygame.transform.scale(jsurf, pygame.math.Vector2(surf.get_size()) * scale_factor)

        surfd = pygame.image.load('data/sprites/birdDead.png').convert_alpha()
        self.dim = pygame.transform.scale(surfd, pygame.math.Vector2(surf.get_size()) * scale_factor)

        self.image = self.normal_image

        self.rect = self.image.get_rect(topleft=(-50, 320))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.gravity = 1700
        self.direction = 0
        self.velocity = 16
        self.rotation = 1

        self.idleFall = 0

        self.dt_jump = 0
        self.jump_done = False

        self.mask = pygame.mask.from_surface(self.image)

        self.import_frames(scale_factor)
        self.frame_index = 0

        self.score = 0

        self.jump_sound = pygame.mixer.Sound('data/sound effects/jump.wav')
        self.jump_sound.set_volume(0.15)

        self.point_sound = pygame.mixer.Sound('data/sound effects/point.wav')
        self.point_sound.set_volume(0.15)

    def showup(self, dt):
        v = 15000 * dt - ((dt * 1000) ** 2) / 2
        self.pos.x += (v / 75)
        self.rect.x = self.pos.x

    def apply_gravity(self, dt):
        self.direction += self.gravity * dt

        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)

        self.pos.x += (self.velocity / 75)
        self.rect.x = self.pos.x

        symbols = '01'
        self.next_spikes = '1' + ''.join(random.choice(symbols) for _ in range(9))

        if self.pos.x <= 0 or self.pos.x > 480 - self.mask.get_rect().width:
            self.velocity = -self.velocity
            self.rotation = -self.rotation

            if not self.dead:
                self.score += 1
                self.point_sound.play()

            if not self.jump_done:
                self.image = pygame.transform.flip(self.normal_image, True,
                                                   False) if self.rotation == -1 else self.normal_image
            else:
                self.image = pygame.transform.flip(self.jump_image, True,
                                                   False) if self.rotation == -1 else self.jump_image

    def jump(self):
        self.jump_sound.play()
        self.direction = -500
        self.image = pygame.transform.flip(self.jump_image, True,
                                           False) if self.rotation == -1 else self.jump_image
        self.jump_done = True

    def import_frames(self, scale_factor):
        self.frames = []
        surf = pygame.image.load('data/sprites/birdIdle.png').convert_alpha()
        scaled_surface = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)
        self.frames.append(self.normal_image)
        self.frames.append(scaled_surface)

    def update(self, dt):
        if not self.dead:
            self.apply_gravity(dt)

        if self.jump_done:
            if self.dt_jump > 0.3:
                self.jump_done = False
                self.dt_jump = 0
                self.image = pygame.transform.flip(self.normal_image, True,
                                                   False) if self.rotation == -1 else self.normal_image
            self.dt_jump += dt

    def idle(self, dt):
        self.pos.y += (sin(self.idleFall * pi / 180) / 10)
        self.rect.y = self.pos.y
        self.idleFall += 0.25

        self.frame_index += 2 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def dead_anim(self, dt):
        self.image = pygame.transform.flip(self.dim, True, False) if self.rotation == -1 else self.dim

        self.pos.y += ((dt * 2.5) ** 2) / 2
        self.pos.x += -0.1 if self.rotation == -1 else 0.1
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
