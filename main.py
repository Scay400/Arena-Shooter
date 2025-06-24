import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арена шутер")


WHITE = (0, 0, 0)
BLACK = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 20 
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.bullets = []
        self.shoot_cooldown = 0
        self.color = BLUE
    
    def move(self, keys):
        if keys[pygame.K_a] and self.x - self.size//2 > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x + self.size//2 < WIDTH:
            self.x += self.speed
        if keys[pygame.K_w] and self.y - self.size//2 > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y + self.size//2 < HEIGHT:
            self.y += self.speed
    
    def shoot(self, target_x, target_y):
        if self.shoot_cooldown == 0:
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx = dx / dist * 10
                dy = dy / dist * 10
                self.bullets.append([self.x, self.y, dx, dy])
                self.shoot_cooldown = 10
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if (bullet[0] < 0 or bullet[0] > WIDTH or 
                bullet[1] < 0 or bullet[1] > HEIGHT):
                self.bullets.remove(bullet)
    
    def draw(self, screen):

        pygame.draw.rect(screen, self.color, 
                         (self.x - self.size//2, self.y - self.size//2, 
                          self.size, self.size))
        

        health_bar_length = 50
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - health_bar_length//2, self.y - 30, 
                                      health_bar_length, 5))
        pygame.draw.rect(screen, GREEN, (self.x - health_bar_length//2, self.y - 30, 
                                        health_bar_length * health_ratio, 5))
        

        for bullet in self.bullets:
            pygame.draw.rect(screen, BLACK, 
                            (int(bullet[0]) - 2, int(bullet[1]) - 2, 4, 4))


class Enemy:
    def __init__(self, x, y, enemy_type="shooter"):
        self.x = x
        self.y = y
        self.size = 16  # Размер квадрата
        self.speed = random.uniform(1.0, 2.5)
        self.health = 30
        self.color = RED
        self.type = enemy_type
        self.bullets = []
        self.shoot_cooldown = random.randint(30, 60)
        self.direction_change_cooldown = 0
        

        if self.type == "shooter":
            self.color = RED
        elif self.type == "rusher":
            self.color = (255, 100, 100)
            self.speed *= 1.5
        elif self.type == "tank":
            self.color = (150, 0, 0)
            self.health = 60
            self.size = 22
    
    def move(self, player_x, player_y):

        if self.type == "rusher":
            dx = player_x - self.x
            dy = player_y - self.y
        elif self.type == "tank":
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 200:
                dx = -dx
                dy = -dy
        else:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 150:
                dx = -dx
                dy = -dy
            elif dist > 300:
                pass
            else:
                if self.direction_change_cooldown <= 0:
                    self.direction_change_cooldown = 30
                    self.sideways_dir = random.choice([-1, 1])
                else:
                    self.direction_change_cooldown -= 1
                dx, dy = -dy * self.sideways_dir, dx * self.sideways_dir
        
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
        
        self.x += dx
        self.y += dy
    
    def shoot_at_player(self, player_x, player_y):
        if self.shoot_cooldown <= 0:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx = dx / dist * 7
                dy = dy / dist * 7
                
                if self.type == "shooter":
                    dx += random.uniform(-0.5, 0.5)
                    dy += random.uniform(-0.5, 0.5)
                
                self.bullets.append([self.x, self.y, dx, dy])
                self.shoot_cooldown = 60 if self.type == "tank" else 30
        else:
            self.shoot_cooldown -= 1
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if (bullet[0] < 0 or bullet[0] > WIDTH or 
                bullet[1] < 0 or bullet[1] > HEIGHT):
                self.bullets.remove(bullet)
    
    def draw(self, screen):

        pygame.draw.rect(screen, self.color, 
                         (self.x - self.size//2, self.y - self.size//2, 
                          self.size, self.size))
        

        health_bar_length = 20
        max_health = 60 if self.type == "tank" else 30
        health_ratio = self.health / max_health
        pygame.draw.rect(screen, RED, (self.x - health_bar_length//2, self.y - 25, 
                                      health_bar_length, 3))
        pygame.draw.rect(screen, GREEN, (self.x - health_bar_length//2, self.y - 25, 
                                        health_bar_length * health_ratio, 3))
        

        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW, 
                            (int(bullet[0]) - 2, int(bullet[1]) - 2, 4, 4))

player = Player()
enemies = []
wave = 1
score = 0
game_over = False
game_won = False
font = pygame.font.SysFont(None, 36)


def spawn_wave(wave_num):
    num_enemies = 3 + wave_num * 2
    for _ in range(num_enemies):
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(0, WIDTH)
            y = -30
        elif side == 1:
            x = WIDTH + 30
            y = random.randint(0, HEIGHT)
        elif side == 2:
            x = random.randint(0, WIDTH)
            y = HEIGHT + 30
        else:
            x = -30
            y = random.randint(0, HEIGHT)
        
        if wave_num == 1:
            enemy_type = "shooter"
        elif wave_num == 2:
            enemy_type = random.choice(["shooter", "rusher"])
        else:
            enemy_type = random.choice(["shooter", "rusher", "tank"])
        
        enemies.append(Enemy(x, y, enemy_type))

spawn_wave(wave)


clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not game_won:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                player.shoot(mouse_x, mouse_y)
    
    if not game_over and not game_won:
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()
        
        for enemy in enemies:
            enemy.move(player.x, player.y)
            enemy.shoot_at_player(player.x, player.y)
            enemy.update_bullets()
            

            if (abs(enemy.x - player.x) < (enemy.size//2 + player.size//2) and
                abs(enemy.y - player.y) < (enemy.size//2 + player.size//2)):
                player.health -= 2 if enemy.type == "rusher" else 1
                if player.health <= 0:
                    game_over = True
        
        for bullet in player.bullets[:]:
            for enemy in enemies[:]:
                if (abs(bullet[0] - enemy.x) < (2 + enemy.size//2) and
                    abs(bullet[1] - enemy.y) < (2 + enemy.size//2)):
                    enemy.health -= 10
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        score += 15 if enemy.type == "tank" else 10
                    break
        
        for enemy in enemies:
            for bullet in enemy.bullets[:]:
                if (abs(bullet[0] - player.x) < (2 + player.size//2) and
                    abs(bullet[1] - player.y) < (2 + player.size//2)):
                    player.health -= 5
                    enemy.bullets.remove(bullet)
                    if player.health <= 0:
                        game_over = True
        
        if len(enemies) == 0 and wave < 3:
            wave += 1
            spawn_wave(wave)
        elif len(enemies) == 0 and wave == 3:
            game_won = True
    
    screen.fill(WHITE)
    
    player.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    
    wave_text = font.render(f"Волна: {wave}/3", True, BLACK)
    score_text = font.render(f"Счет: {score}", True, BLACK)
    health_text = font.render(f"Здоровье: {player.health}", True, BLACK)
    screen.blit(wave_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(health_text, (10, 90))
    
    if game_over:
        game_over_text = font.render("lose", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2))
    
    if game_won:
        win_text = font.render("ezez", True, GREEN)
        screen.blit(win_text, (WIDTH//2 - 180, HEIGHT//2))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
