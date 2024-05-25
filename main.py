import pygame
import math
import time

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

pygame.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
backbuffer = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

font_small = pygame.font.SysFont('Arial', 20)
font_big = pygame.font.SysFont('Arial', 24)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
WHITE = pygame.Color(255, 255, 255)

circles = []
bullets = []
playerbullets = []

class Bullet:
    def __init__(self, pos_x, pos_y, dir_x, dir_y, radius):
        self.pos = pygame.math.Vector2(pos_x, pos_y)
        self.dir = pygame.math.Vector2(dir_x, dir_y)
        self.radius = radius
        self.collided = False

    def checkCollision(self, entity):
        v = entity.pos - self.pos
        dist = v.magnitude()
        if dist < (self.radius + entity.hitbox_radius):
            self.collided = True
            entity.health -= 1
            # print(entity.health)

class Spawner:
    def __init__(self, pos_x, pos_y, dir_x, dir_y, fire_rate, bullet_radius):
        self.pos = pygame.math.Vector2(pos_x, pos_y)
        self.fire_rate = fire_rate
        self.dir = pygame.math.Vector2(dir_x, dir_y).normalize()
        self.bullet_radius = bullet_radius

    def spawnBullet(self, bullets_arr):
        bullet = Bullet(self.pos.x, self.pos.y, self.dir.x, self.dir.y, self.bullet_radius)
        bullets_arr.append(bullet)

class Enemy:
    def __init__(self, pos_x, pos_y, radius):
        self.pos = pygame.math.Vector2(pos_x, pos_y)
        self.radius = radius
        self.spawners = []
        self.num_spawners = 24
        self.spawner_angular_vel = 2
        self.fire_rate = 0.3
        self.phase = 1
        self.velocity = pygame.math.Vector2(40, 0)
        self.acceleration = pygame.math.Vector2(-4, 0)
        self.health = 150
        self.full_health = self.health
        self.hitbox_radius = self.radius

    def generateSpawners(self):
        if self.phase == 1:

            self.spawner_angular_vel = 20
            self.fire_rate = 0.08

            dir = pygame.math.Vector2(0, 1).normalize()
            spawner = Spawner(self.pos.x, self.pos.y, dir.x, dir.y, self.fire_rate, 2)
            self.spawners.append(spawner)

        elif self.phase == 2:

            sector_angles = (2 * math.pi) / self.num_spawners
            self.spawner_angular_vel = 10
            self.fire_rate = 0.5

            bullet_radius = 2
            for index in range(self.num_spawners):
                slope_angle = (index * sector_angles) + (sector_angles / 2)

                pos_x = self.pos.x + (self.radius * math.cos(slope_angle))
                pos_y = self.pos.y + (self.radius * math.sin(slope_angle))
                dir = pygame.math.Vector2(pos_x - self.pos.x, pos_y - self.pos.y).normalize()

                spawner = Spawner(pos_x, pos_y, dir.x, dir.y, self.fire_rate, bullet_radius)
                self.spawners.append(spawner)

    def oscillate(self, delta_time):
        vel = self.acceleration.x * delta_time
        self.velocity.x += vel
        self.pos.x += self.velocity.x * delta_time

        if self.pos.x > SCREEN_WIDTH/2:
            self.acceleration.x = -4

        if self.pos.x < SCREEN_WIDTH/2:
            self.acceleration.x = 4
    
    def spawnerUpdate(self, delta_time):
        if self.phase == 1:
            angle = delta_time * self.spawner_angular_vel
            for spawner in self.spawners:
                spawner.pos.x = self.pos.x
                spawner.pos.y = self.pos.y

                new_x = ((spawner.dir.x * math.cos(angle)) - (math.sin(angle) * spawner.dir.y))
                new_y = ((spawner.dir.x * math.sin(angle)) + (math.cos(angle) * spawner.dir.y))

                spawner.dir = pygame.math.Vector2(new_x, new_y)
                spawner.dir = spawner.dir.normalize()

        elif self.phase == 2:
            index = 0
            angle = delta_time * self.spawner_angular_vel
            for spawner in self.spawners:
                spawner.pos.x -= self.pos.x
                spawner.pos.y -= self.pos.y

                rotated_x = (spawner.pos.x) * math.cos(angle) - (spawner.pos.y) * math.sin(angle)
                rotated_y = (spawner.pos.x) * math.sin(angle) + (spawner.pos.y) * math.cos(angle)

                spawner.pos.x = rotated_x + self.pos.x
                spawner.pos.y = rotated_y + self.pos.y

                spawner.dir.x = spawner.pos.x - self.pos.x
                spawner.dir.y = spawner.pos.y - self.pos.y
                spawner.dir = spawner.dir.normalize()

    def draw(self, delta_time):
        pygame.draw.circle(screen, RED, self.pos, self.radius, 1)
        self.oscillate(delta_time)
        self.spawnerUpdate(delta_time)

class Player:
    def __init__(self, x, y):
        self.mouse = pygame.math.Vector2(0, 0)
        self.height = 16
        self.angle = 0
        self.hitbox_radius = self.height * (2/3)
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = 100
        self.shot_curr_time = 0
        self.shot_prev_time = 0
        self.shot_delta_time = 0
        self.fire_rate = 0.3
        self.health = 5
        self.full_health = self.health
        player_head = pygame.math.Vector2(x, (y - self.hitbox_radius))
        self.spawner = Spawner(player_head.x, player_head.y,
                               (player_head.x - self.pos.x),
                               (player_head.y - self.pos.y), 0.1, 5)

    def draw(self, mouse_x, mouse_y):
        self.mouse.x = mouse_x
        self.mouse.y = mouse_y

        self.angle = (math.pi/2) - math.atan2(-(self.mouse.y - self.pos.y), (self.mouse.x - self.pos.x))

        base_half = self.height/1.732

        v1 = pygame.math.Vector2(self.pos.x, self.pos.y - self.hitbox_radius)
        v2 = pygame.math.Vector2((v1.x + base_half), (v1.y + self.height))
        v3 = pygame.math.Vector2((v1.x - base_half), (v1.y + self.height))

        v1.x -= self.pos.x
        v1.y -= self.pos.y
        rotated_x = (v1.x) * math.cos(self.angle) - (v1.y) * math.sin(self.angle)
        rotated_y = (v1.x) * math.sin(self.angle) + (v1.y) * math.cos(self.angle)
        v1.x = rotated_x + self.pos.x
        v1.y = rotated_y + self.pos.y

        v2.x -= self.pos.x
        v2.y -= self.pos.y
        rotated_x = (v2.x) * math.cos(self.angle) - (v2.y) * math.sin(self.angle)
        rotated_y = (v2.x) * math.sin(self.angle) + (v2.y) * math.cos(self.angle)
        v2.x = rotated_x + self.pos.x
        v2.y = rotated_y + self.pos.y

        v3.x -= self.pos.x
        v3.y -= self.pos.y
        rotated_x = (v3.x) * math.cos(self.angle) - (v3.y) * math.sin(self.angle)
        rotated_y = (v3.x) * math.sin(self.angle) + (v3.y) * math.cos(self.angle)
        v3.x = rotated_x + self.pos.x
        v3.y = rotated_y + self.pos.y

        self.spawner.pos = v1
        self.spawner.dir.x = v1.x - self.pos.x 
        self.spawner.dir.y = v1.y - self.pos.y
        
        # pygame.draw.circle(backbuffer, pygame.Color(255, 255, 255),
        #                    self.pos, self.hitbox_radius, 1)
        pygame.draw.polygon(backbuffer, pygame.Color(255, 255, 255), [v1, v2, v3])

    def handleInput(self, deltaTime):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_w]:
            self.pos.y -= self.velocity * deltaTime

            if not self.checkPlayerBoundsY():
                self.pos.y += self.velocity * deltaTime

        if keys_pressed[pygame.K_a]:
            self.pos.x -= self.velocity * deltaTime

            if not self.checkPlayerBoundsX():
                self.pos.x += self.velocity * deltaTime

        if keys_pressed[pygame.K_s]:
            self.pos.y += self.velocity * deltaTime

            if not self.checkPlayerBoundsY():
                self.pos.y -= self.velocity * deltaTime

        if keys_pressed[pygame.K_d]:
            self.pos.x += self.velocity * deltaTime

            if not self.checkPlayerBoundsX():
                self.pos.x -= self.velocity * deltaTime

    def checkPlayerBoundsX(self):
        in_bounds_x = True
        if self.pos.x < self.hitbox_radius:
            in_bounds_x = False
        if self.pos.x > SCREEN_WIDTH - self.hitbox_radius:
            in_bounds_x = False

        return in_bounds_x

    def checkPlayerBoundsY(self):
        in_bounds_y = True
        if self.pos.y < self.hitbox_radius:
            in_bounds_y = False
        if self.pos.y > SCREEN_HEIGHT - self.hitbox_radius:
            in_bounds_y = False

        return in_bounds_y


def main():
    pygame.key.set_repeat()

    enemy = Enemy(SCREEN_WIDTH/2, SCREEN_HEIGHT/3, 40)
    enemy.phase = 1
    enemy.generateSpawners()

    player = Player(SCREEN_WIDTH/2, (2*SCREEN_HEIGHT)/3)
    player.shot_prev_time = time.time()

    prev_time = time.time()
    shot_prev_time = time.time()

    phase_switch_after = 30
    phase_switch_break = 5

    running = True

    game_over = False
    game_won = False

    while running:

        backbuffer.fill((0, 0, 0))

        if game_over == False:
            curr_time = time.time()
            delta_time = curr_time - prev_time
            prev_time = curr_time

            mouse_x, mouse_y = pygame.mouse.get_pos()
            player.draw(mouse_x, mouse_y)

            player.shot_curr_time = time.time()
            player.shot_delta_time = player.shot_curr_time - player.shot_prev_time
            num_bullets = player.shot_delta_time / player.fire_rate
            for _ in range(int(num_bullets)):
                player.spawner.spawnBullet(playerbullets)
                player.shot_prev_time = time.time()

            player.handleInput(delta_time)

            if (enemy.health < (enemy.full_health * 0.5) and enemy.phase == 1):
                # print("switching phase")
                enemy.phase = 2
                enemy.spawners.clear()
                enemy.generateSpawners()
                phase_switch_prev = time.time()
                phase_switch_delta = 0
                while phase_switch_delta > 3:
                    phase_switch_curr = time.time()
                    phase_switch_delta = phase_switch_curr - phase_switch_prev



            enemy.draw(delta_time)

            shot_curr_time = time.time()
            shot_delta_time = shot_curr_time - shot_prev_time
            num_bullets = shot_delta_time / enemy.fire_rate

            for _ in range(int(num_bullets)):
                for spawner in enemy.spawners:
                    spawner.spawnBullet(bullets)
                shot_prev_time = time.time()


            bullet_index = 0
            for bullet in bullets:
                displacement_x = delta_time * bullet.dir.x * 50
                displacement_y = delta_time * bullet.dir.y * 50

                bullet.pos.x += displacement_x
                bullet.pos.y += displacement_y

                bullet.checkCollision(player)

                if bullet.pos.y > SCREEN_HEIGHT + bullet.radius:
                    bullets.remove(bullet)
                    continue
                elif bullet.pos.x > SCREEN_WIDTH + bullet.radius:
                    bullets.remove(bullet)
                    continue
                elif bullet.pos.y < -bullet.radius:
                    bullets.remove(bullet)
                    continue
                elif bullet.pos.x < -bullet.radius:
                    bullets.remove(bullet)
                    continue
                elif bullet.collided == True:
                    bullets.remove(bullet)
                    continue

                pygame.draw.circle(screen, GREEN, bullet.pos, bullet.radius, 1)

            for bullet in playerbullets:
                displacement_x = delta_time * bullet.dir.x * 50
                displacement_y = delta_time * bullet.dir.y * 50

                bullet.pos.x += displacement_x
                bullet.pos.y += displacement_y

                bullet.checkCollision(enemy)

                if bullet.pos.y > SCREEN_HEIGHT + bullet.radius:
                    playerbullets.remove(bullet)
                    continue
                elif bullet.pos.x > SCREEN_WIDTH + bullet.radius:
                    playerbullets.remove(bullet)
                    continue
                elif bullet.pos.y < -bullet.radius:
                    playerbullets.remove(bullet)
                    continue
                elif bullet.pos.x < -bullet.radius:
                    playerbullets.remove(bullet)
                    continue
                elif bullet.collided == True:
                    playerbullets.remove(bullet)
                    continue

                pygame.draw.circle(screen, BLUE, bullet.pos, bullet.radius, 1)

            if player.health < 0:
                game_won = False
                game_over = True
                # print(game_over)
            elif enemy.health < 0:
                game_won = True
                game_over = True
                # print(game_over)
        else:

            if game_won == True:
                draw_text("You Won", font_big, WHITE, 130, 200)
            else:
                draw_text("You Died", font_big, WHITE, 130, 200)

            key = pygame.key.get_pressed()

            draw_text("PRESS SPACE TO PLAY AGAIN", font_big, WHITE, 40, 300)

            if key[pygame.K_SPACE]:
                game_over = False
                enemy.health = enemy.full_health
                player.health = player.full_health
                enemy = Enemy(SCREEN_WIDTH/2, SCREEN_HEIGHT/3, 40)
                enemy.phase = 1
                enemy.generateSpawners()

                player = Player(SCREEN_WIDTH/2, (2*SCREEN_HEIGHT)/3)
                player.shot_prev_time = time.time()

                prev_time = time.time()
                shot_prev_time = time.time()

                bullets.clear()
                playerbullets.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        pygame.display.flip()

if __name__ == "__main__":
    main()
