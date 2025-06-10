from bsm2tools.loader import load_and_validate_csv
from bsm2tools.analyzer import analizar_violaciones
from bsm2tools.visualizer import graficar_sankey

# Carga el CSV
df = load_and_validate_csv("data/datos_simulados_planta_completo.csv", sep=";")

# Análisis de violaciones (ej: DBO > 25 mg/L)
violaciones_info = analizar_violaciones(
    df,
    columna_objetivo="DBO_salida (mg/L)",
    umbral=25,
    variables_causales=["F/M", "TRC (d-1)", "TRH (h)"],
    nombre_parametro="DBO",
    imprimir=True  # Muestra detalles en consola
)

# Genera el diagrama de Sankey
graficar_sankey(
    df,
    columna_objetivo="DBO_salida (mg/L)",
    umbral=25,
    variables_causales=["F/M", "TRC (d-1)", "TRH (h)"],
    nombre_parametro="DBO"
)