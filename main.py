import pygame
import random
from sys import exit

# Display Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 50
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT  # 350 px (ground floor level)
SPRITE_SIZE = (64, 64)


class Boi(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load spider sprite sheet (5 frames)
        raw_sheet = pygame.image.load("assets/spider.png").convert_alpha()
        
        sheet_width, sheet_height = raw_sheet.get_size()
        frame_width = sheet_width // 5

        self.frames = []
        for col in range(5):
            frame_rect = pygame.Rect(col * frame_width, 0, frame_width, sheet_height)
            frame_surf = raw_sheet.subsurface(frame_rect)
            self.frames.append(pygame.transform.scale(frame_surf, SPRITE_SIZE))

        self.frame_index = 0
        self.animation_speed = 0.15

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=(100, GROUND_Y))
        self.gravity = 0

        self.invulnerable = False
        self.hurt_timer = 0

        try:
            self.jump_sound = pygame.mixer.Sound("assets/jump.wav")
            self.jump_sound.set_volume(0.4)
        except pygame.error:
            self.jump_sound = None

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= GROUND_Y:
            self.gravity = -16
            if self.jump_sound:
                self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        current_frame = self.frames[int(self.frame_index)].copy()

        if self.invulnerable:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                current_frame.set_alpha(100)
            else:
                current_frame.set_alpha(255)
        else:
            current_frame.set_alpha(255)

        self.image = current_frame

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animate()

        if self.invulnerable and pygame.time.get_ticks() - self.hurt_timer > 1000:
            self.invulnerable = False


class Target(pygame.sprite.Sprite):
    def __init__(self, target_type):
        super().__init__()
        self.start_x = random.randint(850, 1100)
        self.start_y = random.randint(120, 260)
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.2

        if target_type == "ant":
            raw_img = pygame.image.load("assets/ant.png").convert_alpha()
            self.frames.append(pygame.transform.scale(raw_img, SPRITE_SIZE))
            self.start_y = GROUND_Y - 32
        elif target_type == "mosquito":
            raw_img = pygame.image.load("assets/mosquito.png").convert_alpha()
            self.frames.append(pygame.transform.scale(raw_img, SPRITE_SIZE))
        else:
            # Fly sprite sheet (1282x264 containing 4 frames)
            raw_sheet = pygame.image.load("assets/fly.png").convert_alpha()
            sheet_width, sheet_height = raw_sheet.get_size()
            frame_width = sheet_width / 4

            for col in range(4):
                frame_rect = pygame.Rect(int(col * frame_width), 0, int(frame_width), sheet_height)
                frame_surf = raw_sheet.subsurface(frame_rect)
                self.frames.append(pygame.transform.scale(frame_surf, SPRITE_SIZE))

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(self.start_x, self.start_y))

    def animate(self):
        if len(self.frames) > 1:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
        self.rect.x -= 6
        if self.rect.right < 0:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()
        self.start_x = random.randint(850, 1200)

        if obstacle_type == "spike1":
            raw_img = pygame.image.load("assets/spike.png").convert_alpha()
        elif obstacle_type == "spike2":
            raw_img = pygame.image.load("assets/spike2.png").convert_alpha()
        elif obstacle_type == "spike3":
            raw_img = pygame.image.load("assets/spike3.png").convert_alpha()
        else:
            raw_img = pygame.image.load("assets/mantis.png").convert_alpha()

        self.image = pygame.transform.scale(raw_img, SPRITE_SIZE)
        self.rect = self.image.get_rect(midbottom=(self.start_x, GROUND_Y))

    def update(self):
        self.rect.x -= 6
        if self.rect.right < 0:
            self.kill()


def check_collisions():
    global score
    if player_group.sprite:
        collided = pygame.sprite.spritecollide(player_group.sprite, target_group, True)
        if collided:
            score += len(collided)


def check_obstacle_collisions():
    global health
    player = player_group.sprite
    if player and not player.invulnerable:
        hit_obstacles = pygame.sprite.spritecollide(player, obstacle_group, False)
        if hit_obstacles:
            health -= 1
            player.invulnerable = True
            player.hurt_timer = pygame.time.get_ticks()


def display_hud():
    score_surf = HUD_FONT.render(f"Score: {score}", True, (255, 255, 255))
    health_surf = HUD_FONT.render(f"Health: {health}", True, (255, 80, 80) if health <= 3 else (255, 255, 255))
    
    screen.blit(score_surf, (30, 20))
    screen.blit(health_surf, (SCREEN_WIDTH - 140, 20))


# Setup display and clock (optional if u don't want your game to work)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Spider Cave Run")
clock = pygame.time.Clock()

# Load static 800x400 background
background = pygame.image.load("assets/background1.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load ground asset explicitly formatted to 100x50
ground_raw = pygame.image.load("assets/ground.png").convert_alpha()
ground = pygame.transform.scale(ground_raw, (100, GROUND_HEIGHT))

# Start/Win/Lose screens
play_btn = pygame.image.load("assets/play.png").convert_alpha()
play_rect = play_btn.get_rect(center=(400, 200))

win_img = pygame.image.load("assets/you_win.png").convert()
win_img = pygame.transform.scale(win_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
lose_img = pygame.image.load("assets/game_over.png").convert()
lose_img = pygame.transform.scale(lose_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

replay_btn = pygame.image.load("assets/replay.png").convert_alpha()
replay_rect = replay_btn.get_rect(center=(300, 300))
exit_btn = pygame.image.load("assets/exit.png").convert_alpha()
exit_rect = exit_btn.get_rect(center=(500, 300))

# Fonts
HUD_FONT = pygame.font.Font(None, 36)
INTRO_FONT = pygame.font.Font(None, 40)

# State Variables for no reason
game_screen = 0
score = 0
health = 5
ground_x = 0

# Spawners
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1600)

target_timer = pygame.USEREVENT + 2
pygame.time.set_timer(target_timer, 1200)

# Sprite groups
boi = Boi()
player_group = pygame.sprite.GroupSingle(boi)
target_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_screen == 0:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_screen = 1

        if game_screen == 1:
            if event.type == target_timer:
                target_type = random.choice(['ant', 'fly', 'mosquito'])
                target_group.add(Target(target_type))

            if event.type == obstacle_timer:
                obstacle_type = random.choice(['spike1', 'spike2', 'spike3', 'mantis'])
                obstacle_group.add(Obstacle(obstacle_type))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_screen == 0 and play_rect.collidepoint(event.pos):
                game_screen = 1
            elif game_screen in (2, 3):
                if replay_rect.collidepoint(event.pos):
                    score = 0
                    health = 5
                    target_group.empty()
                    obstacle_group.empty()
                    boi.rect.midbottom = (100, GROUND_Y)
                    game_screen = 1
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()

    if game_screen == 0:
        screen.blit(background, (0, 0))
        screen.blit(play_btn, play_rect)

        intro_surf = INTRO_FONT.render("Press SPACE or Click Play to Start", True, (255, 255, 255))
        intro_rect = intro_surf.get_rect(center=(400, 280))
        screen.blit(intro_surf, intro_rect)

    elif game_screen == 1:
        # Background render
        screen.blit(background, (0, 0))

        # Horizontal shifting ground (optional)
        ground_x = (ground_x - 6) % ground.get_width()
        for x in range(-100, SCREEN_WIDTH + 100, ground.get_width()):
            screen.blit(ground, (x + ground_x, GROUND_Y))

        # Unknown objects that I decided to add
        target_group.draw(screen)
        target_group.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        player_group.update()
        player_group.draw(screen)

        check_collisions()
        check_obstacle_collisions()
        display_hud()

        if health <= 0:
            game_screen = 3
        elif score >= 15:
            game_screen = 2

    elif game_screen == 2:
        screen.blit(win_img, (0, 0))
        screen.blit(replay_btn, replay_rect)
        screen.blit(exit_btn, exit_rect)

    else:
        screen.blit(lose_img, (0, 0))
        screen.blit(replay_btn, replay_rect)
        screen.blit(exit_btn, exit_rect)

    pygame.display.update()
    clock.tick(60)