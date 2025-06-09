import pandas as pd

def load_csv(filepath):
    """
    Carga un archivo CSV y devuelve un DataFrame de pandas.

    Parámetros:
    filepath (str): Ruta al archivo CSV.

    Retorna:
    pd.DataFrame: Datos cargados.
    """
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error cargando el archivo: {e}")
        return None
