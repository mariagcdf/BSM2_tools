import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pandas as pd
from bsm2tools.analyzer import analizar_violaciones

def test_analizar_violaciones():
    data = {
        'Día': pd.date_range(start='2023-01-01', periods=20, freq='D'),
        'Temperatura (ºC)': [15]*10 + [25]*10,
        'Q (m3/d)': [1000]*10 + [3000]*10,
        'DQO_brut (mg/L)': [500]*10 + [1200]*10,
        'DBO_brut (mg/L)': [200]*10 + [700]*10,
        'SST_brut (mg/L)': [50]*10 + [200]*10,
        'NH_brut (mg/L)': [20]*10 + [60]*10,
        'TRH (d)': [5]*10 + [10]*10,
        'TRC (d)': [3]*10 + [6]*10,
        'F/M': [0.2]*10 + [0.6]*10,
        'Recir. Interna (m3/d)': [500]*10 + list(range(600, 610)),
        'Recir. Externa (m3/d)': [400]*10 + list(range(450, 460)),
        'NH4_efluente': [1]*15 + [10]*5
    }

    df_test = pd.DataFrame(data)

    result = analizar_violaciones(
        df=df_test,
        columna_objetivo='NH4_efluente',
        umbral=5,
        variables_causales=['TRH (d)', 'TRC (d)', 'F/M'],
        nombre_parametro='NH4 en el efluente'
    )

    assert isinstance(result, list)
    assert len(result) == 5  # Últimos 5 días violan el umbral
    assert all('fecha' in r and 'causas_directas' in r for r in result)
