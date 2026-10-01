class GameConfig:
    __config_unica = None

    def __new__(cls):
        if cls.__config_unica is None:
            nueva = super().__new__(cls)
            nueva.dificultad = "normal"
            nueva.numero_maximo_turnos = 20
            nueva.multiplicadores = {
                "facil": 0.8,
                "normal": 1.0,
                "dificil": 1.3,
            }
            cls.__config_unica = nueva
        return cls.__config_unica

    def factor_dificultad(self):
        return self.multiplicadores[self.dificultad]