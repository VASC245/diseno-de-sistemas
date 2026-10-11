# Constructor de la reserva recurrente (patron BUILDER).
# La reserva recurrente tiene datos obligatorios (cancha, fecha de inicio,
# franja y solicitante) y opcionales (numero de semanas, equipo prestado y
# notas para el conserje). Con el builder los obligatorios van en el
# constructor y los opcionales se agregan solo si hacen falta, en vez de
# un __init__ con un monton de parametros que casi siempre van vacios.

from configuracion import Configuracion


class PedidoRecurrente:
    # el objeto que el builder termina armando. La fachada lo procesa
    # con la regla de todo o nada (RF-10).
    def __init__(self, solicitante, cancha, inicio, semanas, equipo, notas):
        self.solicitante = solicitante
        self.cancha = cancha
        self.inicio = inicio          # primera semana (fecha + franja)
        self.semanas = semanas
        self.equipo = equipo
        self.notas = notas

    def __str__(self):
        texto = ("pedido recurrente de " + str(self.solicitante) + ": "
                 + self.cancha.nombre + ", "
                 + self.inicio.strftime("%A %d/%m %H:%M") + ", "
                 + str(self.semanas) + " semanas")
        if self.equipo:
            texto = texto + ", equipo: " + str(self.equipo)
        if self.notas:
            texto = texto + ", notas: '" + self.notas + "'"
        return texto


class ConstructorReservaRecurrente:
    def __init__(self, solicitante, cancha, inicio):
        # obligatorios
        self.solicitante = solicitante
        self.cancha = cancha
        self.inicio = inicio
        # opcionales con sus valores por defecto
        self.semanas = Configuracion().semanas_minimas
        self.equipo = []
        self.notas = ""

    def con_semanas(self, n):
        config = Configuracion()
        if n < config.semanas_minimas or n > config.semanas_maximas:
            raise ValueError("las semanas deben estar entre "
                             + str(config.semanas_minimas) + " y "
                             + str(config.semanas_maximas))
        self.semanas = n
        return self  # devolver self permite encadenar las llamadas

    def con_equipo(self, lista):
        self.equipo = lista
        return self

    def con_notas(self, texto):
        self.notas = texto
        return self

    def construir(self):
        return PedidoRecurrente(self.solicitante, self.cancha, self.inicio,
                                self.semanas, self.equipo, self.notas)
