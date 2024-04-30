import pygame

pygame.init()
# окно
screen_W, screen_H = 900, 700
background = pygame.transform.scale(pygame.image.load('Background.png'), (screen_W, screen_H))
screen = pygame.display.set_mode((screen_W, screen_H))
pygame.display.set_caption("Next lvl")
# игровой таймер
clock = pygame.time.Clock()
FPS = 60

''' КЛАССЫ '''
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.fill((255, 0, 0))

        self.x_vel = 5 # скорость по x
        self.y_vel = 0 # скорость по y
        self.fall_count = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.x_vel
        if keys[pygame.K_d]:
            self.rect.x += self.x_vel

        # гравитация
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.rect.y += self.y_vel
        self.fall_count += 1


    def draw(self):
        screen.blit(self.surface, (self.rect.x, self.rect.y))


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
    player.move()
    # отрисовка
    player.draw()

    pygame.display.update()
    clock.tick(FPS)
