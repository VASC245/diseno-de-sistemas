# PSet 1 - ReservaU

Plataforma de reservas de canchas deportivas de la universidad.

## Que hay en la carpeta

- `requerimientos.pdf` - requerimientos funcionales y no funcionales
- `modelo-de-dominio.pdf` - diagrama de clases
- `casos-de-uso.pdf` - diagrama de casos de uso
- `flujos-casos-de-uso.pdf` - flujo de cada caso de uso con sus flujos alternos
- `implementacion/` - el codigo:
  - `reglas_prioridad.py` - la regla de prioridad en su propia clase (strategy)
  - `dominio.py` - las clases del sistema
  - `simulacion.py` - corre todos los flujos e imprime cada paso
  - `Dockerfile`

## Como correrlo

Local:

```
cd implementacion
python3 simulacion.py
```

Con Docker:

```
cd implementacion
docker build -t reservau .
docker run reservau
```

La simulacion usa una fecha fija para que la salida siempre sea la misma.

## Nota sobre la prioridad

Como "prioridad para reservar antes de las 6 pm" se puede interpretar de
varias formas, asumimos que significa: cuando varias personas piden el
mismo horario y ese horario empieza antes de las 18:00, gana el equipo
oficial. De las 18:00 en adelante no hay prioridad y gana el que pidio
primero. Esto esta igual en RF-03, en el paso 3b de CU-01 y en la clase
PrioridadEquipoOficial.