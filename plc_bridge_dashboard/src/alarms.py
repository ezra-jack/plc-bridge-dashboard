def evaluate_alarms(df, motor_temp_max=80, vibration_max=7.5):
    events = []
    if df.empty: return events
    last = df.iloc[-1]
    if last['motor_temp']>motor_temp_max: events.append(('CRITICAL', f"High Motor Temp {last['motor_temp']}"))
    if last['vibration_rms']>vibration_max: events.append(('WARNING', f"High Vibration {last['vibration_rms']}"))
    if last['line_speed']<=0: events.append(('INFO','Line stopped'))
    return events
