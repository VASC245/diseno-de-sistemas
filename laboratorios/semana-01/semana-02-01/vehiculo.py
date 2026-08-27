##cREAR UN VEHICULO, QUE SE MUEVA, FUNCION MOVER, 

#AUTO -> MUEVE POR CARRETERA
#BOTE -> MUEVE POR AGUA 
#AVION -> MUEVE POR CIELO


class Vehiculo:
    def __init__(self, comportamiento_mover):
        self.comportamiento_mover = comportamiento_mover

    def mover(self):                      
        self.comportamiento_mover.mover()

class ComportamientoMover:
    def mover():
        raise NotImplementedError

class MoverCarretera:
    def mover(ComporatmientoMover):
        print("Conduciendo por carretera")

class MoverAgua:
    def mover(ComporatmientoMover):
        print("Navegando por el agua")

class MoverAire:
    def mover(ComporatmientoMover):
        print("Volando por aire")

class Auto(Vehiculo):
    def __init__(self):
        mover = MoverCarretera()
        super().__init__(mover)

class Bote(Vehiculo):
    def __init__(self):
        mover = MoverAgua()
        super().__init__(mover)

class Avion(Vehiculo):
    def __init__(self):
        mover = MoverAire()
        super().__init__(mover)

if __name__ == "__main__":
    auto1 = Auto()
    auto1.mover()

    bote1 = Bote()
    bote1.mover()

    avion1 = Avion()
    avion1.mover()