#######FUNCION DE ANALISIS CAUSAL############

def evaluar_respuesta_operacional(df, fila_actual, indice_actual, hubo_lluvia):
    import pandas as pd
    respuestas = []

    #se obtiene el índice de la fila actual y se definen los días posteriores (3 días) y los días anteriores (2 días)
    dias_post = df.iloc[indice_actual+1:indice_actual+4]
    dias_prev = df.iloc[max(0, indice_actual-2):indice_actual]

    # si supera el 2% de cambio, se considera significativo
    umbral_alto = 1.02
    umbral_bajo = 0.98

    # Función para determinar si el cambio es significativo (por medio de un ratio, y si supera el 2% de cambio-umbral)
    def cambio_significativo(valor_nuevo, valor_antiguo):
        if pd.notnull(valor_nuevo) and pd.notnull(valor_antiguo) and valor_antiguo != 0:
            ratio = valor_nuevo / valor_antiguo
            return ratio > umbral_alto or ratio < umbral_bajo
        return False

    #se evalúan las respuestas operativas para cada variable manipulable, comparando los valores actuales con los de los días posteriores
    # Recirculación interna
    if 'Recir. Interna (m3/d)' in df.columns and pd.notnull(fila_actual['Recir. Interna (m3/d)']):
        for i in dias_post["Recir. Interna (m3/d)"]:
            valor_posterior = i
            valor_actual = fila_actual['Recir. Interna (m3/d)']
            if cambio_significativo(valor_posterior, valor_actual):
                if valor_posterior > valor_actual:
                    respuestas.append("↑Recir.int tras violación")
                else:
                    respuestas.append("↓Recir.int tras violación")
                break

    # Recirculación externa
    if 'Recir. Externa (m3/d)' in df.columns and pd.notnull(fila_actual['Recir. Externa (m3/d)']):
        for i, fila_post in dias_post.iterrows():
            valor_posterior = fila_post['Recir. Externa (m3/d)']
            valor_actual = fila_actual['Recir. Externa (m3/d)']
            if cambio_significativo(valor_posterior, valor_actual):
                if valor_posterior > valor_actual:
                    respuestas.append("↑Recir.ext tras violación")
                else:
                    respuestas.append("↓Recir.ext tras violación")
                break

    # Anticipación a lluvia (recirculación externa)
    if hubo_lluvia:
    # Comparar con la media de los dos días anteriores
        for variable, etiqueta in [
            ('Recir. Externa (m3/d)', "ajuste de Recir. ext. pre-lluvia"),
            ('Recir. Interna (m3/d)', "ajuste de Recir. int. pre-lluvia"),
        ]:
            if variable in df.columns:
                valores_previos = dias_prev[variable].dropna()
                valor_actual = fila_actual.get(variable)

                if not valores_previos.empty and pd.notnull(valor_actual): #mira que no haya valores nulos
                    media_previos = valores_previos.mean() #hace la media de los valores anteriores (2 días)
                    if media_previos != 0: # para evitar división por cero (esque hay veces que no hay datos durante una semana entera)
                        #si el valor del día de lluvia varió más de un 10% respecto a la media previa, lo considera anticipación operativa.
                        ratio = valor_actual / media_previos
                        if ratio > 1.05 or ratio < 0.95: #
                            respuestas.append(etiqueta)
    return respuestas
### FIN DE LA FUNCIÓN PARA EVALUAR RESPUESTAS OPERACIONALES DESPUÉS DE UNA VIOLACIÓN ######


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
