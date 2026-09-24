class Inventario:
    def verificar(self, producto):
        print(f"Verificando el stock de:  {producto}")
        return True

class Pago:
    def procesar(self, monto):
        print(f"Procesando pago:  {monto}")
        return True

class Envio:
    def crear_envio(self, producto):
        print(f'Preparando el envio del: {producto}')

class Notificacion():
    def crear_notificacion(self,producto):
        print(f'Se compro: {producto}')

class TiendaFacade:
    def __init__(self):
        self.inventario = Inventario()
        self.pago = Pago()
        self.envio = Envio()
        self.notificacion = Notificacion()

    def comprar(self, producto, precio):
        if not self.inventario.verificar(producto):
            print('no hay stock')
            return
        
        if not self.pago.procesar(precio):
            print('fallo el pago')
            return

        self.envio.crear_envio(producto)

        print("Compra completada")

        self.notificacion.crear_notificacion(producto)
    
def main():
    tienda = TiendaFacade()

    tienda.comprar('Laptop', 1500)


main()



###Hacer un sistema de notificacion que tenga la funcion de enviar 
#### y que llegue una notificacion luego del envio 