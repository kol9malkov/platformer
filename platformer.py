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
        self.jump_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

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
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
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
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = 'jump'
            elif self.jump_count == 2:
                sprite_sheet = 'double_jump'
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = 'fall'
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

    def collide_vertical(self, blocks):
        collide_blocks = []
        for block in blocks:
            if pygame.sprite.collide_mask(self, block):
                if self.y_vel > 0:
                    self.rect.bottom = block.rect.top
                    self.landed()
                if self.y_vel < 0:
                    self.rect.top = block.rect.bottom
                    self.hit_head()

                collide_blocks.append(block)
        return collide_blocks
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def draw(self):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, dir, filename, x, y, size):
        super().__init__()
        path = join("assets", dir, filename)
        self.rect = pygame.Rect(x, y, size, size)
        self.image = pygame.transform.scale(pygame.image.load(path), (size, size)).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Block(Object):
    pass

class Saw(Object):
    def __init__(self, dir, filename, x, y, size):
        super().__init__(dir, filename, x, y, size)
        self.speed = 3
        self.angle = 0
        self.original_image = self.image.copy()  # Сохраняем копию оригинального изображения

    def on(self, cell_size, n):
        if self.rect.x <= cell_size * n:
            self.side = "right"
        if self.rect.x >= screen_W - 128:
            self.side = "left"
        if self.side == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

    def animation(self):
        # Поворачиваем изображение пилы
        self.angle += 5  # Увеличиваем угол для вращения
        if self.angle >= 360:
            self.angle = 0  # Сбрасываем угол, если он станет больше или равен 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # Обновляем положение спрайта после поворота


# игровые переменные
player = Player(0, 0, 50, 50)

block_size = 64

lvl1 = []
blocks = pygame.sprite.Group()

block_x = 0
block_size = 64
blocks_bottom_amount = screen_W // block_size
for i in range(blocks_bottom_amount):
    block = Block('tiles', 'Grass.png', block_x, screen_H - block_size, block_size)
    blocks.add(block)
    block_x += block_size
block_x = 0

blocks.add(Block('tiles', 'Grass.png', block_x + block_size * 4, screen_H - block_size * 2, block_size))

# игровой цикл
run_game = True
while run_game:
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player.jump_count < 2:
                player.jump()

    # передвижение
    player.loop()
    # столкновение
    player.collide_vertical(blocks)
    # отрисовка
    player.draw()

    for line in range(screen_H//64+1):
        pygame.draw.line(screen, (255, 255, 255), (0, line * 64), (screen_W, line * 64), 2)
        for col in range(screen_W//64+1):
            pygame.draw.line(screen, (255, 255, 255), (col * 64, 0), (col * 64, screen_H), 2)

    for block in blocks:
        block.draw()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()