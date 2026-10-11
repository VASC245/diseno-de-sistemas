# ReservaU v2 - PSet 2
# docker build -t reservau-v2 .
# docker run reservau-v2
FROM python:3.12-slim

WORKDIR /app

# solo biblioteca estandar de python, no hay dependencias
COPY configuracion.py reglas_prioridad.py politicas_cancelacion.py \
     sedes.py dominio.py fabrica_reservas.py constructor_recurrente.py \
     fachada.py simulacion.py ./

CMD ["python", "simulacion.py"]
