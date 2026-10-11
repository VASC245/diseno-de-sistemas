# Fachada de ReservaU (patron FACADE) + proteccion de concurrencia.
#
# Reservar, reservar de forma recurrente, cancelar y bloquear coordinan
# varios subsistemas: la suspension del solicitante, el validador de
# horario de la sede, la disponibilidad de la cancha, la fabrica de
# reservas, el registro de no-shows y el notificador. La fachada expone
# esas cuatro operaciones y simulacion.py SOLO habla con ella, nunca con
# un subsistema directamente.
#
# Concurrencia: elegimos locking PESIMISTA con un threading.Lock, pero
# solo alrededor de la seccion critica de "verificar disponibilidad y
# registrar la reserva". Las consultas de disponibilidad sueltas no pasan
# por el candado, asi que las muchas lecturas no se frenan entre si; el
# costo del lock lo pagan solo las escrituras, que son pocas, y en los
# picos del inicio de semestre garantiza que dos solicitudes simultaneas
# por la misma cancha y franja produzcan exactamente UNA confirmada.

import threading
from datetime import timedelta

from dominio import Cancha
from fabrica_reservas import creador_para
from sedes import Sede


class FachadaReservaU:
    def __init__(self):
        self.sedes = []
        self.canchas = []
        self.reservas = []
        # el candado que protege la seccion critica (RNF-06)
        self.candado = threading.Lock()

    # ----- preparacion del sistema -----

    def crear_sede(self, nombre, fabrica):
        sede = Sede(nombre, fabrica)
        self.sedes.append(sede)
        return sede

    def agregar_cancha(self, nombre, deporte, sede):
        for c in self.canchas:
            if c.nombre == nombre:
                raise ValueError("ya existe una cancha llamada " + nombre)
        cancha = Cancha(nombre, deporte, sede)
        self.canchas.append(cancha)
        return cancha

    # ----- operacion 1: reservar una cancha -----

    def reservar(self, solicitante, cancha, inicio, ahora, con_pasos=True):
        def paso(n, texto):
            if con_pasos:
                print("  " + n + ". " + texto)

        paso("1", str(solicitante) + " pide reservar " + str(cancha)
             + " el " + inicio.strftime("%d/%m a las %H:%M"))

        # paso 2: el solicitante sabe si esta suspendido (RF-11)
        if solicitante.esta_suspendido(ahora):
            raise ValueError(solicitante.nombre + " esta suspendido hasta el "
                             + solicitante.suspendido_hasta.strftime("%d/%m"))
        paso("2", "el sistema verifica que no este suspendido: ok")

        # paso 3: el horario se valida con el validador de SU sede (RF-14)
        if not cancha.sede.validador.horario_permitido(inicio):
            raise ValueError("fuera del horario permitido de "
                             + str(cancha.sede) + " ("
                             + str(cancha.sede.validador) + ")")
        paso("3", "el validador de " + str(cancha.sede)
             + " acepta el horario (" + str(cancha.sede.validador) + ")")

        # paso 4: SECCION CRITICA. Verificar y registrar van juntos dentro
        # del candado: asi nadie mas puede ver la cancha libre y
        # registrarse entre nuestra verificacion y nuestro registro.
        with self.candado:
            if not cancha.esta_disponible(inicio):
                raise ValueError("la cancha " + cancha.nombre
                                 + " no esta disponible a esa hora")
            # la fabrica decide que clase de reserva crear (factory method)
            reserva = creador_para(solicitante).crear(solicitante, cancha, inicio)
            self.reservas.append(reserva)
        paso("4", "dentro del candado: disponible, se crea la " + str(reserva))

        # paso 5: se notifica por el canal de SU sede (abstract factory)
        paso("5", "el sistema notifica por el canal de " + str(cancha.sede) + ":")
        if con_pasos:
            cancha.sede.notificador.notificar(
                solicitante, "reserva confirmada en " + cancha.nombre
                + " el " + inicio.strftime("%d/%m a las %H:%M"))
        return reserva

    # ----- operacion 2: reservar de forma recurrente (todo o nada) -----

    def reservar_recurrente(self, pedido, ahora):
        print("  1. llega el " + str(pedido))

        if pedido.solicitante.esta_suspendido(ahora):
            raise ValueError(pedido.solicitante.nombre + " esta suspendido")
        print("  2. el sistema verifica que no este suspendido: ok")

        if not pedido.cancha.sede.validador.horario_permitido(pedido.inicio):
            raise ValueError("fuera del horario permitido de "
                             + str(pedido.cancha.sede))
        print("  3. el validador de " + str(pedido.cancha.sede)
              + " acepta la franja")

        with self.candado:
            # primera pasada: verificar semana por semana SIN registrar
            print("  4. verificacion semana por semana (todo o nada):")
            horarios = []
            for i in range(pedido.semanas):
                inicio = pedido.inicio + timedelta(weeks=i)
                libre = pedido.cancha.esta_disponible(inicio)
                print("     semana " + str(i + 1) + " ("
                      + inicio.strftime("%d/%m %H:%M") + "): "
                      + ("libre" if libre else "OCUPADA"))
                if not libre:
                    # regla de todo o nada: no se registra NINGUNA
                    raise ValueError("conflicto en la semana " + str(i + 1)
                                     + " (" + inicio.strftime("%d/%m") + "): "
                                     + "no se registra ninguna reserva")
                horarios.append(inicio)
            # segunda pasada: todas libres, recien ahora se registran
            creador = creador_para(pedido.solicitante)
            creadas = []
            for inicio in horarios:
                reserva = creador.crear(pedido.solicitante, pedido.cancha, inicio)
                self.reservas.append(reserva)
                creadas.append(reserva)
        print("  5. las " + str(len(creadas)) + " semanas estaban libres: "
              + "se registran todas las reservas")

        mensaje = (str(len(creadas)) + " reservas confirmadas en "
                   + pedido.cancha.nombre)
        if pedido.equipo:
            mensaje = mensaje + ", equipo prestado: " + str(pedido.equipo)
        if pedido.notas:
            mensaje = mensaje + ", notas para el conserje: '" + pedido.notas + "'"
        print("  6. el sistema notifica por el canal de "
              + str(pedido.cancha.sede) + ":")
        pedido.cancha.sede.notificador.notificar(pedido.solicitante, mensaje)
        return creadas

    # ----- operacion 3: cancelar una reserva -----

    def cancelar(self, persona, reserva, ahora):
        print("  1. " + str(persona) + " pide cancelar su "
              + str(reserva) + " (son las " + ahora.strftime("%d/%m %H:%M") + ")")
        falta = reserva.inicio - ahora
        print("  2. faltan " + str(falta) + " para el inicio")

        # la reserva delega en su politica de cancelacion (strategy):
        # aqui NADIE pregunta si quien cancela es estudiante o capitan
        resultado = reserva.cancelar(persona, ahora)
        print("  3. la politica de la reserva decide el resultado: " + resultado)

        if reserva.politica_cancelacion.genera_penalidad(resultado):
            quedo_suspendido = reserva.solicitante.registrar_no_show(ahora)
            print("  4. se registra el no-show: " + str(persona) + " lleva "
                  + str(reserva.solicitante.no_shows_del_mes(ahora))
                  + " en el mes")
            if quedo_suspendido:
                print("     llego al limite: queda suspendido hasta el "
                      + reserva.solicitante.suspendido_hasta.strftime("%d/%m"))
        else:
            print("  4. sin penalidad: no se registra no-show")

        print("  5. el sistema notifica por el canal de "
              + str(reserva.cancha.sede) + ":")
        reserva.cancha.sede.notificador.notificar(
            reserva.solicitante, "tu reserva del "
            + reserva.inicio.strftime("%d/%m %H:%M") + " quedo como: " + resultado)
        return resultado

    def anular_por_admin(self, reserva, motivo):
        print("  1. el administrador anula la " + str(reserva)
              + " (motivo: " + motivo + ")")
        resultado = reserva.anular_por_admin(motivo)
        print("  2. resultado: " + resultado + ", sin penalidad para "
              + str(reserva.solicitante))
        print("  3. el sistema notifica por el canal de "
              + str(reserva.cancha.sede) + ":")
        reserva.cancha.sede.notificador.notificar(
            reserva.solicitante, "tu reserva del "
            + reserva.inicio.strftime("%d/%m %H:%M")
            + " fue anulada por administracion (" + motivo + ")")
        return resultado

    # ----- operacion 4: bloquear una cancha (usa el prototype) -----

    def bloquear(self, plantilla, cancha, fecha):
        print("  1. se clona la plantilla para " + cancha.nombre
              + " el " + fecha.strftime("%d/%m"))
        bloqueo = plantilla.clonar(cancha, fecha)
        with self.candado:
            cancha.bloqueos.append(bloqueo)
            afectadas = cancha.reservas_activas_en(bloqueo)
        print("  2. se aplica el " + str(bloqueo))
        if afectadas:
            print("  3. hay " + str(len(afectadas))
                  + " reserva(s) en esa franja: se anulan y se notifica")
            for r in afectadas:
                self.anular_por_admin(r, "bloqueo: " + bloqueo.motivo)
        else:
            print("  3. no habia reservas en esa franja")
        return bloqueo
