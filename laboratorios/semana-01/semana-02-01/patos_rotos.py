class Pato:

    def __init__(self, comportamiento_vuelo, comportamiento_graznar):
        self.comportamiento_vuelo = comportamiento_vuelo
        self.comportamiento_graznar = comportamiento_graznar

    def nadar(self):
        print("Nadando")

    def graznar(self):
        self.comportamiento_graznar.graznar()

    def volar(self):
        self.comportamiento_vuelo.volar()

class PatoSalvaje(Pato):
    def __init__(self):
        vuela_alas = VuelaConAlas()
        graznido_normal = GraznidoNormal()
        super().__init__(vuela_alas, graznido_normal)



class ComportamientoVuelo():
    def volar(self):
        raise NotImplementedError

class VuelaConAlas(ComportamientoVuelo):
    def volar(self):
        print("Volando con alas")

class NoVuela(ComportamientoVuelo):
    def volar(self):
        print("No puede volar")


class ComportamientoGraznar():
    def graznar(self):
        raise NotImplementedError

class GraznidoNormal(ComportamientoGraznar):
    def graznar(self):
        print("Cuac!!")

class GraznidoGoma(ComportamientoGraznar):
    def graznar(self):
        print("Chirrido de goma")

class PatoDeGoma(Pato):
    def __init__(self):
        no_vuela = NoVuela()
        graznido_goma = GraznidoGoma()
        super().__init__(no_vuela, graznido_goma)

    def graznar(self):
        print("Chirrido de Goma")

#    def volar(self): # Mala practica
 #       print("No vuela")


if __name__ == "__main__":
    salvaje = PatoSalvaje()
    salvaje.nadar()
    salvaje.volar()
    salvaje.graznar()
    salvaje.volar()

    print()

    goma = PatoDeGoma()
    goma.nadar()
    goma.graznar()
    goma.volar()