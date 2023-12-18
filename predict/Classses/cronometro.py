
from time import time


class Cronometro:
    def __init__(self):
        self.reset()

    def reset(self):
        self._tempo_inicial = time()

    def tempo_passado(self):
        return time() - self._tempo_inicial
