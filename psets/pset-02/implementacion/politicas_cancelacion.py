# Politicas de cancelacion (patron STRATEGY).
# Coordinacion de Deportes cambio las reglas de cancelacion y ahora hay
# tres resultados distintos segun quien cancela:
#   - estudiante: no-show si cancela con menos de 2 horas
#   - capitan: no-show si cancela con menos de 24 horas
#   - administrador: nunca hay penalidad
# La Reserva NO pregunta quien la creo con un if: cada reserva sale de su
# fabrica con la politica ya puesta adentro, y al cancelar solo le
# pregunta a su politica cual es el resultado. Las ventanas de tiempo se
# leen de la Configuracion (singleton).

from abc import ABC, abstractmethod

from configuracion import Configuracion


class PoliticaCancelacion(ABC):
    @abstractmethod
    def resultado_al_cancelar(self, reserva, ahora):
        # devuelve el estado que le queda a la reserva
        pass

    def genera_penalidad(self, resultado):
        # un no-show cuenta para la suspension, lo demas no
        return resultado == "no-show"


class CancelacionEstudiante(PoliticaCancelacion):
    # regla del PSet 1: menos de 2 horas = no-show
    def resultado_al_cancelar(self, reserva, ahora):
        falta = reserva.inicio - ahora
        if falta < Configuracion().ventana_no_show_estudiante:
            return "no-show"
        return "cancelada"


class CancelacionCapitan(PoliticaCancelacion):
    # regla nueva: un capitan que cancela una reserva de su equipo con
    # menos de 24 horas deja vacia una franja muy pedida -> no-show
    def resultado_al_cancelar(self, reserva, ahora):
        falta = reserva.inicio - ahora
        if falta < Configuracion().ventana_no_show_capitan:
            return "no-show"
        return "cancelada"


class AnulacionAdministrativa(PoliticaCancelacion):
    # cuando el administrador anula (mantenimiento, conflicto o bloqueo)
    # nunca se registra penalidad para el solicitante
    def resultado_al_cancelar(self, reserva, ahora):
        return "cancelada por admin"

    def genera_penalidad(self, resultado):
        return False
