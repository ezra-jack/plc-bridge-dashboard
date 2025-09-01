import pandas as pd

def throughput_pph(df, window_hours=None):
    if df.empty:
        return 0.0
    t_hours = (pd.to_datetime(df["timestamp"]).iloc[-1] - pd.to_datetime(df["timestamp"]).iloc[0]).total_seconds()/3600.0
    if t_hours <= 0:
        return 0.0
    delta_out = df["parts_out"].iloc[-1] - df["parts_out"].iloc[0]
    return max(0.0, delta_out/t_hours)

def scrap_rate(df):
    if df.empty: return 0.0
    scr = df["scrap_flag"].sum()
    total = scr + (df["parts_out"].iloc[-1] - df["parts_out"].iloc[0]) + 1e-6
    return scr/total

def availability(df):
    if df.empty: return 0.0
    down = (df["line_speed"]<=0).sum()
    return 1 - down/len(df)

def quality(df):
    return 1 - scrap_rate(df)

def oee_simple(df):
    A = availability(df)
    Q = quality(df)
    return A*Q, A, Q
