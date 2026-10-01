from abc import ABC, abstractmethod
from personajesFactory import *

class MundoFactoryABC(ABC):
    @abstractmethod
    def crear_jugador(self):
        pass

    @abstractmethod
    def crear_enemigo(self):
        pass

class FantasyFactory(MundoFactoryABC):
    def crear_jugador(self):
        return PersonajeFactory.crear("guerrero")

    def crear_enemigo(self):
        return PersonajeFactory.crear("dragon")

class SciFiFactory(MundoFactoryABC):
    def crear_jugador(self):
        return PersonajeFactory.crear("soldado")

    def crear_enemigo(self):
            return PersonajeFactory.crear("alien")

def crearMundo(factory):
    jugador = factory.crear_jugador()
    enemigo = factory.crear_enemigo()
    jugador.mostrarPersonage()
    enemigo.mostrarPersonage()
    return jugador, enemigo

