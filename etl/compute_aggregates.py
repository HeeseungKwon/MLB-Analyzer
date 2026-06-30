"""Compute aggregates and scores for the day.
This orchestrates the full ETL pipeline.
"""
import os
import sys
import logging
from datetime import date
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd

load_dotenv()
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL not set')

engine = sqlalchemy.create_engine(DATABASE_URL)

# Import scoring functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'score'))
from score_engine import (
    season_score, recent_score, matchup_score,
    statcast_score, park_score, weather_score,
    bullpen_score, total_score
)

def compute_aggregates_for_date(as_of_date=None):
    """Compute aggregates from raw data and insert scores."""
    if as_of_date is None:
        as_of_date = date.today()
    
    logging.info(f'Computing aggregates for {as_of_date}')
    
    # Query season stats to get all active players with HR data
    query = '''
        SELECT player_id, hr, r, rbi, h, plate_appearances, season
        FROM season_stats
        WHERE season = EXTRACT(YEAR FROM %s)::int
        ORDER BY hr DESC
    '''
    
    try:
        df_stats = pd.read_sql_query(query, engine, params=(as_of_date,))
    except Exception as e:
        logging.error(f'Error fetching season stats: {e}')
        return
    
    if df_stats.empty:
        logging.warning('No season stats found')
        return
    
    logging.info(f'Found {len(df_stats)} players with season stats')
    
    # Compute scores for each player
    scores_data = []
    for idx, row in df_stats.iterrows():
        player_id = row['player_id']
        pa = row['plate_appearances'] or 1
        hr = row['hr'] or 0
        
        # Calculate component scores
        s_score = season_score(hr / pa if pa > 0 else 0)
        r_score = recent_score(0.05, 15)  # Placeholder: would need recent PA data
        m_score = matchup_score(1.2, 4.2, 0.8)  # Placeholder matchup data
        stat_score = statcast_score(3.5, 35.0, 0.340)  # Placeholder
        p_score = park_score(1.02)  # Placeholder
        w_score = weather_score(0.3)  # Placeholder
        b_score = bullpen_score(1.1)  # Placeholder
        
        components = {
            'season_score': s_score,
            'recent_score': r_score,
            'matchup_score': m_score,
            'statcast_score': stat_score,
            'park_score': p_score,
            'weather_score': w_score,
            'bullpen_score': b_score,
        }
        t_score = total_score(components)
        
        scores_data.append({
            'player_id': player_id,
            'as_of': as_of_date,
            'season_score': s_score,
            'recent_score': r_score,
            'matchup_score': m_score,
            'statcast_score': stat_score,
            'park_score': p_score,
            'weather_score': w_score,
            'bullpen_score': b_score,
            'total_score': t_score,
        })
    
    if not scores_data:
        logging.warning('No scores calculated')
        return
    
    # Insert into scores table
    df_scores = pd.DataFrame(scores_data)
    df_scores.to_sql('scores', engine, if_exists='append', index=False)
    logging.info(f'Inserted {len(df_scores)} scores')

if __name__ == '__main__':
    compute_aggregates_for_date()
