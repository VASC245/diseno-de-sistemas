
from datetime import timedelta

from reglasPrioridad import PrioridadEquipoOficial, SinPrioridad


class Estudiante:
    # estudiante normal, puede reservar y cancelar sus reservas
    def __init__(self, nombre):
        self.nombre = nombre
        # los estudiantes normales no tienen prioridad nunca
        self.regla_prioridad = SinPrioridad()

    def tiene_prioridad_para(self, inicio):
        # no decide con un if, le pregunta a su regla (strategy)
        return self.regla_prioridad.tiene_prioridad(inicio)

    def __str__(self):
        return self.nombre


class Capitan(Estudiante):
    # el capitan puede hacer lo mismo que un estudiante 
    # pero su regla de prioridad es la de equipo oficial
    def __init__(self, nombre, equipo):
        super().__init__(nombre)
        self.equipo = equipo
        self.regla_prioridad = PrioridadEquipoOficial()

    def __str__(self):
        return self.nombre + " (capitan de " + self.equipo + ")"


class Cancha:
    def __init__(self, nombre, deporte):
        self.nombre = nombre
        self.deporte = deporte
        self.activa = True
        self.reservas = []

    def esta_disponible(self, inicio):
        # no esta disponible si esta deshabilitada o si ya hay una
        # reserva confirmada a esa misma hora
        if not self.activa:
            return False
        for r in self.reservas:
            if r.estado == "confirmada" and r.inicio == inicio:
                return False
        return True

    def deshabilitar(self):
        self.activa = False

    def reservas_futuras(self, ahora):
        # sirve para saber que reservas quedan en conflicto si se
        # deshabilita la cancha
        futuras = []
        for r in self.reservas:
            if r.estado == "confirmada" and r.inicio > ahora:
                futuras.append(r)
        return futuras

    def __str__(self):
        if self.activa:
            return self.nombre + " (" + self.deporte + ", activa)"
        return self.nombre + " (" + self.deporte + ", deshabilitada)"


class Reserva:
    # estados posibles: confirmada, cancelada, no-show, cancelada por admin
    LIMITE_NO_SHOW = timedelta(hours=2)

    def __init__(self, solicitante, cancha, inicio):
        self.solicitante = solicitante
        self.cancha = cancha
        self.inicio = inicio
        self.estado = "confirmada"
        self.motivo_admin = None
        cancha.reservas.append(self)

    def pertenece_a(self, persona):
        return self.solicitante is persona

    def cancelar(self, persona, ahora):
        # regla: solo el dueño puede cancelar su reserva
        if not self.pertenece_a(persona):
            raise ValueError("la reserva no pertenece a " + persona.nombre)
        if self.estado != "confirmada":
            raise ValueError("la reserva ya no esta activa")

        # regla de las 2 horas: si falta menos de 2 horas para el inicio
        # el sistema la registra como no-show. El usuario no decide esto.
        tiempo_restante = self.inicio - ahora
        if tiempo_restante < Reserva.LIMITE_NO_SHOW:
            self.estado = "no-show"
        else:
            self.estado = "cancelada"
        return self.estado

    def cancelar_por_admin(self, motivo):
        # cancelacion administrativa cuando el admin resuelve un conflicto
        self.estado = "cancelada por admin"
        self.motivo_admin = motivo
        return self.estado

    def reubicar(self, nueva_cancha):
        # mover la reserva a otra cancha (tambien para resolver conflictos)
        if not nueva_cancha.esta_disponible(self.inicio):
            raise ValueError(nueva_cancha.nombre + " no esta disponible a esa hora")
        self.cancha.reservas.remove(self)
        self.cancha = nueva_cancha
        nueva_cancha.reservas.append(self)

    def __str__(self):
        return ("reserva de " + str(self.solicitante) + " en "
                + self.cancha.nombre + " el "
                + self.inicio.strftime("%d/%m %H:%M")
                + " [" + self.estado + "]")


class SolicitudReserva:
    # cuando varias personas quieren el mismo horario, primero se guardan
    # las solicitudes y despues el gestor decide quien gana
    def __init__(self, solicitante, cancha, inicio, orden):
        self.solicitante = solicitante
        self.cancha = cancha
        self.inicio = inicio
        self.orden = orden  # orden de llegada
        self.estado = "pendiente"
        self.reserva = None
        self.motivo = None


class Administrador:
    # el admin gestiona las canchas y resuelve conflictos, no reserva
    def __init__(self, nombre):
        self.nombre = nombre

    def agregar_cancha(self, gestor, nombre, deporte):
        return gestor.agregar_cancha(nombre, deporte)

    def deshabilitar_cancha(self, gestor, nombre, ahora):
        return gestor.deshabilitar_cancha(nombre, ahora)

    def resolver_reubicando(self, reserva, nueva_cancha):
        reserva.reubicar(nueva_cancha)

    def resolver_cancelando(self, reserva, motivo):
        return reserva.cancelar_por_admin(motivo)

    def __str__(self):
        return self.nombre


class GestorReservas:
    # junta todo: canchas, reservas y solicitudes
    def __init__(self):
        self.canchas = []
        self.reservas = []
        self.solicitudes = []
        self.contador = 0

    def agregar_cancha(self, nombre, deporte):
        if self.buscar_cancha(nombre) is not None:
            raise ValueError("ya existe una cancha llamada " + nombre)
        cancha = Cancha(nombre, deporte)
        self.canchas.append(cancha)
        return cancha

    def buscar_cancha(self, nombre):
        for c in self.canchas:
            if c.nombre == nombre:
                return c
        return None

    def deshabilitar_cancha(self, nombre, ahora):
        cancha = self.buscar_cancha(nombre)
        if cancha is None:
            raise ValueError("no existe la cancha " + nombre)
        cancha.deshabilitar()
        # devuelve las reservas que quedaron en conflicto para que el
        # admin las resuelva
        return cancha, cancha.reservas_futuras(ahora)

    def reservar(self, solicitante, cancha, inicio):
        if not cancha.activa:
            raise ValueError("la cancha " + cancha.nombre + " esta deshabilitada")
        if not cancha.esta_disponible(inicio):
            raise ValueError("la cancha " + cancha.nombre + " ya esta ocupada a esa hora")
        reserva = Reserva(solicitante, cancha, inicio)
        self.reservas.append(reserva)
        return reserva

    def recibir_solicitud(self, solicitante, cancha, inicio):
        self.contador = self.contador + 1
        s = SolicitudReserva(solicitante, cancha, inicio, self.contador)
        self.solicitudes.append(s)
        return s

    def procesar_solicitudes(self):
        # aca se aplica la prioridad se atiende primero a los que SI
        # tienen prioridad para ese horario (segun su regla) y despues
        # por orden de llegada. No hay ningun "if es capitan".
        pendientes = self.solicitudes
        self.solicitudes = []

        def clave(s):
            if s.solicitante.tiene_prioridad_para(s.inicio):
                return (0, s.orden)
            return (1, s.orden)

        pendientes.sort(key=clave)

        for s in pendientes:
            try:
                s.reserva = self.reservar(s.solicitante, s.cancha, s.inicio)
                s.estado = "aprobada"
            except ValueError as error:
                s.estado = "rechazada"
                s.motivo = str(error)
        return pendientes

    def cancelar_reserva(self, persona, reserva, ahora):
        # la reserva es la que sabe cancelarse (conoce su dueño y su hora)
        return reserva.cancelar(persona, ahora)