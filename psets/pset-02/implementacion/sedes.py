# Sedes de ReservaU (patron ABSTRACT FACTORY).
# La universidad abrio una segunda sede y cada una tiene su propia FAMILIA
# de objetos que se usan juntos: su validador de horario y su notificador.
# Hay una fabrica por sede, y la Sede le pide a su fabrica los dos objetos
# al mismo tiempo. Asi es imposible que desde afuera se combine el
# validador de una sede con el notificador de la otra: nadie arma las
# piezas a mano, siempre salen juntas de la misma fabrica.

from abc import ABC, abstractmethod
from datetime import time


# ----- los productos: validador de horario y notificador -----

class ValidadorHorario:
    def __init__(self, abre, cierra):
        self.abre = abre
        self.cierra = cierra

    def horario_permitido(self, inicio):
        return self.abre <= inicio.time() < self.cierra

    def __str__(self):
        return self.abre.strftime("%H:%M") + " a " + self.cierra.strftime("%H:%M")


class Notificador(ABC):
    @abstractmethod
    def notificar(self, persona, mensaje):
        pass


class NotificadorCorreo(Notificador):
    # canal de Campus Norte
    def notificar(self, persona, mensaje):
        print("      [correo institucional para " + str(persona) + "] " + mensaje)


class NotificadorSMS(Notificador):
    # canal de Campus Sur
    def notificar(self, persona, mensaje):
        print("      [mensaje de texto para " + str(persona) + "] " + mensaje)


# ----- las fabricas: una por sede -----

class FabricaSede(ABC):
    @abstractmethod
    def crear_validador(self):
        pass

    @abstractmethod
    def crear_notificador(self):
        pass


class FabricaCampusNorte(FabricaSede):
    # familia de Campus Norte: 06:00 a 22:00 + correo institucional
    def crear_validador(self):
        return ValidadorHorario(time(6, 0), time(22, 0))

    def crear_notificador(self):
        return NotificadorCorreo()


class FabricaCampusSur(FabricaSede):
    # familia de Campus Sur: 07:00 a 23:00 + mensaje de texto
    def crear_validador(self):
        return ValidadorHorario(time(7, 0), time(23, 0))

    def crear_notificador(self):
        return NotificadorSMS()


# ----- la sede: recibe su fabrica y saca de ahi sus dos objetos -----

class Sede:
    def __init__(self, nombre, fabrica):
        self.nombre = nombre
        # los dos productos salen de la MISMA fabrica, siempre en pareja
        self.validador = fabrica.crear_validador()
        self.notificador = fabrica.crear_notificador()

    def __str__(self):
        return self.nombre
