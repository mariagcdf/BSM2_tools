import matplotlib.pyplot as plt

def plot_variable(df, column_name):
    """
    Dibuja una gráfica de línea para una columna del DataFrame.

    Parámetros:
    df (pd.DataFrame): DataFrame de pandas.
    column_name (str): Nombre de la columna a graficar.
    """
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(df[column_name], marker='o')
        plt.title(f"Plot of {column_name}")
        plt.xlabel("Index")
        plt.ylabel(column_name)
        plt.grid()
        plt.show()
    except Exception as e:
        print(f"Error al graficar la variable: {e}")
