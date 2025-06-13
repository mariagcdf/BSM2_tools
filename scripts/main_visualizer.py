#en este script es en el que puedes cambiar los parámetros de análisis y la ruta del CSV

from bsm2tools.loader import load_and_validate_csv
from bsm2tools.visualizer import graficar_sankey

# Cargar y analizar datos (desde el CSV que tengo subido en data)
df = load_and_validate_csv("data/datos_simulados_planta_completo.csv")

#Graficar
graficar_sankey(
    df,
    columna_objetivo="DBO_salida (mg/L)",
    umbral=10,
    variables_causales=["F/M", "TRC (d-1)", "TRH (h)"],
    nombre_parametro="DBO"
)