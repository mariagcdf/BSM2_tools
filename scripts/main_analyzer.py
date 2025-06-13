from bsm2tools.loader import load_and_validate_csv #esta es obligatorio para que se cargue bien el CSV
from bsm2tools.analyzer import analizar_violaciones

df = load_and_validate_csv("data/datos_simulados_planta_completo.csv") #este es el CSV que está en \data

violaciones_info = analizar_violaciones(
    df,
      columna_objetivo="DBO_salida (mg/L)",
      umbral=10,
      variables_causales=["F/M", "TRC (d-1)", "TRH (h)"],
      nombre_parametro="DBO",
      imprimir=True
      # Todos estos parámetros son personalizables. Consulta la sección siguiente para más detalles.
)