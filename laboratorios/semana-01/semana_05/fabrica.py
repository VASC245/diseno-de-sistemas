class Estudiante:
    def __init__(self, nombre):
        self.nombre = nombre

class EquipoOficial:
    def __init__(self, nombre):
        self.nombre = nombre

class ReservaRegular:
    def __init__(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante

    def confirmar(self):
        return "Reserva confirmada para " + self.solicitante.nombre

class ReservaPrioridad:
    def __init__(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante

    def confirmar(self):
            return "Reserva de prioridad confirmada para " + self.solicitante.nombre

def reserva_desde_web(cancha, fecha, hora_inicio, hora_fin, solicitante):
    creador = FabricaDeReservas.elegir_creador(solicitante)
    
class CreadordeReserva():
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        raise NotImplementedError

class CreadordeReservaRegular():
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaRegular(
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            solicitante
        )

class CreadordeReservaPrioridad():
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaPrioridad(
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            solicitante
        )

class FabricaDeReservas():
    @staticmethod
    def elegir_creador(solicitante):
        if isinstance(solicitante, Estudiante):
            return CreadordeReservaRegular()
        elif isinstance(solicitante, EquipoOficial):
            return CreadordeReservaPrioridad()
    
def main():
    reserva_desde_web(
        'Cancha de futbol',
        '2026-09-'

    )

if __name__ == "__main__":
    main()

