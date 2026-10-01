class Personaje:
    def __init__(self, nombre, ataque, vida):
        self.nombre = nombre
        self.ataque = ataque
        self.vida = vida


class Guerrero(Personaje):
    def mostrarPersonage(self):
        return f"Personaje: {self.nombre} "


class Dragon(Personaje):
    def mostrarPersonage(self):
        return f"Personaje: {self.nombre}"


class Soldado(Personaje):
    def mostrarPersonage(self):
        return f"Personaje: {self.nombre}"


class Alien(Personaje):
    def mostrarPersonage(self):
        return f"Personaje: {self.nombre}"


class CreadorDePersonaje:
    def crear_personaje(self):
        raise NotImplementedError


class CreadorDeGuerrero(CreadorDePersonaje):
    def crear_personaje(self):
        return Guerrero("Guerrero", 15, 100)


class CreadorDeDragon(CreadorDePersonaje):
    def crear_personaje(self):
        return Dragon("Dragón", 12, 120)


class CreadorDeSoldado(CreadorDePersonaje):
    def crear_personaje(self):
        return Soldado("Soldado", 17, 90)


class CreadorDeAlien(CreadorDePersonaje):
    def crear_personaje(self):
        return Alien("Alien", 11, 110)


class PersonajeFactory:
    @staticmethod
    def elegir_creador(tipo):
        tipo = tipo.lower()
        if tipo == "guerrero":
            return CreadorDeGuerrero()
        elif tipo == "dragon":
            return CreadorDeDragon()
        elif tipo == "soldado":
            return CreadorDeSoldado()
        elif tipo == "alien":
            return CreadorDeAlien()
        raise ValueError("Tipo de personaje desconocido: " + tipo)

    @staticmethod
    def crear(tipo):
        creador = PersonajeFactory.elegir_creador(tipo)
        return creador.crear_personaje()