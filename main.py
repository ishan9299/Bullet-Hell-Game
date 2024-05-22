import pygame
import math
import time

screen_width = 640
screen_height = 480
game_window = pygame.display.set_mode((screen_width, screen_height))
bullets = []
playerbullets = []

class Projectile:
    def __init__(self, pos_x, pos_y, dir_x, dir_y, velocity, radius):
        self.pos = pygame.math.Vector2(pos_x, pos_y)
        self.dir = pygame.math.Vector2(dir_x, dir_y).normalize()
        self.velocity = velocity
        self.radius = radius
        self.collided = False

class Spawner:
    def __init__(self, pos_x, pos_y, dir_x, dir_y, bullet_radius):
        self.pos = pygame.math.Vector2(pos_x, pos_y)
        self.bullet_radius = bullet_radius
        self.dir = pygame.math.Vector2(dir_x, dir_y).normalize()

    def spawnBullet(self):
        velocity = 4
        projectile = Projectile(self.pos.x, self.pos.y, self.dir.x,
                                self.dir.y, velocity, self.bullet_radius)
        bullets.append(projectile)

class Enemy:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = 40
        self.num_of_spawners = 20
        self.spawners = []
        self.spawners_circle_radius = 80
        self.fire_rate = 0.3
        self.shot_curr_time = 0
        self.shot_prev_time = 0
        self.shot_delta_time = 0

    def generateSpawners(self):
        num_of_spawners = self.num_of_spawners
        angles = (2 * math.pi) / num_of_spawners

        bullet_radius = 2 * self.spawners_circle_radius * math.cos((math.pi / 2) - (angles / 4))

        for index in range(self.num_of_spawners):
            pos_x = self.pos.x + (self.spawners_circle_radius * math.cos((angles / 2) + (index * (angles))))
            pos_y = self.pos.y + (self.spawners_circle_radius * math.sin((angles / 2) + (index * (angles))))
            dir_x = pos_x - self.pos.x
            dir_y = pos_y - self.pos.y
            spawner = Spawner(pos_x, pos_y, dir_x, dir_y, bullet_radius)
            self.spawners.append(spawner)

    def fireShot(self):
        self.shot_curr_time = time.time()
        self.shot_delta_time = self.shot_curr_time - self.shot_prev_time
        num_of_bullets = self.shot_delta_time / self.fire_rate

        for bullet in range(int(num_of_bullets)):
            for idx in range(self.num_of_spawners):
                self.spawners[idx].spawnBullet()
            self.shot_prev_time = time.time()

    def drawEnemy(self):
        pygame.draw.circle(game_window, pygame.Color(255, 255, 255),
                           [self.pos.x, self.pos.y], self.radius, 1)

class Player:
    def __init__(self, x, y):
        self.mouse = pygame.math.Vector2(0, 0)
        self.height = 20
        self.angle = 0
        self.hitbox_radius = self.height * (2/3)
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = 100
        self.shot_curr_time = 0
        self.shot_prev_time = 0
        self.shot_delta_time = 0
        player_head = pygame.math.Vector2(x, (y - self.hitbox_radius))
        self.spawner = Spawner(player_head.x, player_head.y,
                               (player_head.x - self.pos.x),
                               (player_head.y - self.pos.y), 5)

    def drawPlayer(self, mouse_x, mouse_y):
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
        
        pygame.draw.circle(game_window, pygame.Color(255, 255, 255),
                           self.pos, self.hitbox_radius, 1)
        pygame.draw.polygon(game_window, pygame.Color(255, 255, 255), [v1, v2, v3])

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

        if keys_pressed[pygame.K_SPACE]:
            self.fireShot(deltaTime)

    def fireShot(self, shot_delta_time):
        num_of_bullets = shot_delta_time / enemy.fire_rate

        for bullet in range(int(num_of_bullets)):
            self.spawner.spawnBullet()


    def checkPlayerBoundsX(self):
        in_bounds_x = True
        if self.pos.x < self.hitbox_radius:
            in_bounds_x = False
        if self.pos.x > screen_width - self.hitbox_radius:
            in_bounds_x = False

        return in_bounds_x

    def checkPlayerBoundsY(self):
        in_bounds_y = True
        if self.pos.y < self.hitbox_radius:
            in_bounds_y = False
        if self.pos.y > screen_height - self.hitbox_radius:
            in_bounds_y = False

        return in_bounds_y


def main():
    pygame.init()

    pygame.key.set_repeat()

    running = True
    player = Player(screen_width/2, screen_height/2)

    enemy = Enemy(screen_width/2, screen_height/2)
    enemy.generateSpawners()

    player.shot_prev_time = time.time()

    prev_time = time.time()
    shot_prev_time = time.time()

    while running:
        game_window.fill((0, 0, 0))

        now = time.time()
        dt = now - prev_time
        prev_time = now

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.drawPlayer(mouse_x, mouse_y)
        player.handleInput(dt)

        enemy.drawEnemy()

        shot_curr_time = time.time()
        shot_delta_time = shot_curr_time - shot_prev_time

        num_of_bullets = shot_delta_time / enemy.fire_rate

        for bullet in range(int(num_of_bullets)):
            for idx in range(enemy.num_of_spawners):
                enemy.spawners[idx].spawnBullet()
            shot_prev_time = time.time()

        for bullet in bullets:
            bullet.pos.x += shot_delta_time * bullet.dir.x * 0.3
            bullet.pos.y += shot_delta_time * bullet.dir.y * 0.3
            if bullet.pos.y > screen_height + bullet.radius:
                bullets.remove(bullet)
                continue
            elif bullet.pos.x > screen_width + bullet.radius:
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
            pygame.draw.circle(game_window, pygame.Color(255, 0, 0),
                               bullet.pos, bullet.radius, 1)

        pygame.display.flip()


if __name__ == "__main__":
    main()
