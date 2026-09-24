from abc import ABC, abstractmethod

class EstrategiaDescuento(ABC):
    @abstractmethod
    def aplicar(self, precio_base):
        pass 

class SinDescuento(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base

class DescuentoVip(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.80

class DescuentoEstudiante(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.95

class DescuentoEmpleado(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.75

class Compra:
    def __init__(self, estrategiaDescuento):
        self.estrategiaDescuento = estrategiaDescuento

    def calcularTotal(self, precio):
       return self.estrategiaDescuento.aplicar(precio)

def main():

    sin_descuento = SinDescuento()
    vip_descuentp = DescuentoVip()
    estud_descuento = DescuentoEstudiante()
    empleado_descuento = DescuentoEmpleado()


    compra1 = Compra(sin_descuento)
    print(compra1.calcularTotal(100))

    compra2 = Compra(vip_descuentp)
    print(compra2.calcularTotal(200))

    compra3 = Compra(estud_descuento)
    print(compra3.calcularTotal(1000))

    compra4 = Compra(empleado_descuento)
    print(compra4.calcularTotal(10))


main()