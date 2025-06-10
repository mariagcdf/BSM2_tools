import pandas as pd
import numpy as np

def evaluar_respuesta_operacional(df, fila_actual, indice_actual, hubo_lluvia):
    respuestas = []
    dias_post = df.iloc[indice_actual+1:indice_actual+4]
    dias_prev = df.iloc[max(0, indice_actual-2):indice_actual]

    umbral_alto = 1.02
    umbral_bajo = 0.98

    def cambio_significativo(valor_nuevo, valor_antiguo):
        if pd.notnull(valor_nuevo) and pd.notnull(valor_antiguo) and valor_antiguo != 0:
            ratio = valor_nuevo / valor_antiguo
            return ratio > umbral_alto or ratio < umbral_bajo
        return False

    for variable, etiqueta_alta, etiqueta_baja in [
        ("Recir. Interna (m3/d)", "↑Recir.int tras violación", "↓Recir.int tras violación"),
        ("Recir. Externa (m3/d)", "↑Recir.ext tras violación", "↓Recir.ext tras violación")
    ]:
        if variable in df.columns and pd.notnull(fila_actual.get(variable)):
            for i in dias_post[variable]:
                if cambio_significativo(i, fila_actual[variable]):
                    respuestas.append(etiqueta_alta if i > fila_actual[variable] else etiqueta_baja)
                    break

    if hubo_lluvia:
        for variable, etiqueta in [
            ('Recir. Externa (m3/d)', "ajuste de Recir. ext. pre-lluvia"),
            ('Recir. Interna (m3/d)', "ajuste de Recir. int. pre-lluvia"),
        ]:
            if variable in df.columns:
                valores_previos = dias_prev[variable].dropna()
                valor_actual = fila_actual.get(variable)
                if not valores_previos.empty and pd.notnull(valor_actual):
                    media_previos = valores_previos.mean()
                    if media_previos != 0:
                        ratio = valor_actual / media_previos
                        if ratio > 1.05 or ratio < 0.95:
                            respuestas.append(etiqueta)
    return respuestas


def analizar_violaciones(df, columna_objetivo="DBO_salida (mg/L)", umbral=25,
                         variables_causales=None, nombre_parametro="DBO", imprimir=False):
    if variables_causales is None:
        variables_causales = ['F/M', 'TRC (d-1)', 'TRH (h)']

    violaciones = df[df[columna_objetivo] > umbral]

    # Precomputar estadísticas
    p_temp_baja = np.percentile(df['Temperatura (ºC)'].dropna(), 20)
    p_temp_alta = np.percentile(df['Temperatura (ºC)'].dropna(), 80)
    p_q_alto = np.percentile(df['Q (m3/d)'].dropna(), 80)
    dqo_bruta_alto = np.percentile(df['DQO_brut (mg/L)'].dropna(), 80)
    tss_bruta_alto = np.percentile(df['SST_brut (mg/L)'].dropna(), 80)
    nh_bruto_alto = np.percentile(df['NH_brut (mg/L)'].dropna(), 80)
    dbo_bruta_alto = np.percentile(df['DBO_brut (mg/L)'].dropna(), 80)

    resultados = []

    for idx, fila in violaciones.iterrows():
        fecha = pd.to_datetime(fila['Día']).date()
        causas_directas = []
        causas_secundarias = []
        hubo_lluvia = False

        for var in variables_causales:
            if pd.notnull(fila.get(var)):
                media_local = df.loc[max(0, idx-15):idx-1, var].mean()
                if pd.notnull(media_local):
                    if fila[var] < media_local * 0.7:
                        causas_directas.append(f"{var} bajo respecto a días anteriores")
                    elif fila[var] > media_local * 1.3:
                        causas_directas.append(f"{var} alto respecto a días anteriores")

        if pd.notnull(fila.get('Temperatura (ºC)')):
            if fila['Temperatura (ºC)'] < p_temp_baja:
                causas_secundarias.append("↓ T")
            elif fila['Temperatura (ºC)'] > p_temp_alta:
                causas_secundarias.append("↑ T")

        if fila.get('Q (m3/d)', 0) > p_q_alto:
            hubo_lluvia = True
            if fila.get('SST_brut (mg/L)', 0) > tss_bruta_alto:
                causas_secundarias.append("↑Q+TSS (posible arrastre de sólidos por lluvia)")
            else:
                causas_secundarias.append("↑Q (posible lluvia)")

        if pd.notnull(fila.get('DQO_brut (mg/L)')) and pd.notnull(fila.get('DBO_brut (mg/L)')):
            if fila['DQO_brut (mg/L)'] > dqo_bruta_alto and fila['DBO_brut (mg/L)'] > dbo_bruta_alto:
                causas_secundarias.append("↑DQO+DBO influente (posible vertido orgánico intenso)")
            elif fila['DQO_brut (mg/L)'] > dqo_bruta_alto:
                causas_secundarias.append("↑DQO influente (posible vertido no biodegradable)")
            elif fila['DBO_brut (mg/L)'] > dbo_bruta_alto:
                causas_secundarias.append("↑DBO influente (posible carga biodegradable alta)")

        if pd.notnull(fila.get('NH_brut (mg/L)')) and fila['NH_brut (mg/L)'] > nh_bruto_alto:
            causas_secundarias.append("↑NH influente (posible vertido con alto nitrógeno)")

        estrategias = evaluar_respuesta_operacional(df, fila, idx, hubo_lluvia)

        if imprimir and causas_directas:
            print(f"📅 {fecha} → violación de {nombre_parametro} ({columna_objetivo} > {umbral})")
            print(f"  ↪ Causas directas: {', '.join(causas_directas)}")
            if causas_secundarias:
                print(f"  ↪ Posibles explicaciones: {', '.join(causas_secundarias)}")
            if estrategias:
                print(f"  ↪ Respuestas operativas: {', '.join(estrategias)}")
            print("-" * 80)

        resultados.append({
            'fecha': fecha,
            'causas_directas': causas_directas,
            'explicaciones': causas_secundarias,
            'estrategias_control_reactivas': estrategias
        })

    return resultados
