import pygame

pygame.init()
# окно
screen_W, screen_H = 900, 700
background = pygame.transform.scale(pygame.image.load('Background.png'), (screen_W, screen_H))
screen = pygame.display.set_mode((screen_W, screen_H))
pygame.display.set_caption("Next lvl")

# игровой цикл
clock = pygame.time.Clock()
FPS = 60

run_game = True
while run_game:
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False

    pygame.display.update()
    clock.tick(FPS)
