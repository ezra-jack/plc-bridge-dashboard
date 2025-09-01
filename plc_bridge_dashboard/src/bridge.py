import os, pandas as pd
from datetime import timedelta

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_stream.csv')

def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        return pd.DataFrame(columns=['timestamp','work_order','station','part_id','line_speed','motor_temp','vibration_rms','parts_in','parts_out','scrap_flag'])
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)

def window(df, minutes=60):
    if df.empty: return df
    t_end = df['timestamp'].iloc[-1]
    return df[df['timestamp']>=t_end - timedelta(minutes=minutes)]
