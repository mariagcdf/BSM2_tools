import pandas as pd

REQUIRED_COLUMNS = [
    'Día',
    'DBO_salida (mg/L)', 'DQO_salida (mg/L)', 'SST_salida (mg/L)',
    'Ntot_salida (mg/L)', 'NH_salida (mg/L)', 'PT_salida (mg/L)',
    'F/M', 'TRC (d-1)', 'TRH (h)',
    'Recir. Interna (m3/d)', 'Recir. Externa (m3/d)',
    'Q (m3/d)', 'Temperatura (ºC)',
    'DQO_brut (mg/L)', 'DBO_brut (mg/L)',
    'SST_brut (mg/L)', 'NH_brut (mg/L)'
]

def load_and_validate_csv(path: str, sep: str = ',', verbose: bool = True) -> pd.DataFrame:
    """
    Loads a CSV file and checks that all required columns are present.
    
    Parameters:
    - path (str): Path to the CSV file.
    - sep (str): Separator used in the CSV (default: ',').
    - verbose (bool): If True, print informative messages.

    Returns:
    - pd.DataFrame: The validated dataframe.

    Raises:
    - ValueError: If required columns are missing.
    """
    df = pd.read_csv(path, sep=sep)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"❌ Missing required columns in CSV: {missing}")

    # Convert 'Día' to datetime
    df['Día'] = pd.to_datetime(df['Día'], errors='coerce')
    if df['Día'].isnull().any():
        raise ValueError("❌ Some values in 'Día' could not be converted to datetime.")

    if verbose:
        print("✅ CSV loaded successfully. All required columns are present.")
    
    return df
