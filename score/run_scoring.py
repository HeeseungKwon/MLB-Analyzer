"""Run the scoring pipeline and insert scores into the database."""
import os
from datetime import date
from dotenv import load_dotenv
import sqlalchemy
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise RuntimeError('Set DATABASE_URL in environment or .env')

engine = sqlalchemy.create_engine(DATABASE_URL)

from score_engine import (
    season_score, recent_score, matchup_score,
    statcast_score, park_score, weather_score,
    bullpen_score, total_score
)

def run_scoring(as_of_date=None):
    """Calculate scores for all players and insert into scores table."""
    if as_of_date is None:
        as_of_date = date.today()
    
    logging.info(f'Calculating scores for {as_of_date}')
    
    # For now, create dummy scores for testing
    with engine.connect() as conn:
        # Insert sample scores
        dummy_scores = [
            (1, as_of_date, 10.5, 20.3, 5.0, 12.1, 3.5, 2.1, 1.8, 55.3),
            (2, as_of_date, 8.2, 15.1, 3.5, 9.8, 2.1, 1.5, 2.2, 42.4),
            (3, as_of_date, 12.1, 25.5, 7.2, 14.3, 4.2, 3.1, 2.5, 69.0),
        ]
        
        for player_id, as_of, s_score, r_score, m_score, stat_score, p_score, w_score, b_score, t_score in dummy_scores:
            query = '''
                INSERT INTO scores (player_id, as_of, season_score, recent_score, matchup_score, statcast_score, park_score, weather_score, bullpen_score, total_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            conn.execute(sqlalchemy.text(query), {
                'player_id': player_id,
                'as_of': as_of,
                'season_score': s_score,
                'recent_score': r_score,
                'matchup_score': m_score,
                'statcast_score': stat_score,
                'park_score': p_score,
                'weather_score': w_score,
                'bullpen_score': b_score,
                'total_score': t_score,
            })
        conn.commit()
    
    logging.info('Scoring complete!')

if __name__ == '__main__':
    run_scoring()
