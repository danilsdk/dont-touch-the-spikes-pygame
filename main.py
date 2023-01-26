import sqlite3

import pygame
import sys
import time
from sprites import Ground, Bird, Obstacle

FPS, WIDTH, HEIGHT = 75, 480, 800


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Don't touch the spikes")
        self.clock = pygame.time.Clock()

        self.colors = ['light blue', 'light green', 'gold2', 'orange', 'aquamarine1',
                       'pink', 'purple', 'indigo', 'springgreen', 'violet', 'red', 'cyan', 'dark green',
                       'dark orange', 'magenta', 'dark blue', 'maroon', 'darksalmon', 'orchid',
                       'black']

        self.bg_num = 0
        self.base_color = 'light gray'
        self.next_color = self.colors[self.bg_num]
        self.bg_color = 'light gray'

        self.dead_sound = pygame.mixer.Sound('data/sound effects/dead.wav')
        self.dead_sound.set_volume(0.15)

        self.highscore = None
        self.games_played = None

        self.number_of_steps = 0.8
        self.step = 0
        self.fade = False

        self.spikes_timer = 0
        self.dead_timer = 0

        self.font = pygame.font.Font('data/fonts/Blissful Thinking.otf', 33)
        self.title_font = pygame.font.Font('data/fonts/Blissful Thinking.otf', 50)
        self.score_font = pygame.font.Font('data/fonts/Sci Auralieph.otf', 120)

        self.text1 = self.font.render("CLICK", True, (255, 49, 100))
        self.text2 = self.font.render("TO JUMP", True, (255, 49, 100))
        self.title1 = self.title_font.render("DON'T TOUCH", True, 'white')
        self.title2 = self.title_font.render("THE SPIKES", True, 'white')
        self.title3 = None
        self.title4 = None
        self.title5 = self.title_font.render("GAME OVER :)", True, 'white')
        self.scoreText = self.score_font.render("0", True, self.bg_color)

        self.active = True
        self.score = "00"

        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        bg_height = pygame.image.load('data/sprites/ground.png').get_height()
        self.scale_factor = HEIGHT / bg_height

        Ground([self.all_sprites, self.collision_sprites], self.scale_factor)

        self.spikes = []

        self.bird = None

    def run(self):
        for i in range(6):
            self.spikes.append(
                Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 0.15, 'right'))
        for i in range(6):
            self.spikes.append(
                Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 0.15, 'left'))

        self.bg_color = 'light gray'
        self.bg_num = 0
        self.base_color = self.bg_color
        self.next_color = self.colors[self.bg_num]

        last_time = time.time()
        text_timer = 0
        self.dead_timer = 0
        self.spikes_timer = 0

        while True:
            last_rotation = self.bird.rotation
            dt = time.time() - last_time
            last_time = time.time()

            text_timer += dt

            if self.score != self.bird.score:
                self.render_score()
            if self.score // 5 > self.bg_num:
                self.fade = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not self.bird.dead and event.button == 1:

                    if self.active:
                        self.bird.jump()
                    else:
                        self.bird = Bird(self.all_sprites, self.scale_factor / 3)
                        self.active = True

            if self.fade:
                dv = (5 / 8) * dt
                self.bird.velocity += dv if self.bird.velocity > 0 else -dv
                self.step += dt
                if self.step < self.number_of_steps:
                    self.bg_color = [x + (((y - x) / self.number_of_steps) * self.step) for x, y in
                                     zip(pygame.color.Color(self.base_color), pygame.color.Color(self.next_color))]
                else:
                    if self.bg_num == len(self.colors) - 1:
                        self.bg_num = 0
                    else:
                        self.bg_num += 1
                    self.step = 0
                    self.base_color = self.next_color
                    self.next_color = self.colors[self.bg_num]
                    self.fade = False
                self.render_score()

            self.surface.fill(pygame.color.Color(self.bg_color))
            self.all_sprites.update(dt)
            pygame.draw.circle(self.surface, 'white', (WIDTH / 2, HEIGHT / 2 - 20), 135)

            if text_timer < 0.8:
                self.terminate_text(text_timer)

            step1 = 55 if len(str(self.score)) == 1 else 55 * (len(str(self.score)) - 1)
            step2 = 25 * str(self.score).count('1')
            self.surface.blit(self.scoreText, (195 - step1 + step2, 320))

            if self.active:
                if last_rotation != self.bird.rotation:
                    for spike in self.spikes:
                        spike.kill()
                    for i in range(6):
                        self.spikes.append(
                            Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 0.15, 'right'))
                    for i in range(6):
                        self.spikes.append(
                            Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 0.15, 'left'))

                self.collisions()

                if self.spikes[0].pos.x >= 450 and self.bird.rotation == 1:
                    for spike in self.spikes:
                        spike.slide(dt, -1)

                elif self.spikes[0].pos.x < 480 and self.bird.rotation == -1:
                    for spike in self.spikes:
                        spike.slide(dt, 1)

            else:
                self.render_score()
                if self.dead_timer <= 2:
                    self.surface.blit(self.title5, (105, 150))
                    self.bird.dead_anim(self.dead_timer)
                else:
                    for spike in self.spikes:
                        spike.kill()
                    self.games_played += 1
                    if self.score > self.highscore:
                        self.highscore = self.score

                    self.make_record()

                    self.bird.kill()
                    self.starting_screen()
                self.dead_timer += dt
            self.all_sprites.draw(self.surface)
            pygame.display.update()

    def starting_screen(self):
        self.load_stats()

        self.bird = Bird(self.all_sprites, self.scale_factor / 3)
        ready = False

        self.spikes_timer = 0

        last_time = time.time()
        text_timer = 0

        while True:
            dt = time.time() - last_time
            last_time = time.time()

            text_timer += dt

            if self.bird.pos.x < 205:
                self.bird.showup(dt)
            else:
                ready = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and ready and not self.bird.dead and event.button == 1:
                    self.active = True
                    self.bird.jump()
                    game.run()

            self.surface.fill('light gray')
            pygame.draw.circle(self.surface, 'white', (WIDTH / 2, HEIGHT / 2 - 20), 135)

            self.surface.blit(self.text1, (200, 255))
            self.surface.blit(self.text2, (182, 285))

            self.surface.blit(self.title1, (100, 65))
            self.surface.blit(self.title2, (130, 110))

            self.surface.blit(self.title3, (145, 620))
            self.surface.blit(self.title4, (130, 650))

            self.all_sprites.draw(self.surface)
            self.bird.idle(dt)

            pygame.display.update()

    def terminate_text(self, dt):
        x = ((dt * 50) ** 2 / 2)
        self.surface.blit(self.text1, (200 - x, 255))
        self.surface.blit(self.text2, (182 - x, 285))

        self.surface.blit(self.title1, (100 - x, 65))
        self.surface.blit(self.title2, (130 - x, 110))

        self.surface.blit(self.title3, (145 - x, 620))
        self.surface.blit(self.title4, (130 - x, 650))

    def render_score(self):
        self.score = self.bird.score
        self.scoreText = self.score_font.render(str(f"{self.score:02d}"), True, (pygame.color.Color(self.bg_color)))

    def collisions(self):
        if pygame.sprite.spritecollide(self.bird, self.collision_sprites, False, pygame.sprite.collide_mask):
            for sprite in self.collision_sprites.sprites():
                if sprite.sprite_type == 'obstacle':
                    self.dead_sound.play()
                    self.bird.rotation = -self.bird.rotation
                    self.base_color = 'light gray'
                    self.next_color = self.colors[0]
                    self.bg_color = 'light gray'
                    self.bg_num = 0

                    self.number_of_steps = 0.8
                    self.step = 0
                    self.fade = False

                    self.bird.dead = True
                    self.active = False
                    break

        if self.bird.rect.top <= 48 or self.bird.rect.bottom > 720:
            self.dead_sound.play()
            self.base_color = 'light gray'
            self.next_color = self.colors[0]
            self.bg_color = 'light gray'
            self.bg_num = 0

            self.number_of_steps = 0.8
            self.step = 0
            self.fade = False

            self.bird.dead = True
            self.bird.rotation = -self.bird.rotation
            self.active = False

    def load_stats(self):
        conn = sqlite3.connect('data/database.sqlite')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS stats (
                    gplayed     INTEGER NOT NULL,
                    highscore   INTEGER NOT NULL
        );""")

        if len(list(c.execute("""select * from stats"""))) == 0:
            c.execute(f'''insert into stats values (0, 0)''')

        res = list(c.execute("""select * from stats"""))
        self.games_played = res[0][0]
        self.highscore = res[0][1]

        self.title3 = self.font.render(f"BEST SCORE: {self.highscore}", True, 'white')
        self.title4 = self.font.render(f"GAMES PLAYED: {self.games_played}", True, 'white')

        conn.commit()
        conn.close()

    def make_record(self):
        conn = sqlite3.connect('data/database.sqlite')
        c = conn.cursor()

        c.execute(f'''update stats set highscore = {self.highscore}, gplayed = {self.games_played}''')

        conn.commit()
        conn.close()


if __name__ == '__main__':
    game = Game()
    game.starting_screen()
