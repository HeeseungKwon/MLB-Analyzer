"""Streamlit app to display top picks based on scores table.
This is an interactive starter UI.
"""
import os
from dotenv import load_dotenv
import streamlit as st
import sqlalchemy
import pandas as pd

load_dotenv()

engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL'))

st.title('MLB HR / HRR Prospects Analyzer - Starter')

st.markdown('This is a starter UI that displays top picks from the scores table.')

date = st.date_input('As of date')

if st.button('Load top picks'):
    query = 'SELECT player_id, total_score, season_score, recent_score, matchup_score, statcast_score, park_score, weather_score, bullpen_score FROM scores WHERE as_of = %s ORDER BY total_score DESC LIMIT 200'
    try:
        df = pd.read_sql_query(query, engine, params=(date,))
    except Exception as e:
        st.error(f'Error reading scores from DB: {e}')
        df = None
    if df is None or df.empty:
        st.info('No scores found for this date — run the ingestion and scoring pipeline first')
    else:
        st.subheader('Top 50 by total score')
        st.dataframe(df.head(50))
        st.subheader('Top 10 HR prospects')
        st.dataframe(df.head(10))
