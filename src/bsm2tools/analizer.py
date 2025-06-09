def calculate_statistics(df):
    """
    Calcula estadísticas básicas (media y desviación estándar) de un DataFrame.

    Parámetros:
    df (pd.DataFrame): DataFrame de pandas.

    Retorna:
    pd.DataFrame: DataFrame con estadísticas (mean, std).
    """
    try:
        mean = df.mean()
        std = df.std()
        summary = {"mean": mean, "std": std}
        return summary
    except Exception as e:
        print(f"Error al calcular estadísticas: {e}")
        return None