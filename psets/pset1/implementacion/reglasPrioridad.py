from abc import ABC, abstractmethod
from datetime import time
 
 
class ReglaPrioridad(ABC):
    # clase base, todas las reglas tienen que implementar este metodo
    @abstractmethod
    def tiene_prioridad(self, inicio):
        pass
 
 
class PrioridadEquipoOficial(ReglaPrioridad):
    # regla de los equipos oficiales: tienen prioridad para reservar
    # antes de las 6 pm. Despues de esa hora ya no aplica.
    def tiene_prioridad(self, inicio):
        return inicio.time() < time(18, 0)
 
 
class SinPrioridad(ReglaPrioridad):
    # regla de los estudiantes normales: nunca tienen prioridad
    def tiene_prioridad(self, inicio):
        return False
 