# Configuracion de reglas de ReservaU (patron SINGLETON).
# Tecnologia pidio que los valores de las reglas vivan en un unico lugar
# del sistema, para cambiarlos sin buscar numeros repartidos por el codigo.
# Por eso esta clase existe una sola vez: no importa cuantas veces se haga
# Configuracion(), siempre devuelve el mismo objeto.

from datetime import time, timedelta


class Configuracion:
    _instancia = None

    def __new__(cls):
        # si todavia no existe la unica instancia, se crea y se cargan
        # los valores. Si ya existe, se devuelve la misma de siempre.
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._cargar_valores()
        return cls._instancia

    def _cargar_valores(self):
        # regla de prioridad (PSet 1, RF-03)
        self.hora_limite_prioridad = time(18, 0)
        # ventanas de cancelacion (RF-05 modificado)
        self.ventana_no_show_estudiante = timedelta(hours=2)
        self.ventana_no_show_capitan = timedelta(hours=24)
        # suspension por no-shows (RF-11)
        self.limite_no_shows_mes = 3
        self.dias_suspension = 7
        # reserva recurrente (RF-09)
        self.semanas_minimas = 2
        self.semanas_maximas = 8
