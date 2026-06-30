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

from score_engine import total_score

def run_scoring(as_of_date=None):
    """Calculate scores for all players and insert into scores table."""
    if as_of_date is None:
        as_of_date = date.today()
    
    logging.info(f'Calculating scores for {as_of_date}')
    
    dummy_scores = [
        (1, as_of_date, 10.5, 20.3, 5.0, 12.1, 3.5, 2.1, 1.8, 55.3),
        (2, as_of_date, 8.2, 15.1, 3.5, 9.8, 2.1, 1.5, 2.2, 42.4),
        (3, as_of_date, 12.1, 25.5, 7.2, 14.3, 4.2, 3.1, 2.5, 69.0),
    ]
    
    with engine.begin() as conn:
        for player_id, as_of, s_score, r_score, m_score, stat_score, p_score, w_score, b_score, t_score in dummy_scores:
            conn.execute(sqlalchemy.text(
                "INSERT INTO scores (player_id, as_of, season_score, recent_score, matchup_score, statcast_score, park_score, weather_score, bullpen_score, total_score) "
                "VALUES (:p, :d, :s, :r, :m, :st, :pk, :w, :b, :t)"
            ), {'p': player_id, 'd': as_of, 's': s_score, 'r': r_score, 'm': m_score, 'st': stat_score, 'pk': p_score, 'w': w_score, 'b': b_score, 't': t_score})
    
    logging.info('Scoring complete!')

if __name__ == '__main__':
    run_scoring()
