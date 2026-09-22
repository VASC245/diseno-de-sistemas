import copy

class Computadora:
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.disco = None
        self.gpu = None
        self.wifi = None


    def mostrar(self):
        print('CPU ', self.cpu)
        print('RAM ', self.ram)
        print('DISCO ', self.disco)
        print('GPU', self.gpu)
        print('WIFI', self.wifi)

    def clonar(self):
        return copy.deepcopy(self)

class computadoraBuilder:
    def __init__(self):
        self.computadora = Computadora()

    def addCPU(self, cpu):
        self.computadora.cpu = cpu
        return self

    def addRAM(self, ram):
        self.computadora.ram = ram
        return self

    def addDISCO(self, disco):
        self.computadora.disco = disco
        return self

    def addGPU(self, gpu):
        self.computadora.gpu = gpu
        return self

    def addWIFI(self, wifi):
        self.computadora.wifi = wifi
        return self

    def build(self):
        return self.computadora

def main():
    pc_builder = computadoraBuilder()
    #Aqui sucede algo


    pc_builder = pc_builder.addRAM(4).addGPU(18).addWIFI(1)

    pc_gaming = pc_builder.addDISCO(1).addCPU(20).build()

    pc_gaming.mostrar()

    pc_work = pc_gaming.clonar()

    pc_work.ram = 64

    pc_work.mostrar()
main()