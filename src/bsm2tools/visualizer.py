import plotly.graph_objects as go
import pandas as pd
from collections import Counter

def graficar_sankey_causas_explicaciones(violaciones_info, columna_objetivo='el parámetro'):
    """
    Generate a Sankey diagram to visualize the flow from direct causes 
    to explanations to reactive control strategies for violations.
    
    Parameters:
    - violaciones_info: list of dicts from analizar_violaciones
    - columna_objetivo: name of the violated parameter (for title)
    """

    if not violaciones_info:
        print("No hay violaciones que mostrar en el diagrama Sankey.")
        return

    # Ask for user input (year or specific month)
    opcion = input("\nVisualizar Sankey para todo el año o un mes concreto? (todo/mes): ").strip().lower()
    mes_seleccionado = None
    if opcion == "mes":
        mes_seleccionado = input("Introduce el mes en formato AAAA-MM: ").strip()
        try:
            pd.to_datetime(mes_seleccionado + "-01")
        except ValueError:
            print("Formato de mes no válido. Se visualizará todo el año.")
            mes_seleccionado = None

    # Filter by selected month if needed
    if mes_seleccionado:
        violaciones_info = [v for v in violaciones_info if pd.to_datetime(v['fecha']).strftime('%Y-%m') == mes_seleccionado]

    if not violaciones_info:
        print("No hay violaciones en el mes seleccionado.")
        return

    # Create link pairs
    enlaces_1 = []  # causa -> explicacion
    enlaces_2 = []  # explicacion -> estrategia

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

    sources = []
    targets = []
    values = []

    for (c, e), v in conteos_1.items():
        sources.append(indices[c])
        targets.append(indices[e])
        values.append(v)

    for (e, s), v in conteos_2.items():
        sources.append(indices[e])
        targets.append(indices[s])
        values.append(v)

    colores = [
        'rgba(31, 119, 180, 0.8)' for _ in nodos_causas
    ] + [
        'rgba(148, 103, 189, 0.8)' for _ in nodos_explicaciones
    ] + [
        'rgba(214, 39, 40, 0.8)' for _ in nodos_estrategias
    ]

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

    titulo = f"Causal Sankey diagram for {columna_objetivo}"
    if mes_seleccionado:
        titulo += f" ({mes_seleccionado})"

    fig.update_layout(
        title_text=titulo,
        font_size=13,
        width=1300,
        height=600
    )

    fig.show()
