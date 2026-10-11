# Reglas de prioridad para las reservas (patron STRATEGY).
# Viene del PSet 1: el comportamiento que cambia (tener prioridad o no)
# va en su propia clase y cada solicitante tiene una regla adentro,
# sin usar ifs. En el PSet 2 lo unico que cambia es que la hora limite
# ya no esta escrita aqui: se lee de la Configuracion (singleton).

from abc import ABC, abstractmethod

from configuracion import Configuracion


class ReglaPrioridad(ABC):
    # estrategia abstracta: todas las reglas implementan este metodo
    @abstractmethod
    def tiene_prioridad(self, inicio):
        pass


class PrioridadEquipoOficial(ReglaPrioridad):
    # regla de los equipos oficiales: tienen prioridad para reservar
    # antes de la hora limite (18:00 segun la configuracion)
    def tiene_prioridad(self, inicio):
        return inicio.time() < Configuracion().hora_limite_prioridad


class SinPrioridad(ReglaPrioridad):
    # regla de los estudiantes normales: nunca tienen prioridad
    def tiene_prioridad(self, inicio):
        return False
