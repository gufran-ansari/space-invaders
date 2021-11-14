import pygame
import os
import random
import time
pygame.font.init()

# Window and size
width, height = 800, 700
win = pygame.display.set_mode((width, height))
# Name of the window
pygame.display.set_caption("Space Shooter")


# Load Images
red_ship = pygame.image.load(os.path.join('assets', 'red_ship.png'))
green_ship = pygame.image.load(os.path.join('assets', 'green_ship.png'))
blue_ship = pygame.image.load(os.path.join('assets', 'blue_ship.png'))

# Player Ship
yellow_ship = pygame.image.load(os.path.join('assets', 'yellow_ship.png'))

# Laser
red_laser = pygame.image.load(os.path.join('assets', 'red_laser.png'))
green_laser = pygame.image.load(os.path.join('assets', 'green_laser.png'))
blue_laser = pygame.image.load(os.path.join('assets', 'blue_laser.png'))
yellow_laser = pygame.image.load(os.path.join('assets', 'yellow_laser.png'))

# Backgroung
# to fill the background image in window, we use 'pygame.transform.scale' with height and width we declare earlier.
bg = pygame.transform.scale(pygame.image.load(
    os.path.join('assets', 'bg.png')), (width, height))


class Laser:
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
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30  # class variable.

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

        for laser in self.lasers:
            laser.draw(window)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 5 # player's ship can shoots 5 times per seconds

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_ship
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def healthBar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                                               self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width()*(self.health / self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthBar(window)


class Enemy(Ship):
    color_map = {
        "red": (red_ship, red_laser),
        "green": (green_ship, green_laser),
        "blue": (blue_ship, blue_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y))


def main():
    # FPS(Frames Per Seconds) as the number goes higher then game is gonna run Faster.
    # If variables declared in all capitals then they're constant. and can't change the value of them.
    # FPS = 60 means you're going to show 60 frames per second.
    FPS = 60
    run = True
    level = 0
    lives = 5
    score = 0
    main_font = pygame.font.SysFont("comicsans", 25)
    lost_font = pygame.font.SysFont("comicsans", 50)
    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 10
    player_vel = 10
    player = Player(350, 580)
    lost = False
    lost_count = 0
    clock = pygame.time.Clock()

    def redraw_window():
        # Cordinates in pygame start from Top Left corner. The x will be remain same to increase but 'y' will increase downwards.
        win.blit(bg, (0, 0))

        # Draw Text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        win.blit(lives_label, (20, 20))
        win.blit(level_label, (width - level_label.get_width() - 20, 20))
        # .get_width() is used to get the padding used in level_label so both text going to be on same line and have same padding.

        for enemy in enemies:
            enemy.draw(win)

        player.draw(win)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            win.blit(lost_label, (width / 2 -
                                  int(lost_label.get_width()) / 2, 350))

        # To Refresh Window
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # Enemy Ship coming down.
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(
                    50, width - 100), random.randrange(-1500, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            # To exit the game.
            if event.type == pygame.QUIT:
                quit()

        # To move player
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # Left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < width:  # Right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # Up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < height:  # Down
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            # [:] adding this means we create a copy of enemies so it wont occur any error.
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)

    run = True
    while run:
        win.blit(bg, (0, 0))
        title_label = title_font.render("Press Any Key To Begin..!!", 1, (255, 255, 255))
        win.blit(title_label, (width / 2 - title_label.get_width() / 2, 350))
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()


main_menu()
