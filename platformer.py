import pygame
from os import listdir
from os.path import isfile, join, exists

pygame.init()
# окно
screen_W, screen_H = 900, 700
background = pygame.transform.scale(
    pygame.image.load("Background.png"), (screen_W, screen_H)
)
screen = pygame.display.set_mode((screen_W, screen_H))
pygame.display.set_caption("Next lvl")
# игровой таймер
clock = pygame.time.Clock()
FPS = 60


# Загрузка изображений
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir, width, height, direction=False):
    path = join("assets", dir)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


""" КЛАССЫ """
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("character", 32, 32, True) # спрайт героя
    PLAYER_VEL = 5
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0  # скорость по x
        self.y_vel = 0  # скорость по y
        self.direction = "right" # Направление по умолчанию
        self.fall_count = 0
        self.animation_count = 0
        self.mask = None

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self):
        # self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.hotkeys()

        self.fall_count += 1

        self.update_animation()

    def hotkeys(self):
        keys = pygame.key.get_pressed()
        self.x_vel = 0
        if keys[pygame.K_a]:
            self.move_left(self.PLAYER_VEL)
        if keys[pygame.K_d]:
            self.move_right(self.PLAYER_VEL)

    def update_animation(self):
        sprite_sheet = "idle"
        if self.x_vel != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update_mask()

    def update_mask(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

# игровые переменные
player = Player(100, 100, 50, 50)

# игровой цикл
run_game = True
while run_game:
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False

    # передвижение
    player.loop()
    # отрисовка
    player.draw()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()