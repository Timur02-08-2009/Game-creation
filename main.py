import pygame
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


        # sprite_sheet = pygame.image.load("img/123.png").convert_alpha()
        
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
        self.rect = self.image.get_rect(midbottom=(100, 230))

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


# Setup display and clock
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("GW Game")
clock = pygame.time.Clock()

# Load assets (ensure file paths match your folder structure)
sky = pygame.image.load("assets/sky1.jpg").convert()
ground1 = pygame.image.load("assets/ground2.png").convert()
ground2 = pygame.image.load("assets/ground2.png").convert()

# Instantiate player and group
boi = Boi()
player_group = pygame.sprite.GroupSingle()
player_group.add(boi)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Show background
    screen.blit(sky, (0, 0))
    screen.blit(ground1, (0, 330))
    screen.blit(ground2, (400, 330))

    # Update and draw player
    player_group.update()
    player_group.draw(screen)

    pygame.display.update()
    clock.tick(60)