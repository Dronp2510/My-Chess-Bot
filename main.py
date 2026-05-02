import pygame

pygame.init()


window = pygame.display.set_mode((500,500) , pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("My Chess")

run = True
colors = [pygame.Color('white') , pygame.Color('brown')]

def chess_board(surface):

    WIDTH , HEIGHT = surface.get_size()
    SQUARE_SIZE = min(WIDTH , HEIGHT) // 8
    for row in range(8):
        for column in range(8):
            color = colors[((row + column) % 2)]
            rect = pygame.Rect(column * SQUARE_SIZE , row * SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE)
            pygame.draw.rect(window , color , rect)


while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    window.fill((0 , 0 , 0))
    chess_board(window)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()