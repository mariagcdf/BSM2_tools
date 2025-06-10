import plotly.graph_objects as go
import pandas as pd
from collections import Counter
from bsm2tools.analyzer import analizar_violaciones

def graficar_sankey(input_data, columna_objetivo="DBO_salida (mg/L)", umbral=25,
                    variables_causales=None, nombre_parametro="DBO"):
    """
    Si recibe un DataFrame, ejecuta automáticamente el análisis de violaciones.
    Si recibe una lista de dicts (violaciones_info), la usa directamente.
    """
    if variables_causales is None:
        variables_causales = ["F/M", "TRC (d-1)", "TRH (h)"]

    if isinstance(input_data, pd.DataFrame):
        violaciones_info = analizar_violaciones(
            input_data,
            columna_objetivo=columna_objetivo,
            umbral=umbral,
            variables_causales=variables_causales,
            nombre_parametro=nombre_parametro,
            imprimir=False
        )
    else:
        violaciones_info = input_data

    if not violaciones_info:
        print("No se detectaron violaciones. No se generará el diagrama Sankey.")
        return

    opcion = input("\n¿Visualizar Sankey para todo el año o un mes concreto? (todo/mes): ").strip().lower()
    mes_seleccionado = None
    if opcion == "mes":
        mes_seleccionado = input("Introduce el mes en formato AAAA-MM: ").strip()
        try:
            pd.to_datetime(mes_seleccionado + "-01")
        except ValueError:
            print("Mes no válido. Se mostrará todo el año.")
            mes_seleccionado = None

    if mes_seleccionado:
        violaciones_info = [
            v for v in violaciones_info
            if pd.to_datetime(v['fecha']).strftime('%Y-%m') == mes_seleccionado
        ]
        if not violaciones_info:
            print("No hay violaciones en ese mes.")
            return

    enlaces_1, enlaces_2 = [], []
    for v in violaciones_info:
        causas = v.get('causas_directas') or ["sin causa"]
        explicaciones = v.get('explicaciones') or ["sin explicación"]
        estrategias = v.get('estrategias_control_reactivas') or ["sin estrategia"]

        for causa in causas:
            for explicacion in explicaciones:
                enlaces_1.append((causa, explicacion))
                for estrategia in estrategias:
                    enlaces_2.append((explicacion, estrategia))

    conteos_1 = Counter(enlaces_1)
    conteos_2 = Counter(enlaces_2)

    nodos_causas = sorted(set(c for c, _ in conteos_1))
    nodos_explicaciones = sorted(set(e for _, e in conteos_1))
    nodos_estrategias = sorted(set(e for _, e in conteos_2))

    nodos = nodos_causas + nodos_explicaciones + nodos_estrategias
    indices = {n: i for i, n in enumerate(nodos)}

    sources, targets, values = [], [], []

    for (c, e), v in conteos_1.items():
        sources.append(indices[c])
        targets.append(indices[e])
        values.append(v)

    for (e, s), v in conteos_2.items():
        sources.append(indices[e])
        targets.append(indices[s])
        values.append(v)

    colores = (
        ['rgba(31, 119, 180, 0.8)'] * len(nodos_causas) +
        ['rgba(148, 103, 189, 0.8)'] * len(nodos_explicaciones) +
        ['rgba(214, 39, 40, 0.8)'] * len(nodos_estrategias)
    )

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=8,
            thickness=8,
            line=dict(color="black", width=0.5),
            label=nodos,
            color=colores
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(150,150,150,0.3)"
        )
    )])

    titulo = f"Diagrama Sankey causal para {nombre_parametro}"
    if mes_seleccionado:
        titulo += f" ({mes_seleccionado})"

    fig.update_layout(
        title_text=titulo,
        font_size=13,
        width=1300,
        height=600
    )

    fig.show()
