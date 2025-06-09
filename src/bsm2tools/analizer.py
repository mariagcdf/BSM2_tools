import pandas as pd
import matplotlib.pyplot as plt


def analizar_violaciones(df, columna_objetivo, umbral, variables_operativas):
    """Detecta violaciones normativas y analiza causas directas simples."""
    violaciones = df[df[columna_objetivo] > umbral]
    resultado = []

    for idx, fila in violaciones.iterrows():
        fecha = fila['Día'] if 'Día' in df.columns else idx
        causas = []

        for var in variables_operativas:
            if var not in df.columns or pd.isnull(fila[var]):
                continue

            if idx >= 15:
                media_local = df.iloc[max(0, idx-15):idx][var].mean()
                if fila[var] > media_local * 1.3:
                    causas.append(f"{var} alto")
                elif fila[var] < media_local * 0.7:
                    causas.append(f"{var} bajo")

        ajuste = evaluar_respuesta_operacional(df, idx, var_control=variables_operativas[0])

        resultado.append({
            'fecha': fecha,
            'valor': fila[columna_objetivo],
            'causas_detectadas': causas,
            'respuesta_operativa': ajuste
        })

    return resultado


def evaluar_respuesta_operacional(df, idx, var_control, umbral=0.1):
    """Evalúa si se aplicó una respuesta operativa tras una violación"""
    if var_control not in df.columns or idx >= len(df) - 3:
        return None

    valor_actual = df.at[idx, var_control]
    futuros = df.iloc[idx+1:idx+4][var_control].dropna()

    for v in futuros:
        if abs((v - valor_actual) / valor_actual) > umbral:
            return f"Ajuste en {var_control} tras violación"
    return None


def graficar_violaciones_mensuales(df, columna_objetivo, umbral):
    """Grafica el número de violaciones mensuales"""
    if 'Día' not in df.columns:
        raise ValueError("La columna 'Día' no está en el DataFrame")

    df['Día'] = pd.to_datetime(df['Día'])
    df['Mes'] = df['Día'].dt.to_period('M')
    violaciones = df[df[columna_objetivo] > umbral]
    conteo = violaciones['Mes'].value_counts().sort_index()

    conteo.plot(kind='bar', figsize=(10, 5), color='steelblue', edgecolor='black')
    plt.title(f'Violaciones mensuales de {columna_objetivo}')
    plt.xlabel('Mes')
    plt.ylabel('Nº de violaciones')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
