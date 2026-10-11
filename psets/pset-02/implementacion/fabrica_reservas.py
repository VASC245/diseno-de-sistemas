# Creadores de reservas (patron FACTORY METHOD).
# El tipo de reserva depende de quien la solicita: un estudiante crea una
# reserva regular y un capitan una reserva de equipo oficial. La decision
# de que clase instanciar vive en UN solo lugar (creador_para, abajo), y
# cada reserva sale de su creador con la politica de cancelacion ya
# asignada. Asi ni la Reserva ni la fachada tienen ifs preguntando quien
# es el solicitante cada vez que hay que cancelar.

from abc import ABC, abstractmethod

from dominio import Capitan, ReservaEquipoOficial, ReservaRegular
from politicas_cancelacion import CancelacionCapitan, CancelacionEstudiante


class CreadorReserva(ABC):
    # el metodo fabrica: cada creador concreto decide que clase
    # instanciar y con que politica sale
    @abstractmethod
    def crear(self, solicitante, cancha, inicio):
        pass


class CreadorReservaRegular(CreadorReserva):
    def crear(self, solicitante, cancha, inicio):
        return ReservaRegular(solicitante, cancha, inicio,
                              CancelacionEstudiante())


class CreadorReservaEquipoOficial(CreadorReserva):
    def crear(self, solicitante, cancha, inicio):
        return ReservaEquipoOficial(solicitante, cancha, inicio,
                                    CancelacionCapitan())


def creador_para(solicitante):
    # ESTE es el unico lugar del sistema donde se decide que clase de
    # reserva se instancia. Si mañana aparece otro tipo de solicitante,
    # se agrega un creador aqui y el resto del codigo no cambia.
    if isinstance(solicitante, Capitan):
        return CreadorReservaEquipoOficial()
    return CreadorReservaRegular()
