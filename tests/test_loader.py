import pandas as pd
from bsm2tools.loader import load_csv

def test_load_csv_realistic():
    # Simula un pequeño dataset como el de BSM2
    data = {
        'Time': [0, 15, 30],
        'Q': [18465.7, 18392.5, 18402.0],
        'TSS': [2985.4, 2992.1, 3000.0],
        'SALK': [4.2, 4.3, 4.1],
        'TN': [32.5, 33.0, 32.7],
        'SNH': [15.3, 15.0, 15.5],
        'Temp': [17.2, 17.4, 17.5]
    }
    df_expected = pd.DataFrame(data)

    # Guardamos como un CSV temporal
    test_csv_path = 'test_bsm2.csv'
    df_expected.to_csv(test_csv_path, index=False)

    # Cargar usando tu función
    df_loaded = load_csv(test_csv_path)

    # Verificar que los datos coinciden
    pd.testing.assert_frame_equal(df_loaded, df_expected)
