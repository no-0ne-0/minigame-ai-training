import game
import multiprocessing
import torch
from torch import nn
import pygame


class Bot(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(32, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 9)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)

def mutate(statedict, lr=0.7):
    new_bot = Bot()
    new_bot.load_state_dict(statedict)
    for param in new_bot.parameters():
        if torch.rand(1) < lr:
            param.data += lr * torch.randn_like(param)
    return new_bot


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    fases = [game.generate_phase() for _ in range(10)]

    with multiprocessing.Pool(processes=16) as pool:
        resultados = sorted(pool.starmap(game.main, [(fases[:], None)] * 800), key=lambda x: x[0])
    print(resultados[-1][0], resultados[-2][0])

    new_gen = [mutate(resultados[-1][1], lr=0), mutate(resultados[-2][1], lr=0)] + [mutate(resultados[-1][1]) for _ in range(199)] + [mutate(resultados[-2][1]) for _ in range(199)]

    for epoch in range(60):
        with multiprocessing.Pool(processes=16) as pool:
            resultados = sorted(pool.starmap(game.main, [(fases[:], bot) for bot in new_gen]), key=lambda x: x[0])
        print(resultados[-1][0], resultados[-2][0])

        new_gen = [mutate(resultados[-1][1], lr=0), mutate(resultados[-2][1], lr=0)] + [mutate(resultados[-1][1]) for _ in range(199)] + [mutate(resultados[-2][1]) for _ in range(199)]
        