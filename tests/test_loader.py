import pytest
import pandas as pd
from io import StringIO
from bsm2tools.loader import load_and_validate_csv

VALID_CSV = """Día,DBO_salida (mg/L),DQO_salida (mg/L),SST_salida (mg/L),Ntot_salida (mg/L),NH_salida (mg/L),PT_salida (mg/L),F/M,TRC (d-1),TRH (h),Recir. Interna (m3/d),Recir. Externa (m3/d),Q (m3/d),Temperatura (ºC),DQO_brut (mg/L),DBO_brut (mg/L),SST_brut (mg/L),NH_brut (mg/L)
2025-01-01,12,80,25,15,3.5,1.1,0.4,15,6,1200,300,10000,18,350,220,180,28
"""

INVALID_CSV = """Día,DBO_salida (mg/L),DQO_salida (mg/L)
2025-01-01,12,80
"""

def test_load_and_validate_csv_valid():
    data = StringIO(VALID_CSV)
    df = load_and_validate_csv(data, sep=",", verbose=False)
    assert isinstance(df, pd.DataFrame)
    assert 'Día' in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df['Día'])

def test_load_and_validate_csv_invalid():
    data = StringIO(INVALID_CSV)
    with pytest.raises(ValueError) as exc_info:
        load_and_validate_csv(data, sep=",", verbose=False)
    assert "Missing required columns" in str(exc_info.value)