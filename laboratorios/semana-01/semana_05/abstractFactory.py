from abc import ABC, abstractmethod

class Boton(ABC):
    @abstractmethod
    def renderizar(self):
        pass

class Menu(ABC):
    @abstractmethod
    def renderizar(self):
        pass

class CheckBox(ABC):
    @abstractmethod
    def renderizar(self):
        pass

class BotonWindows(Boton):
    def renderizar(self):
        print("Boton estilo windows")

class MenuWindows(Menu):
    def renderizar(self):
        print("Menu estilo windows")

class CheckBoxWindows(CheckBox):
    def renderizar(self):
        print("Checkbox estilo windows")

class BotonMac(Boton):
    def renderizar(self):
        print("Boton estilo mac")

class MenuMac(Menu):
    def renderizar(self):
        print("Menu estilo mac")

class CheckBoxMac(CheckBox):
    def renderizar(self):
        print("Checkbox estilo mac")

class UIFactoryABC(ABC):
    @abstractmethod
    def crear_boton(self):
        pass

    @abstractmethod
    def crear_menu(self):
        pass

    @abstractmethod
    def crear_checkbox(self):
        pass

class WindowsFactory(UIFactoryABC):
    def crear_boton(self):
        return BotonWindows()

    def crear_menu(self):
        return MenuWindows()

    def crear_checkbox(self):
        return CheckBoxWindows

class MacFactory(UIFactoryABC):
    def crear_boton(self):
        return BotonMac()

    def crear_menu(self):
        return MenuMac()

    def crear_checkbox(self):
        return CheckBoxMac

def crear_UI(factory):
    boton = factory.crear_boton()
    menu = factory.crear_menu()
    checkbox = factory.crear_checkbox()
    boton.renderizar()
    menu.renderizar()
    checkbox.renderizar()

def main():
    sistema = "Windows"  

    if sistema == "Windows":
        factory = WindowsFactory()
    elif sistema == "Mac":
        factory = MacFactory()

    crear_UI(factory)

if __name__ == "__main__":
    main()