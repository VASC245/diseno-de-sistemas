from personajesFactory import *
from abc import ABC , abstractmethod

class estrategiaAtaque(ABC):
    @abstractmethod
    def ataque(self, ataque):
        pass


class ataqueNormal(estrategiaAtaque):
    def ataque(self, ataque):
        return ataque

class ataqueFuerte(estrategiaAtaque):
    def ataque(self, ataque):
        return ataque * 10

class ataque:
    def __init__(self, estrategiaAtaque):
        self.estrategiaAtaque = estrategiaAtaque

    def cambiarEstrategia(self, estrategiaAtaque):
        self.estrategiaAtaque = estrategiaAtaque

    def ataque(self, atacante, objetivo):
        danio = self.estrategiaAtaque.ataque(atacante.ataque)
        objetivo.vida = max(0, objetivo.vida - danio)
        return danio

