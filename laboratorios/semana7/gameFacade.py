from gameConfigSingleton import GameConfig
from mundosAbstractFactory import FantasyFactory, SciFiFactory
from ataqueStrategy import ataque, ataqueNormal, ataqueFuerte


class GameFacade:
    def __init__(self):
        self.config = GameConfig()
        self.mundo = None
        self.jugador = None
        self.enemigo = None
        self.ataque = ataque(ataqueNormal())
        self.turno = 0

    def jugar(self):
        print("===== COMBATE POR TURNOS =====")
        print("Dificultad:", self.config.dificultad,
              "| Maximo de turnos:", self.config.numero_maximo_turnos)
        self.crear_mundo()
        self.crear_personajes()
        self.ejecutar_turnos()
        self.determinar_ganador()

    # 1. Crear el mundo (Abstract Factory)
    def crear_mundo(self):
        opcion = self.pedir_opcion(
            "\nElige un mundo:\n"
            "  1) Fantasia (Guerrero vs Dragon)\n"
            "  2) Ciencia ficcion (Soldado vs Alien)\n"
            "Opcion: ",
            "1"
        )
        if opcion == "1":
            self.mundo = FantasyFactory()
            print("Mundo seleccionado: Fantasia")
        else:
            self.mundo = SciFiFactory()
            print("Mundo seleccionado: Ciencia ficcion")

    # 2. Crear jugador y enemigo (Abstract Factory + Factory)
    def crear_personajes(self):
        self.jugador = self.mundo.crear_jugador()
        self.enemigo = self.mundo.crear_enemigo()
        print()
        print(self.jugador.mostrarPersonage())
        print(self.enemigo.mostrarPersonage())

    # 3. Ejecutar los turnos (usa el limite del Singleton)
    def ejecutar_turnos(self):
        while (self.jugador.vida > 0 and self.enemigo.vida > 0
               and self.turno < self.config.numero_maximo_turnos):
            self.turno += 1
            print("\n----- Turno", self.turno, "-----")
            self.aplicar_estrategia()
            if self.enemigo.vida > 0:
                self.enemigo_responde()
            print(self.jugador.nombre, "vida:", self.jugador.vida,
                  "|", self.enemigo.nombre, "vida:", self.enemigo.vida)

    # 4. Aplicar la estrategia de ataque (Strategy)
    def aplicar_estrategia(self):
        if self.turno % 2 == 1:
            por_defecto = "1"
        else:
            por_defecto = "2"
        opcion = self.pedir_opcion("Estrategia: 1) Ataque normal  2) Ataque fuerte\nOpcion: ", por_defecto)
        if opcion == "1":
            self.ataque.cambiarEstrategia(ataqueNormal())
            nombre_ataque = "Ataque normal"
        else:
            self.ataque.cambiarEstrategia(ataqueFuerte())
            nombre_ataque = "Ataque fuerte"

        danio = self.ataque.ataque(self.jugador, self.enemigo)
        print(self.jugador.nombre, "usa", nombre_ataque, "y causa", danio, "de danio")

    def enemigo_responde(self):
        danio = round(self.enemigo.ataque * self.config.factor_dificultad())
        self.jugador.vida = max(0, self.jugador.vida - danio)
        print(self.enemigo.nombre, "responde y causa", danio, "de danio")

    # 5. Determinar quien gana
    def determinar_ganador(self):
        print("\n===== RESULTADO =====")
        if self.enemigo.vida == 0:
            print(self.jugador.nombre, "gana!")
        elif self.jugador.vida == 0:
            print(self.enemigo.nombre, "gana. Game over.")
        elif self.jugador.vida > self.enemigo.vida:
            print("Se acabaron los turnos.", self.jugador.nombre, "gana por tener mas vida.")
        elif self.enemigo.vida > self.jugador.vida:
            print("Se acabaron los turnos.", self.enemigo.nombre, "gana por tener mas vida.")
        else:
            print("Se acabaron los turnos. Empate.")

    # Lee la opcion del teclado; si no hay teclado (docker run sin -it) usa la opcion por defecto
    def pedir_opcion(self, mensaje, por_defecto):
        while True:
            try:
                opcion = input(mensaje).strip()
            except EOFError:
                print(por_defecto, "(automatico)")
                return por_defecto
            if opcion in ("1", "2"):
                return opcion
            print("Opcion invalida, escribe 1 o 2.")