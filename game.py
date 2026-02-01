import torch
from random import randint

import os

import training
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame

pygame.init()
width, height = 1000, 1000
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("jogo")

background = pygame.transform.scale(pygame.image.load("Background.png"), (width, height))
font = pygame.font.SysFont("comicsans", 30)

player_speed = 5
player_width = 50
player_height = 50
square_size = 100

class Square:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, square_size, square_size)
        self.speed = speed

    def copy(self):
        new = Square(self.rect.x, self.rect.y, self.speed)
        new.rect = self.rect.copy()
        return new


def draw(player, squares, time):
    window.blit(background, (0, 0))
    pygame.draw.rect(window, (0, 0, 200), player)
    text_time = font.render(str(round(time)), 1, "white")
    window.blit(text_time, (10, 10))

    for q in squares:
        pygame.draw.rect(window, "blue", q.rect)
    pygame.display.update()

def generate_phase():
    res = []
    vertical_spaces = height // square_size
    horizontal_spaces = width // square_size
    for _ in range(15):
        square_side = randint(1, 4) #1: up 2: down 3: left 4: right
        match square_side:
            case 1:
                square = Square(randint(0,vertical_spaces)*square_size, 1, (0, 5))
            case 2:
                square = Square(randint(0,vertical_spaces)*square_size, height - square_size - 1, (0, -5))
            case 3:
                square = Square(1, randint(0,horizontal_spaces)*square_size, (5, 0))
            case 4:
                square = Square(width - square_size - 1, randint(0,horizontal_spaces)*square_size, (-5, 0))
        res.append(square)
    return res

def main(phases, bot=None):
    run = True
    hit = False
    player = pygame.Rect(width//2, height//2, player_width, player_height)

    clock = pygame.time.Clock()

    if bot is None:
        bot = training.Bot()
    global state_dict_backup
    state_dict_backup = bot.state_dict()
    squares = []
    phase_idx = 0
    frames = 0

    while run:
        clock.tick(3000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        state = [player.x, player.y]
        if len(squares) == 0:
            squares = [q.copy() for q in phases[phase_idx]]
            phase_idx = (phase_idx + 1) % len(phases)

        for q in squares[:]:
            q.rect.move_ip(q.speed)
            state.append(q.rect.x); state.append(q.rect.y)
            if player.colliderect(q.rect):
                hit = True
            if (q.rect.x >= width-square_size and q.speed[0] > 0 or 
                q.rect.x <= 0 and q.speed[0] < 0 or 
                q.rect.y >= height-square_size and q.speed[1] > 0 or 
                q.rect.y <= 0 and q.speed[1] < 0):
                squares.remove(q)
        
        if hit:
            return [frames, state_dict_backup]
        frames+=1

        draw(player, squares, frames)

        with torch.no_grad():
            result = bot(torch.tensor(state, dtype=torch.float32))

        match torch.argmax(result):
            case 0:
                if player.y - player_speed >= 0:
                    player.y -= player_speed
            case 1:
                if player.y - player_speed >= 0:
                    player.y -= player_speed
                if player.x + player_speed + player_width <= width:
                    player.x += player_speed
            case 2:
                if player.x + player_speed + player_width <= width:
                    player.x += player_speed
            case 3:
                if player.x + player_speed + player_width <= width:
                    player.x += player_speed
                if player.y + player_speed + player_height <= height:
                    player.y += player_speed
            case 4:
                if player.y + player_speed + player_height <= height:
                    player.y += player_speed
            case 5:
                if player.y + player_speed + player_height <= height:
                    player.y += player_speed
                if player.x - player_speed >= 0:
                    player.x -= player_speed
            case 6:
                if player.x - player_speed >= 0:
                    player.x -= player_speed
            case 7:
                if player.x - player_speed >= 0:
                    player.x -= player_speed
                if player.y - player_speed >= 0:
                    player.y -= player_speed

if __name__ == "__main__":
    main()

