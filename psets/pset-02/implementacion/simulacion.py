# Simulacion de ReservaU v2 (PSet 2).
# Para operar sobre reservas, este archivo SOLO habla con la fachada:
# nunca llama directo a la cancha, al validador ni al notificador.
# Los prints siguen el orden de los flujos documentados y de los
# diagramas de secuencia y actividad.
# Se usa una fecha fija para que la salida sea siempre la misma.

import threading
from datetime import date, datetime, time, timedelta

from configuracion import Configuracion
from constructor_recurrente import ConstructorReservaRecurrente
from dominio import Bloqueo, Capitan, Estudiante
from fachada import FachadaReservaU
from sedes import FabricaCampusNorte, FabricaCampusSur

AHORA = datetime(2026, 10, 12, 10, 0)  # lunes 12/10/2026, 10:00 am


def titulo(texto):
    print()
    print("--------------------------------------------------------------")
    print(texto)
    print("--------------------------------------------------------------")


def intento_fallido(funcion):
    # ejecuta una operacion que sabemos que el sistema debe rechazar
    try:
        funcion()
        print("  ERROR: esto debia ser rechazado!")
    except ValueError as error:
        print("  -> el sistema la rechaza: " + str(error))


fachada = FachadaReservaU()
config = Configuracion()

print("Simulacion ReservaU v2 - fecha de referencia: "
      + AHORA.strftime("%A %d/%m/%Y %H:%M"))
print("(la configuracion es un singleton: Configuracion() is Configuracion() -> "
      + str(Configuracion() is Configuracion()) + ")")

# preparacion: sedes (abstract factory), canchas y personas
norte = fachada.crear_sede("Campus Norte", FabricaCampusNorte())
sur = fachada.crear_sede("Campus Sur", FabricaCampusSur())
futbol_n = fachada.agregar_cancha("Futbol Norte 1", "futbol", norte)
tenis_n = fachada.agregar_cancha("Tenis Norte 1", "tenis", norte)
futbol_s = fachada.agregar_cancha("Futbol Sur 1", "futbol", sur)
tenis_s = fachada.agregar_cancha("Tenis Sur 1", "tenis", sur)

ana = Estudiante("Ana")
carla = Estudiante("Carla")
diego = Estudiante("Diego")
bruno = Capitan("Bruno", "Futbol Masculino")

# ======================================================================
titulo("ESCENARIO 1 - una reserva en cada sede, validada y notificada "
       "en su sede")
# ======================================================================
hoy_20 = AHORA.replace(hour=20, minute=0)
reserva_ana = fachada.reservar(ana, futbol_n, hoy_20, AHORA)
print()
reserva_diego_sur = fachada.reservar(diego, futbol_s, hoy_20, AHORA)

# ======================================================================
titulo("ESCENARIO 2 - rechazo por horario fuera del permitido de SU sede")
# ======================================================================
manana_0630 = (AHORA + timedelta(days=1)).replace(hour=6, minute=30)
print("  (las 06:30 son validas en Campus Norte, pero Campus Sur abre 07:00)")
intento_fallido(lambda: fachada.reservar(carla, tenis_s, manana_0630, AHORA))

# ======================================================================
titulo("ESCENARIO 3a - reserva recurrente exitosa (builder + todo o nada)")
# ======================================================================
martes_16 = (AHORA + timedelta(days=1)).replace(hour=16, minute=0)
pedido_ok = (ConstructorReservaRecurrente(bruno, tenis_n, martes_16)
             .con_semanas(4)
             .con_equipo(["balones", "chalecos"])
             .con_notas("dejar la red armada")
             .construir())
reservas_bruno = fachada.reservar_recurrente(pedido_ok, AHORA)

# ======================================================================
titulo("ESCENARIO 3b - recurrente rechazada por conflicto (indica la semana)")
# ======================================================================
lunes_9 = (AHORA + timedelta(days=7)).replace(hour=9, minute=0)
print("  (contexto: Ana reserva " + futbol_n.nombre + " el "
      + (lunes_9 + timedelta(weeks=1)).strftime("%d/%m %H:%M")
      + ", que sera la semana 2 del pedido de Bruno)")
fachada.reservar(ana, futbol_n, lunes_9 + timedelta(weeks=1), AHORA,
                 con_pasos=False)
pedido_choca = (ConstructorReservaRecurrente(bruno, futbol_n, lunes_9)
                .con_semanas(3)
                .construir())
intento_fallido(lambda: fachada.reservar_recurrente(pedido_choca, AHORA))
activas_bruno_futbol = [r for r in fachada.reservas
                        if r.solicitante is bruno
                        and r.cancha is futbol_n and r.esta_activa()]
print("  (todo o nada: Bruno tiene " + str(len(activas_bruno_futbol))
      + " reservas registradas en " + futbol_n.nombre + ")")

# ======================================================================
titulo("ESCENARIO 4 - tres cancelaciones con resultados distintos "
       "(strategy de cancelacion)")
# ======================================================================
print("a) estudiante que cancela a tiempo (faltan mas de 2 horas):")
fachada.cancelar(ana, reserva_ana, AHORA.replace(hour=10, minute=30))

print()
print("b) capitan que cancela con menos de 24 horas (no-show):")
primera_de_bruno = reservas_bruno[0]  # martes 16:00, cancelada el lunes 20:00
fachada.cancelar(bruno, primera_de_bruno, AHORA.replace(hour=20, minute=0))

print()
print("c) anulacion del administrador (nunca hay penalidad):")
fachada.anular_por_admin(reserva_diego_sur, "mantenimiento de la cancha")
print("  (no-shows de Diego este mes: "
      + str(diego.no_shows_del_mes(AHORA)) + ")")

# ======================================================================
titulo("ESCENARIO 5 - un solicitante llega a 3 no-shows y queda suspendido")
# ======================================================================
print("  (contexto: Carla hace 3 reservas para hoy y las cancela todas "
      "con menos de 2 horas)")
r1 = fachada.reservar(carla, tenis_n, AHORA.replace(hour=12), AHORA, con_pasos=False)
r2 = fachada.reservar(carla, tenis_n, AHORA.replace(hour=13), AHORA, con_pasos=False)
r3 = fachada.reservar(carla, tenis_n, AHORA.replace(hour=14), AHORA, con_pasos=False)
print()
fachada.cancelar(carla, r1, AHORA.replace(hour=11, minute=0))
print()
fachada.cancelar(carla, r2, AHORA.replace(hour=12, minute=30))
print()
fachada.cancelar(carla, r3, AHORA.replace(hour=13, minute=30))
print()
print("  Carla intenta reservar de nuevo:")
intento_fallido(lambda: fachada.reservar(
    carla, tenis_n, (AHORA + timedelta(days=2)).replace(hour=15),
    AHORA.replace(hour=14, minute=0)))

# ======================================================================
titulo("ESCENARIO 6 - bloqueo definido una vez y clonado en dos canchas "
       "(prototype)")
# ======================================================================
sabado = (AHORA + timedelta(days=5)).replace(hour=10, minute=0)
print("  (contexto: Diego tiene una reserva el sabado a las 10:00 en "
      + futbol_n.nombre + ", dentro de la franja del bloqueo)")
fachada.reservar(diego, futbol_n, sabado, AHORA, con_pasos=False)
plantilla = Bloqueo("torneo interfacultades", time(9, 0), time(13, 0),
                    ["arcos", "vallas"])
print("  plantilla definida una sola vez: " + str(plantilla))
print()
print("  clon 1 (tiene una reserva existente que se anula):")
fachada.bloquear(plantilla, futbol_n, sabado.date())
print()
print("  clon 2 (sin reservas):")
clon2 = fachada.bloquear(plantilla, futbol_s, sabado.date() + timedelta(days=1))
print()
print("  prueba del prototype: al clon 2 se le agrega una 'tarima'")
clon2.equipo.append("tarima")
print("    equipo del clon 2:      " + str(clon2.equipo))
print("    equipo de la plantilla: " + str(plantilla.equipo)
      + "  (no cambio: por eso se usa deepcopy)")

# ======================================================================
titulo("ESCENARIO 7 - dos hilos piden la misma cancha y franja: "
       "solo uno confirma (lock pesimista)")
# ======================================================================
pablo = Estudiante("Pablo")
quique = Estudiante("Quique")
domingo_18 = (AHORA + timedelta(days=6)).replace(hour=18, minute=0)
resultados = {}
barrera = threading.Barrier(2)  # para que los dos arranquen a la vez


def intentar_reservar(persona):
    barrera.wait()  # los dos hilos llegan aqui y salen al mismo tiempo
    try:
        fachada.reservar(persona, tenis_s, domingo_18, AHORA, con_pasos=False)
        resultados[persona.nombre] = "CONFIRMADA"
    except ValueError as error:
        resultados[persona.nombre] = "rechazada (" + str(error) + ")"


hilo_a = threading.Thread(target=intentar_reservar, args=(pablo,))
hilo_b = threading.Thread(target=intentar_reservar, args=(quique,))
print("  los dos hilos verifican y registran sobre " + tenis_s.nombre
      + " el " + domingo_18.strftime("%d/%m %H:%M") + "...")
hilo_a.start()
hilo_b.start()
hilo_a.join()
hilo_b.join()

for nombre in sorted(resultados):
    print("  resultado de " + nombre + ": " + resultados[nombre])
confirmadas = [r for r in fachada.reservas
               if r.cancha is tenis_s and r.inicio == domingo_18
               and r.esta_activa()]
print("  reservas confirmadas para esa cancha y franja: "
      + str(len(confirmadas)) + " (exactamente una, RNF-06)")

# ======================================================================
titulo("RESUMEN FINAL")
# ======================================================================
print("Reservas en el sistema:")
for r in fachada.reservas:
    print("  - " + str(r))
print()
print("Simulacion completada sin errores")
