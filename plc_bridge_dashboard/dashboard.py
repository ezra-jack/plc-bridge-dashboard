import streamlit as st, time
from src.bridge import load_data, window
from src.kpis import throughput_pph, scrap_rate, oee_simple
from src.alarms import evaluate_alarms

st.set_page_config(page_title='PLC Dashboard', layout='wide')
st.title('PLC Bridge Dashboard (Simplified OEE)')

df = load_data()
if df.empty:
    st.warning('No data yet.')
else:
    dfw = window(df, minutes=60)
    tpph = throughput_pph(dfw)
    sr = scrap_rate(dfw)
    oee, A, Q = oee_simple(dfw)

    col1,col2,col3,col4 = st.columns(4)
    col1.metric('Throughput (pph)', f'{tpph:.1f}')
    col2.metric('Scrap Rate', f'{sr*100:.1f}%')
    col3.metric('OEE (A×Q)', f'{oee*100:.1f}%')
    col4.metric('A | Q', f'{A*100:.0f}% | {Q*100:.0f}%')
