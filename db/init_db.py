import psycopg2
from psycopg2 import sql
import os
import time

def init_db():
    """Initialize the database and create the scores table."""
    
    # Get database connection details from environment or use defaults
    db_config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "database": os.getenv("POSTGRES_DB", "mlb"),
        "user": os.getenv("POSTGRES_USER", "mlb"),
        "password": os.getenv("POSTGRES_PASSWORD", "mlbpassword"),
        "port": os.getenv("POSTGRES_PORT", "5432")
    }
    
    # Retry logic for database connection
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Connecting to database at {db_config['host']}:{db_config['port']}...")
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            print("✓ Connected to database")
            break
        except psycopg2.OperationalError as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"✗ Connection failed: {e}")
                print(f"  Retrying in 2 seconds... ({retry_count}/{max_retries})")
                time.sleep(2)
            else:
                print(f"✗ Failed to connect after {max_retries} attempts")
                raise
    
    # Create the scores table
    create_scores_table = """
    CREATE TABLE IF NOT EXISTS scores (
        as_of DATE NOT NULL,
        player_id INT NOT NULL,
        total_score FLOAT,
        season_score FLOAT,
        recent_score FLOAT,
        matchup_score FLOAT,
        statcast_score FLOAT,
        park_score FLOAT,
        weather_score FLOAT,
        bullpen_score FLOAT,
        PRIMARY KEY (as_of, player_id)
    );
    """
    
    try:
        cursor.execute(create_scores_table)
        conn.commit()
        print("✓ Created 'scores' table successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"✗ Error creating table: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        init_db()
        print("\n✓ Database initialization complete!")
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        exit(1)
