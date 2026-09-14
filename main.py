import pygame
import random
from sys import exit


class Boi(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/123.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=(100, 360))
        self.gravity = 0

        # Sound setup
        self.jump_sound = pygame.mixer.Sound("assets/jump.wav")
        self.jump_sound.set_volume(0.5)

        # Calculate individual frame size based on grid dimensions
        sheet_width, sheet_height = self.image.get_size()
        frame_width = sheet_width // 4   # 4 columns
        frame_height = sheet_height // 2  # 2 rows

        # Extract all 8 frames in order (row by row)
        self.frames = []
        for row in range(2):
            for col in range(4):
                x = col * frame_width
                y = row * frame_height
                frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                frame = self.image.subsurface(frame_rect)
                self.frames.append(frame)

        # Animation variables
        self.frame_index = 0
        self.animation_speed = 0.15  # Adjust to speed up/slow down

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=(100, 360))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 360:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 360:
            self.rect.bottom = 360

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animate()


class Target(pygame.sprite.Sprite):
    def __init__(self, target_type):
        super().__init__()
        self.start = random.randint(800, 1000)

        if target_type == "apple":
            self.image = pygame.image.load("assets/apple.png").convert_alpha()
        elif target_type == "broccoli":
            self.image = pygame.image.load("assets/broccoli.png").convert_alpha()
        else:
            self.image = pygame.image.load("assets/carrot.png").convert_alpha()

        self.rect = self.image.get_rect(center=(self.start, 200))

    def update(self):
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()
        self.start = random.randint(800, 2000)

        if obstacle_type == "donut":
            self.image = pygame.image.load("assets/donut.png").convert_alpha()
        elif obstacle_type == "ice_cream":
            self.image = pygame.image.load("assets/ice_cream.png").convert_alpha()
        elif obstacle_type == "fries":
            self.image = pygame.image.load("assets/fries.png").convert_alpha()
        elif obstacle_type == "soda":
            self.image = pygame.image.load("assets/soda.png").convert_alpha()
        else:
            self.image = pygame.image.load("assets/cookie.png").convert_alpha()

        self.rect = self.image.get_rect(midbottom=(self.start, 360))

    def update(self):
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()


def check_collisions():
    """Player collects a target -> score goes up."""
    global score
    if player_group.sprite:
        collided_targets = pygame.sprite.spritecollide(player_group.sprite, target_group, True)
        if collided_targets:
            score += 1


def check_obstacle_collisions():
    """Player hits an obstacle -> health goes down."""
    global health
    if player_group.sprite:
        hit_obstacles = pygame.sprite.spritecollide(player_group.sprite, obstacle_group, True)
        if hit_obstacles:
            health -= 1


def display_score():
    score_surf = score_font.render("Score:" + str(score), True, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(100, 50))
    screen.blit(score_surf, score_rect)


def display_health():
    health_surf = health_font.render("Health:" + str(health), True, (255, 255, 255))
    health_rect = health_surf.get_rect(center=(650, 50))
    screen.blit(health_surf, health_rect)


# Setup display and clock
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

# Load background assets
sky = pygame.image.load("assets/sky1.jpg").convert()
ground1 = pygame.image.load("assets/ground2.png").convert()
ground2 = pygame.image.load("assets/ground2.png").convert()

# Start screen
start_screen = pygame.image.load("assets/start_screen.png").convert()
play_btn = pygame.image.load("assets/play.png").convert_alpha()
play_rect = play_btn.get_rect(center=(400, 350))

# Win / lose screens
win = pygame.image.load("assets/you_win.png").convert()
lose = pygame.image.load("assets/game_over.png").convert()
replay_btn = pygame.image.load("assets/replay.png").convert_alpha()
replay_rect = replay_btn.get_rect(center=(250, 300))
exit_btn = pygame.image.load("assets/exit.png").convert_alpha()
exit_rect = exit_btn.get_rect(center=(500, 300))

# Fonts
start_font = pygame.font.Font(None, 50)
score_font = pygame.font.Font(None, 30)
health_font = pygame.font.Font(None, 30)

# Initialize variables
game_screen = 0
score = 0
health = 10

# Player
boi = Boi()
player_group = pygame.sprite.GroupSingle()
player_group.add(boi)

# Targets and obstacles
target_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Start button
                if play_rect.collidepoint(event.pos):
                    game_screen = 1
                # Replay button (resets score/health and restarts)
                if replay_rect.collidepoint(event.pos):
                    score = 0
                    health = 10
                    target_group.empty()
                    obstacle_group.empty()
                    game_screen = 1
                # Exit button
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()

    if game_screen == 0:
        # Start screen
        screen.blit(start_screen, (0, 0))
        screen.blit(play_btn, play_rect)

    elif game_screen == 1:
        # Background
        screen.blit(sky, (0, 0))
        screen.blit(ground1, (0, 330))
        screen.blit(ground2, (400, 330))

        # Targets
        target_group.draw(screen)
        target_group.update()
        if not target_group:
            target_type = random.choice(['apple', 'broccoli', 'carrot'])
            target_group.add(Target(target_type))

        # Obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()
        if not obstacle_group:
            obstacle_type = random.choice(['cookie', 'fries', 'ice_cream', 'soda', 'donut'])
            obstacle_group.add(Obstacle(obstacle_type))

        # Player
        player_group.update()
        player_group.draw(screen)

        # Score / health
        check_collisions()
        check_obstacle_collisions()
        display_score()
        display_health()

        # Check win / lose conditions
        if health <= 0:
            game_screen = 3
        if score >= 3:
            game_screen = 2

    elif game_screen == 2:
        # Win screen
        screen.blit(win, (0, 0))
        screen.blit(replay_btn, replay_rect)
        screen.blit(exit_btn, exit_rect)

    else:
        # Lose screen (game_screen == 3)
        screen.blit(lose, (0, 0))
        screen.blit(replay_btn, replay_rect)
        screen.blit(exit_btn, exit_rect)

    pygame.display.update()
    clock.tick(60)