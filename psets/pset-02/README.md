# PSet 2 - ReservaU con patrones de diseño

Extiende el PSet 1 con los pedidos de Coordinacion de Deportes
(stakeholder 3) y Direccion de Tecnologia (stakeholder 4).

## Que hay en la carpeta

- `requerimientos.pdf` - requerimientos nuevos y modificados (sigue la numeracion del PSet 1)
- `modelo-de-dominio.pdf` - diagrama de clases actualizado
- `casos-de-uso.pdf` - diagrama de casos de uso + flujos de los casos nuevos o modificados
- `robustez.pdf` - robustez de "Cancelar una reserva" (reglas ICONIX)
- `secuencia.pdf` - secuencia de "Reservar una cancha" con la fachada y los tres alt de rechazo
- `actividad.pdf` - actividad de "Reservar de forma recurrente" (todo o nada)
- `maquina-estados.pdf` - estados de Reserva con eventos, guardas y estados finales
- `implementacion/` - el codigo y el Dockerfile

## Como correrlo

Local:

```
cd implementacion
python3 simulacion.py
```

Con Docker:

```
cd implementacion
docker build -t reservau-v2 .
docker run reservau-v2
```

## Tabla de patrones

| Patron | Requerimiento que lo justifica | Problema que resuelve | Clases y metodos |
|---|---|---|---|
| Strategy (prioridad) | RF-03 (PSet 1) | Sin el, cada solicitante decidiria su prioridad con un `if es_capitan` repetido en cada lugar donde se compite por un horario. | `ReglaPrioridad`, `PrioridadEquipoOficial`, `SinPrioridad` (reglas_prioridad.py), compuestas en `Estudiante.regla_prioridad` |
| Strategy (cancelacion) | RF-05 mod. y RF-07 mod. | Sin el, `Reserva.cancelar()` tendria un `if` preguntando quien la creo (estudiante, capitan o admin) para elegir la ventana y la penalidad, y agregar un cuarto tipo tocaria esa clase. | `PoliticaCancelacion`, `CancelacionEstudiante`, `CancelacionCapitan`, `AnulacionAdministrativa` (politicas_cancelacion.py); `Reserva.cancelar()` solo delega |
| Factory Method | RF-01 + RF-05 mod. (el tipo de reserva depende de quien la pide) | Sin el, la decision de que clase instanciar y con que politica estaria duplicada en cada lugar que crea reservas (reservar, recurrente), y seria facil crear una reserva de capitan con politica de estudiante. | `CreadorReserva`, `CreadorReservaRegular`, `CreadorReservaEquipoOficial`, `creador_para()` (fabrica_reservas.py) |
| Abstract Factory | RF-14 | Sin el, el codigo armaria validador y notificador por separado y nada impediria validar con el horario de Norte y notificar por el canal de Sur (justo lo prohibido). | `FabricaSede`, `FabricaCampusNorte`, `FabricaCampusSur`; `Sede.__init__` saca los dos productos de la misma fabrica (sedes.py) |
| Builder | RF-09 | Sin el, el pedido recurrente seria un constructor con 6 parametros donde los opcionales van casi siempre vacios, o varios constructores repetidos. Ademas el builder valida el rango de 2 a 8 semanas en un solo lugar. | `ConstructorReservaRecurrente` (con_semanas, con_equipo, con_notas, construir), `PedidoRecurrente` (constructor_recurrente.py) |
| Prototype | RF-12 | Sin el, el administrador registraria cada bloqueo a mano repitiendo motivo, franja y equipo para cada cancha y fecha, con riesgo de escribirlos distinto. | `Bloqueo.clonar(cancha, fecha)` con `copy.deepcopy` (dominio.py) |
| Singleton | RNF-05 | Sin el, la hora limite, las ventanas de 2 y 24 horas, el limite de 3 y los 7 dias estarian repetidos como numeros sueltos por el codigo, y cambiar una regla seria buscar y reemplazar. | `Configuracion` (configuracion.py); la leen las politicas, la regla de prioridad, `Estudiante.registrar_no_show()` y el builder |
| Facade | RF-10, RF-13 y la consigna (simulacion solo habla con una entrada) | Sin ella, simulacion.py coordinaria a mano suspension + sede + disponibilidad + fabrica + notificador en cada operacion, repitiendo el mismo baile 4 veces y acoplandose a todos los subsistemas. | `FachadaReservaU.reservar()`, `.reservar_recurrente()`, `.cancelar()`, `.bloquear()` (fachada.py) |
| Concurrencia (lock pesimista) | RNF-06 | Sin el, dos hilos pueden ver la cancha libre al mismo tiempo y registrarse los dos (el incidente del primer lunes del semestre). | `FachadaReservaU.candado` (`threading.Lock`) alrededor de verificar + registrar en `reservar()`, `reservar_recurrente()` y `bloquear()` |

## Justificacion de Prototype: por que deepcopy y no copy.copy

El equipo del bloqueo es una **lista** (`["arcos", "vallas"]`). Con
`copy.copy` (copia superficial) el clon y la plantilla compartirian esa
misma lista: al agregarle una "tarima" al clon tambien se la agregariamos
a la plantilla, y todos los bloqueos futuros saldrian con tarima. Con
`copy.deepcopy` la lista tambien se copia, asi que modificar el equipo de
un clon no afecta a la plantilla. El escenario 6 de la simulacion lo
comprueba: se agrega "tarima" al clon 2 y la plantilla queda igual.

## Justificacion de Singleton: que gane y que costo acepte

Gane un unico lugar donde viven los valores de todas las reglas: cambiar
la ventana del capitan o el limite de no-shows es tocar una linea en
`configuracion.py` y todo el sistema (politicas, prioridad, suspension y
builder) lee el valor nuevo. El costo que acepte es que la configuracion
es un global disfrazado: las clases que la usan quedan acopladas a ella de
forma escondida (no se ve en sus parametros) y eso haria mas dificil, por
ejemplo, probar dos configuraciones distintas a la vez.

## Justificacion de la concurrencia: por que locking pesimista

En ReservaU hay muchas mas consultas de disponibilidad que reservas, con
picos de escritura al inicio del semestre. Nuestro candado es pesimista
pero **solo envuelve la seccion critica de escribir** (verificar
disponibilidad + registrar la reserva, que es corta): las consultas
sueltas no lo toman, asi que las muchas lecturas no se frenan. Un esquema
optimista (dejar que ambos escriban y detectar el choque despues para
reintentar) seria mas codigo y justo en los picos de inicio de semestre
provocaria reintentos en cadena sobre las franjas populares. Con el lock,
dos solicitudes simultaneas por la misma cancha y franja producen
exactamente una confirmada (escenario 7, RNF-06).

## Recorrido completo de la regla de los 3 no-shows

- **Requerimiento que la define:** RF-11 (nuevo): 3 no-shows en el mismo
  mes calendario -> suspension de 7 dias sin poder crear reservas.
- **Caso de uso y diagramas:** aparece en CU-02 (paso 4 y alterno 4a:
  registrar el no-show y suspender) y en CU-01 (alterno 2a: el suspendido
  no puede reservar). En los diagramas: paso 8 de la robustez, primer alt
  de la secuencia (`[el solicitante esta suspendido]`) y la transicion
  `confirmada -> no-show` de la maquina de estados.
- **Entidad que lleva la cuenta y metodo que suspende:** el propio
  `Estudiante`: `no_shows_del_mes(fecha)` cuenta y
  `registrar_no_show(fecha)` aplica la suspension (es quien conoce sus
  fechas de no-show). `esta_suspendido(fecha)` responde al bloqueo de
  nuevas reservas.
- **Valores que lee de la configuracion:** `limite_no_shows_mes` (3) y
  `dias_suspension` (7), del singleton `Configuracion`.
- **Donde se observa en la salida:** escenario 5 de simulacion.py: la
  tercera cancelacion de Carla imprime "lleva 3 en el mes / llego al
  limite: queda suspendido hasta el 19/10" y su intento siguiente imprime
  "el sistema la rechaza: Carla esta suspendido hasta el 19/10".

## Nota sobre el PSet 1

El PSet 1 queda intacto en `psets/pset-01/`. De ahi se copiaron y
extendieron: la estrategia de prioridad (ahora lee la configuracion), el
modelo rico de Cancha/Reserva/Estudiante/Capitan y el estilo de la
simulacion con prints por paso.
