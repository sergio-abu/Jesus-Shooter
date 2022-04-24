import pygame
import os
import random

pygame.font.init()

WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Armageddon')

# CHARACTER ASSETS
JESUS = pygame.image.load(os.path.join('assets', 'jesus.png'))
SATAN = pygame.image.load(os.path.join('assets', 'satan.png'))
JUDAS = pygame.image.load(os.path.join('assets', 'judas.png'))
CENTURION = pygame.image.load(os.path.join('assets', 'centurion.png'))

# SHOT ASSETS
JESUS_SHOT = pygame.image.load(os.path.join('assets', 'jesus_shot.png'))
SATAN_SHOT = pygame.image.load(os.path.join('assets', 'satan_shot.png'))
JUDAS_SHOT = pygame.image.load(os.path.join('assets', 'judas_shot.png'))
CENTURION_SHOT = pygame.image.load(os.path.join('assets', 'centurion_shot.png'))

# BACKGROUND
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background.png')), (WIDTH, HEIGHT))


class Shot:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Character:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.char_img = None
        self.shot_img = None
        self.shots = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.char_img, (self.x, self.y))
        for shot in self.shots:
            shot.draw(window)

    def move_shot(self, vel, obj):
        self.cooldown()
        for shot in self.shots:
            shot.move(vel)
            if shot.off_screen(HEIGHT):
                self.shots.remove(shot)
            elif shot.collision(obj):
                obj.health -= 10
                self.shots.remove(shot)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            shot = Shot(self.x, self.y, self.shot_img)
            self.shots.append(shot)
            self.cool_down_counter = 1

    def get_width(self):
        return self.char_img.get_width()

    def get_height(self):
        return self.char_img.get_height()


class Player(Character):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.char_img = JESUS
        self.shot_img = JESUS_SHOT
        self.mask = pygame.mask.from_surface(self.char_img)  # pixel collision
        self.max_health = health

    def move_shot(self, vel, objs):
        self.cooldown()
        for shot in self.shots:
            shot.move(vel)
            if shot.off_screen(HEIGHT):
                self.shots.remove(shot)
            else:
                for obj in objs:
                    if shot.collision(obj):
                        objs.remove(obj)
                        if shot in self.shots:
                            self.shots.remove(shot)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.char_img.get_height() + 10,
                          self.char_img.get_width(), 10))

        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.char_img.get_height() + 10,
                          self.char_img.get_width() * (self.health / self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)


class Enemy(Character):
    ENEMY_MAP = {
        'satan': (SATAN, SATAN_SHOT),
        'judas': (JUDAS, JUDAS_SHOT),
        'centurion': (CENTURION, CENTURION_SHOT)
    }

    def __init__(self, x, y, enemy, health=100):
        super().__init__(x, y, health)
        self.char_img, self.shot_img = self.ENEMY_MAP[enemy]
        self.mask = pygame.mask.from_surface(self.char_img)  # pixel collision

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    fps = 60
    level = 0
    resurrections = 9
    main_font = pygame.font.SysFont('comicsans', 40)
    title_font = pygame.font.SysFont('comicsans', 100)

    player_vel = 10
    player = Player(370, 570)

    enemies = []
    wave_length = 5
    enemy_vel = 2

    shot_vel = 5

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BACKGROUND, (0, 0))

        # text draw
        level_label = main_font.render(f'LEVEL: {level}', True, (0, 255, 255))
        resurrections_label = main_font.render(f'RESURRECTIONS: {resurrections}', True, (255, 0, 0))

        WIN.blit(level_label, (10, (HEIGHT - 60)))
        WIN.blit(resurrections_label, (10, HEIGHT - 30))

        # draw character
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = title_font.render('GAME OVER', True, (255, 0, 0))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 450))

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if player.health <= 0:
            resurrections -= 1
            player.health = player.max_health

        if resurrections <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(
                    ['satan', 'judas', 'centurion']
                ))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel >= -30:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() <= WIDTH + 30:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel >= 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() <= HEIGHT - 30:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_shot(shot_vel, player)

            if random.randrange(0, 4 * fps) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 50
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT + 155:
                resurrections -= 1
                enemies.remove(enemy)

        player.move_shot(-shot_vel*2, enemies)


def main_menu():
    title_font = pygame.font.SysFont('comicsans', 70)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render('PRESS THE MOUSE TO BEGIN', True, (0, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 450))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
