#######FUNCION DE ANALISIS CAUSAL############

def analizar_violaciones(df, columna_objetivo, umbral, variables_causales, nombre_parametro='el parámetro'):
    import pandas as pd
    import numpy as np

    violaciones = df[df[columna_objetivo] > umbral]
    medias = df.select_dtypes(include='number').mean()
    desviaciones = df.select_dtypes(include='number').std()

    # Calcular percentiles para las causas secundarias (son perturbaciones relacionados con el influente)
    p_temp_baja = np.percentile(df['Temperatura (ºC)'].dropna(), 20)
    p_temp_alta = np.percentile(df['Temperatura (ºC)'].dropna(), 80)
    p_q_alto = np.percentile(df['Q (m3/d)'].dropna(), 80)
    dqo_bruta_alto = np.percentile(df['DQO_brut (mg/L)'].dropna(), 80)
    tss_bruta_alto = np.percentile(df['SST_brut (mg/L)'].dropna(), 80)
    nh_bruto_alto = np.percentile(df['NH_brut (mg/L)'].dropna(), 80)
    dbo_bruta_alto = np.percentile(df['DBO_brut (mg/L)'].dropna(), 80)

    violaciones_info = []

    # Recorro las filas de violaciones para analizar cada una, rellenar las causas directas y secundarias
    for idx, fila in violaciones.iterrows():
        fecha = pd.to_datetime(fila['Día']).date()
        causas_directas = []
        causas_secundarias = []

        # Defino el hubo_lluvia
        hubo_lluvia = False

        for var in variables_causales:
            if pd.notnull(fila[var]):
                valor = fila[var]
                media = medias[var]
                std = desviaciones[var]

                if idx >= 15:
                    media_local = df.loc[idx-15:idx-1, var].mean()
                    if pd.notnull(media_local):
                        if valor < media_local * 0.7:
                            causas_directas.append(f"{var} bajo respecto a días anteriores")
                        elif valor > media_local * 1.3:
                            causas_directas.append(f"{var} alto respecto a días anteriores")

        if pd.notnull(fila['Temperatura (ºC)']):
            if fila['Temperatura (ºC)'] < p_temp_baja:
                causas_secundarias.append("↓ T")
            elif fila['Temperatura (ºC)'] > p_temp_alta:
                causas_secundarias.append("↑ T")

        if fila['Q (m3/d)'] > p_q_alto:
            hubo_lluvia = True
            if fila['SST_brut (mg/L)'] > tss_bruta_alto:
                causas_secundarias.append("↑Q+TSS (posible arrastre de sólidos por lluvia)")
            else:
                causas_secundarias.append("↑Q (posible lluvia)")

        if pd.notnull(fila['DQO_brut (mg/L)']) and pd.notnull(fila['DBO_brut (mg/L)']):
            if fila['DQO_brut (mg/L)'] > dqo_bruta_alto and fila['DBO_brut (mg/L)'] > dbo_bruta_alto:
                causas_secundarias.append("↑DQO+DBO influente (posible vertido orgánico intenso)")
            elif fila['DQO_brut (mg/L)'] > dqo_bruta_alto:
                causas_secundarias.append("↑DQO influente (posible vertido no biodegradable)")
            elif fila['DBO_brut (mg/L)'] > dbo_bruta_alto:
                causas_secundarias.append("↑DBO influente (posible carga biodegradable alta)")

        if pd.notnull(fila['NH_brut (mg/L)']) and fila['NH_brut (mg/L)'] > nh_bruto_alto:
            causas_secundarias.append("↑NH influente (posible vertido con alto nitrógeno)")

        estrategias_control_reactivas = evaluar_respuesta_operacional(df, fila, idx, hubo_lluvia)

        if len(causas_directas) > 1:
            print(f"📅 {fecha} → violación de {nombre_parametro} ({columna_objetivo} > {umbral})")
            print(f"  ↪ Causas directas: {', '.join(causas_directas)}")
            if causas_secundarias:
                print(f"  ↪ Posibles explicaciones: {', '.join(causas_secundarias)}")
            if estrategias_control_reactivas:
                print(f"  ↪ Respuestas operativas: {', '.join(estrategias_control_reactivas)}")
            print("-" * 80)

        violaciones_info.append({
            'fecha': fecha,
            'causas_directas': causas_directas,
            'explicaciones': causas_secundarias,
            'estrategias_control_reactivas': estrategias_control_reactivas
        })
    return violaciones_info
####FIN DE LA FUNCIÓN ANALIZAR VIOLACIONES####
