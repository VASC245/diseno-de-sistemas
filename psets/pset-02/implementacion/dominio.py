# Clases del dominio de ReservaU (PSet 2).
# Igual que en el PSet 1, cada regla vive en la clase que tiene la
# informacion para aplicarla:
#   - Reserva conoce su inicio y su politica -> ella sabe cancelarse
#   - Estudiante conoce sus no-shows -> el sabe si esta suspendido
#   - Cancha conoce sus reservas y bloqueos -> ella sabe su disponibilidad
#   - Bloqueo se define una vez y se clona (patron PROTOTYPE)

import copy
from datetime import timedelta

from configuracion import Configuracion
from politicas_cancelacion import AnulacionAdministrativa
from reglas_prioridad import PrioridadEquipoOficial, SinPrioridad


# ---------------------------------------------------------------------
# solicitantes (ahora llevan la cuenta de sus no-shows, RF-11)
# ---------------------------------------------------------------------

class Estudiante:
    def __init__(self, nombre):
        self.nombre = nombre
        # strategy de prioridad del PSet 1
        self.regla_prioridad = SinPrioridad()
        self.no_shows = []            # fechas de cada no-show
        self.suspendido_hasta = None  # None = no esta suspendido

    def tiene_prioridad_para(self, inicio):
        return self.regla_prioridad.tiene_prioridad(inicio)

    def no_shows_del_mes(self, fecha):
        # cuenta los no-shows del mismo mes calendario
        cuenta = 0
        for f in self.no_shows:
            if f.year == fecha.year and f.month == fecha.month:
                cuenta = cuenta + 1
        return cuenta

    def registrar_no_show(self, fecha):
        # el solicitante es quien sabe cuantos no-shows lleva este mes,
        # por eso el mismo aplica su suspension (RF-11). Los valores
        # (limite 3 y 7 dias) se leen de la configuracion.
        self.no_shows.append(fecha)
        config = Configuracion()
        if self.no_shows_del_mes(fecha) >= config.limite_no_shows_mes:
            self.suspendido_hasta = fecha + timedelta(days=config.dias_suspension)
            return True  # quedo suspendido
        return False

    def esta_suspendido(self, fecha):
        if self.suspendido_hasta is None:
            return False
        return fecha < self.suspendido_hasta

    def __str__(self):
        return self.nombre


class Capitan(Estudiante):
    # el capitan hace lo mismo que un estudiante (herencia, RF-02)
    # pero con la regla de prioridad de equipo oficial
    def __init__(self, nombre, equipo):
        super().__init__(nombre)
        self.equipo = equipo
        self.regla_prioridad = PrioridadEquipoOficial()

    def __str__(self):
        return self.nombre + " (capitan de " + self.equipo + ")"


# ---------------------------------------------------------------------
# cancha (ahora pertenece a una sede y conoce sus bloqueos)
# ---------------------------------------------------------------------

class Cancha:
    def __init__(self, nombre, deporte, sede):
        self.nombre = nombre
        self.deporte = deporte
        self.sede = sede
        self.activa = True
        self.reservas = []
        self.bloqueos = []

    def esta_disponible(self, inicio):
        if not self.activa:
            return False
        for b in self.bloqueos:
            if b.cubre(inicio):
                return False
        for r in self.reservas:
            if r.esta_activa() and r.inicio == inicio:
                return False
        return True

    def reservas_activas_en(self, bloqueo):
        # reservas que caen dentro de la franja de un bloqueo
        afectadas = []
        for r in self.reservas:
            if r.esta_activa() and bloqueo.cubre(r.inicio):
                afectadas.append(r)
        return afectadas

    def __str__(self):
        return self.nombre + " (" + str(self.sede) + ")"


# ---------------------------------------------------------------------
# reserva y su maquina de estados
# estados: confirmada -> cancelada / no-show / cancelada por admin
# los tres estados de la derecha son finales: de ahi ya no se sale
# ---------------------------------------------------------------------

class Reserva:
    def __init__(self, solicitante, cancha, inicio, politica_cancelacion):
        self.solicitante = solicitante
        self.cancha = cancha
        self.inicio = inicio
        # la politica llega desde la fabrica que creo la reserva:
        # la reserva nunca pregunta "quien me creo?" para cancelarse
        self.politica_cancelacion = politica_cancelacion
        self.estado = "confirmada"
        self.motivo_admin = None
        cancha.reservas.append(self)

    def esta_activa(self):
        return self.estado == "confirmada"

    def pertenece_a(self, persona):
        return self.solicitante is persona

    def cancelar(self, persona, ahora):
        # RF-04: solo el dueño puede cancelar
        if not self.pertenece_a(persona):
            raise ValueError("la reserva no pertenece a " + persona.nombre)
        if not self.esta_activa():
            raise ValueError("la reserva ya esta en un estado final: " + self.estado)
        # la politica (strategy) decide el resultado, no un if por tipo
        self.estado = self.politica_cancelacion.resultado_al_cancelar(self, ahora)
        return self.estado

    def anular_por_admin(self, motivo):
        # evento de la maquina de estados: anular (sin penalidad)
        if not self.esta_activa():
            raise ValueError("la reserva ya esta en un estado final: " + self.estado)
        politica = AnulacionAdministrativa()
        self.estado = politica.resultado_al_cancelar(self, None)
        self.motivo_admin = motivo
        return self.estado

    def tipo(self):
        return "regular"

    def __str__(self):
        return ("reserva " + self.tipo() + " de " + str(self.solicitante)
                + " en " + self.cancha.nombre + " el "
                + self.inicio.strftime("%d/%m %H:%M")
                + " [" + self.estado + "]")


class ReservaRegular(Reserva):
    # la que crea un estudiante (sale con CancelacionEstudiante)
    def tipo(self):
        return "regular"


class ReservaEquipoOficial(Reserva):
    # la que crea un capitan (sale con CancelacionCapitan)
    def tipo(self):
        return "de equipo oficial"


# ---------------------------------------------------------------------
# bloqueo (patron PROTOTYPE)
# ---------------------------------------------------------------------

class Bloqueo:
    # el administrador lo define UNA vez como plantilla (motivo, franja
    # horaria y equipo que debe montarse) y lo clona para cada cancha y
    # fecha, cambiando solo esas dos cosas.
    def __init__(self, motivo, hora_inicio, hora_fin, equipo):
        self.motivo = motivo
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.equipo = equipo      # lista: balones, vallas, tarima...
        self.cancha = None        # la plantilla no tiene cancha ni fecha
        self.fecha = None

    def clonar(self, cancha, fecha):
        # deepcopy y no copy.copy: el equipo es una LISTA. Con una copia
        # superficial el clon y la plantilla compartirian la misma lista,
        # y agregarle algo al clon tambien se lo agregaria a la plantilla.
        clon = copy.deepcopy(self)
        clon.cancha = cancha
        clon.fecha = fecha
        return clon

    def cubre(self, inicio):
        # un bloqueo cubre un horario si es el mismo dia y la hora cae
        # dentro de su franja
        if self.fecha is None:
            return False
        if inicio.date() != self.fecha:
            return False
        return self.hora_inicio <= inicio.time() < self.hora_fin

    def __str__(self):
        base = ("bloqueo '" + self.motivo + "' de "
                + self.hora_inicio.strftime("%H:%M") + " a "
                + self.hora_fin.strftime("%H:%M")
                + " con equipo " + str(self.equipo))
        if self.cancha is None:
            return base + " (plantilla)"
        return base + " en " + self.cancha.nombre + " el " + self.fecha.strftime("%d/%m")
