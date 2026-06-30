"""Streamlit app to display top picks based on scores table.
This is an interactive starter UI.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import sqlalchemy
import pandas as pd

# Load .env from the repo root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

database_url = os.getenv('DATABASE_URL')
if not database_url:
    st.error('DATABASE_URL not found in .env file')
    st.stop()

engine = sqlalchemy.create_engine(database_url)

st.title('MLB HR / HRR Prospects Analyzer - Starter')

st.markdown('This is a starter UI that displays top picks from the scores table.')

date = st.date_input('As of date')

if st.button('Load top picks'):
    query = '''
        SELECT s.player_id, COALESCE(p.full_name, 'Unknown') as player_name, 
               s.total_score, s.season_score, s.recent_score, s.matchup_score, 
               s.statcast_score, s.park_score, s.weather_score, s.bullpen_score 
        FROM scores s
        LEFT JOIN players p ON s.player_id = p.player_id
        WHERE s.as_of = %s 
        ORDER BY s.total_score DESC
    '''
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
