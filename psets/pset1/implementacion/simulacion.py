
from datetime import datetime, timedelta

from dominio import Estudiante, Capitan, Administrador, GestorReservas

AHORA = datetime(2026, 9, 7, 10, 0)  # lunes 7/9/2026 a las 10 am


def titulo(texto):
    print()
    print("--------------------------------------------------")
    print(texto)
    print("--------------------------------------------------")


gestor = GestorReservas()
admin = Administrador("Marta")
ana = Estudiante("Ana")
carla = Estudiante("Carla")
diego = Estudiante("Diego")
bruno = Capitan("Bruno", "Futbol Masculino")

print("Simulacion ReservaU - fecha de referencia:", AHORA.strftime("%d/%m/%Y %H:%M"))

# ==========================================================
titulo("CU-03 Gestionar canchas (flujo principal: agregar)")
# ==========================================================
for nombre, deporte in [("Futbol 1", "futbol"), ("Futbol 2", "futbol"), ("Tenis 1", "tenis")]:
    print("1. El administrador pide agregar la cancha", nombre)
    cancha = admin.agregar_cancha(gestor, nombre, deporte)
    print("2. El sistema registra la cancha como activa:", cancha)
    print("3. El sistema confirma la operacion")

# ==========================================================
titulo("CU-03 flujo alterno 2a: nombre duplicado")
# ==========================================================
print("1. El administrador pide agregar la cancha Futbol 1 otra vez")
try:
    admin.agregar_cancha(gestor, "Futbol 1", "futbol")
except ValueError as error:
    print("2a. El sistema rechaza el registro:", error)

futbol1 = gestor.buscar_cancha("Futbol 1")
futbol2 = gestor.buscar_cancha("Futbol 2")
tenis1 = gestor.buscar_cancha("Tenis 1")

# ==========================================================
titulo("CU-01 Reservar cancha (flujo principal)")
# ==========================================================
hora_20 = AHORA.replace(hour=20, minute=0)
print("1. Ana pide reservar Futbol 1 hoy a las 20:00")
print("2. El sistema revisa que la cancha este activa:", futbol1.activa)
print("3. El sistema revisa que el horario este libre:", futbol1.esta_disponible(hora_20))
reserva_ana = gestor.reservar(ana, futbol1, hora_20)
print("4. El sistema crea la reserva:", reserva_ana)
print("5. El sistema le confirma la reserva a Ana")

# ==========================================================
titulo("CU-01 flujo alterno 3b: dos solicitudes para el mismo horario ANTES de las 18:00")
# ==========================================================
hora_16 = AHORA.replace(hour=16, minute=0)
print("1. Ana pide Futbol 1 a las 16:00 (llega primero)")
s_ana = gestor.recibir_solicitud(ana, futbol1, hora_16)
print("1. Bruno (capitan) pide Futbol 1 a las 16:00 (llega despues)")
s_bruno = gestor.recibir_solicitud(bruno, futbol1, hora_16)
print("2. El sistema ve que hay dos solicitudes para el mismo horario")
print("3b. El sistema le pregunta a la regla de prioridad de cada uno:")
print("    Ana tiene prioridad para las 16:00?", ana.tiene_prioridad_para(hora_16))
print("    Bruno tiene prioridad para las 16:00?", bruno.tiene_prioridad_para(hora_16))
resultados = gestor.procesar_solicitudes()
for s in resultados:
    if s.estado == "aprobada":
        print("4. Gana el que tiene prioridad. Se crea:", s.reserva)
    else:
        print("4. La solicitud de", s.solicitante, "se rechaza:", s.motivo)
print("5. El sistema avisa el resultado a los dos")

# ==========================================================
titulo("CU-01 flujo alterno 3b: mismo caso pero DESPUES de las 18:00 (la prioridad ya no vale)")
# ==========================================================
hora_19 = AHORA.replace(hour=19, minute=0)
print("1. Carla pide Tenis 1 a las 19:00 (llega primero)")
s_carla = gestor.recibir_solicitud(carla, tenis1, hora_19)
print("1. Bruno pide Tenis 1 a las 19:00 (llega despues)")
s_bruno19 = gestor.recibir_solicitud(bruno, tenis1, hora_19)
print("2. El sistema ve que hay dos solicitudes para el mismo horario")
print("3b. El sistema le pregunta a la regla de prioridad de cada uno:")
print("    Carla tiene prioridad para las 19:00?", carla.tiene_prioridad_para(hora_19))
print("    Bruno tiene prioridad para las 19:00?", bruno.tiene_prioridad_para(hora_19))
resultados = gestor.procesar_solicitudes()
for s in resultados:
    if s.estado == "aprobada":
        print("4. Nadie tiene prioridad, gana el orden de llegada. Se crea:", s.reserva)
    else:
        print("4. La solicitud de", s.solicitante, "se rechaza:", s.motivo)
print("5. El sistema avisa el resultado a los dos")
reserva_carla = s_carla.reserva

# ==========================================================
titulo("CU-02 Cancelar reserva (flujo principal, con tiempo de sobra)")
# ==========================================================
momento = AHORA.replace(hour=10, minute=30)
print("1. Ana pide cancelar su reserva de las 20:00 (son las 10:30)")
print("2. El sistema revisa que la reserva sea de Ana:", reserva_ana.pertenece_a(ana))
faltan = reserva_ana.inicio - momento
print("3. El sistema calcula cuanto falta para el inicio:", faltan)
estado = gestor.cancelar_reserva(ana, reserva_ana, momento)
print("4. Falta mas de 2 horas, se registra como cancelacion normal:", estado)
print("5. El sistema le avisa a Ana")

# ==========================================================
titulo("CU-02 flujo alterno 2a: cancelar una reserva ajena")
# ==========================================================
print("1. Carla intenta cancelar la reserva de Bruno de las 16:00")
try:
    gestor.cancelar_reserva(carla, s_bruno.reserva, AHORA.replace(hour=11))
except ValueError as error:
    print("2a. El sistema rechaza la operacion:", error)

# ==========================================================
titulo("CU-02 flujo alterno 4a: cancelar con menos de 2 horas -> no-show")
# ==========================================================
momento = AHORA.replace(hour=17, minute=30)
print("1. Carla pide cancelar su reserva de las 19:00 (son las 17:30)")
print("2. El sistema revisa que la reserva sea de Carla:", reserva_carla.pertenece_a(carla))
faltan = reserva_carla.inicio - momento
print("3. El sistema calcula cuanto falta para el inicio:", faltan)
estado = gestor.cancelar_reserva(carla, reserva_carla, momento)
print("4a. Falta menos de 2 horas, el sistema lo registra como:", estado)
print("    (Carla no eligio esto, lo decide el sistema)")
print("5. El sistema le avisa a Carla")

# ==========================================================
titulo("CU-03 flujo alterno 1a: deshabilitar una cancha (y aparece un conflicto)")
# ==========================================================
manana_9 = AHORA.replace(hour=9) + timedelta(days=1)
reserva_diego = gestor.reservar(diego, futbol2, manana_9)
print("(antes: Diego tiene una", str(reserva_diego) + ")")
print("1a. El administrador pide deshabilitar Futbol 2 por mantenimiento")
cancha, conflictos = admin.deshabilitar_cancha(gestor, "Futbol 2", AHORA)
print("2. El sistema marca la cancha como inactiva:", cancha)
print("3. El sistema encuentra", len(conflictos), "reserva(s) futura(s) en conflicto y le avisa al admin")

print()
print("(de paso, CU-01 flujo alterno 2a: reservar una cancha deshabilitada)")
print("1. Diego intenta reservar Futbol 2 mañana a las 11:00")
try:
    gestor.reservar(diego, futbol2, manana_9.replace(hour=11))
except ValueError as error:
    print("2a. El sistema rechaza la solicitud:", error)

# ==========================================================
titulo("CU-04 Resolver conflicto (flujo principal: reubicar la reserva)")
# ==========================================================
conflicto = conflictos[0]
print("1. El administrador revisa el conflicto:", conflicto)
print("2. El administrador decide reubicar la reserva en Futbol 1")
print("3. El sistema revisa si Futbol 1 esta libre a esa hora:", futbol1.esta_disponible(conflicto.inicio))
admin.resolver_reubicando(conflicto, futbol1)
print("4. El sistema reubica la reserva:", conflicto)
print("5. El sistema le confirma al administrador")

# ==========================================================
titulo("CU-04 flujo alterno 2a: no hay cancha alternativa -> cancelacion administrativa")
# ==========================================================
tarde_15 = AHORA.replace(hour=15) + timedelta(days=1)
reserva_extra = gestor.reservar(carla, tenis1, tarde_15)
print("(antes: Carla tiene una", str(reserva_extra) + " y hay mantenimiento a esa hora)")
print("1. El administrador revisa el conflicto reportado")
print("2a. No hay otra cancha, decide cancelarla administrativamente")
estado = admin.resolver_cancelando(reserva_extra, "mantenimiento del complejo")
print("3. El sistema la registra como:", estado, "(motivo:", reserva_extra.motivo_admin + ")")
print("4. El sistema le avisa a Carla y confirma al administrador")

# ==========================================================
titulo("Resumen final")
# ==========================================================
print("Canchas:")
for c in gestor.canchas:
    print("  -", c)
print("Reservas:")
for r in gestor.reservas:
    print("  -", r)
print()
print("Simulacion completada sin errores")