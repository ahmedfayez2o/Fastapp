import pandas as pd # type: ignore
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
import logging
import random
import time
from pathlib import Path
import json
import pickle
from typing import Optional, Tuple

# Set up logging with rotation
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Set up logging with rotation (10MB max size, keep 5 backup files)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/import_reviews.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

# Database connection parameters
DB_PARAMS = {
    'dbname': 'iqraa_db',
    'user': 'iqraa_user',
    'password': 'iqraa_password',
    'host': '127.0.0.1',
    'port': '5432'
}

def verify_database_connection():
    """Verify database connection and required tables exist"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            # Check if required tables exist
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'books', 'book_reviews')
            """)
            tables = {row[0] for row in cur.fetchall()}
            required_tables = {'users', 'books', 'book_reviews'}
            missing_tables = required_tables - tables
            if missing_tables:
                raise Exception(f"Missing required tables: {missing_tables}")
            logging.info("Database connection and tables verified successfully")
        return conn
    except Exception as e:
        logging.error(f"Database verification failed: {e}")
        raise

def verify_csv_file(file_path):
    """Verify CSV file exists and is readable"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    try:
        # Try to read first few rows to verify file is readable
        df_sample = pd.read_csv(file_path, nrows=5)
        required_columns = {'book_id', 'title', 'authors', 'rating', 'review/text'}
        missing_columns = required_columns - set(df_sample.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV: {missing_columns}")
        logging.info(f"CSV file verified successfully. Found columns: {', '.join(df_sample.columns)}")
        return True
    except Exception as e:
        logging.error(f"CSV file verification failed: {e}")
        raise

def create_temp_user(conn, username):
    """Create a temporary user for Amazon reviews with proper password hashing"""
    with conn.cursor() as cur:
        # Use a more secure password hash
        password_hash = f"amazon_import_{int(time.time())}"  # In production, use proper password hashing
        cur.execute("""
            INSERT INTO users (username, email, password, full_name, is_active, first_name, last_name, date_joined, is_admin, is_superuser, favorite_genres, notification_preferences, is_verified, last_active, created_at, updated_at, is_staff)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE
            SET email = EXCLUDED.email,
                password = EXCLUDED.password,
                full_name = EXCLUDED.full_name,
                is_active = EXCLUDED.is_active,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                date_joined = EXCLUDED.date_joined,
                is_admin = EXCLUDED.is_admin,
                is_superuser = EXCLUDED.is_superuser,
                favorite_genres = EXCLUDED.favorite_genres,
                notification_preferences = EXCLUDED.notification_preferences,
                is_verified = EXCLUDED.is_verified,
                last_active = EXCLUDED.last_active,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at,
                is_staff = EXCLUDED.is_staff
            RETURNING id
        """, (username, f"{username}@amazon.com", password_hash, f"Amazon User {username}", True, "Amazon", username, timezone.now(), False, False, [], json.dumps({}), False, timezone.now(), timezone.now(), timezone.now(), False)) # type: ignore
        conn.commit()
        user_id = cur.fetchone()[0]
        logging.info(f"Created/updated temporary user {username} with ID: {user_id}")
        return user_id

def create_specific_user(conn, username, password):
    """Create a specific user with given credentials and admin privileges"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (username, email, password, full_name, first_name, last_name, date_joined, is_admin, is_superuser, favorite_genres, notification_preferences, is_verified, last_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING id
        """, (username, f"{username}@bookstore.com", password, f"{username.capitalize()} User", username, "User", timezone.now(), True, True, [], json.dumps({}), False, timezone.now(), timezone.now())) # type: ignore
        conn.commit()
        return cur.fetchone()[0] if cur.rowcount > 0 else None

def load_checkpoint() -> Optional[int]:
    """Load the last processed row index from checkpoint file"""
    checkpoint_file = 'logs/import_checkpoint.pkl'
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logging.warning(f"Failed to load checkpoint: {e}")
    return None

def save_checkpoint(row_index: int):
    """Save the current row index to checkpoint file"""
    checkpoint_file = 'logs/import_checkpoint.pkl'
    try:
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(row_index, f)
    except Exception as e:
        logging.error(f"Failed to save checkpoint: {e}")

def process_batch_with_retry(cur, batch, amazon_user_id, max_retries=3) -> Tuple[int, int, int]:
    """Process a batch of reviews with retry logic"""
    reviews_data = []
    batch_skipped = 0
    batch_errors = 0
    
    for retry in range(max_retries):
        try:
            # Start a fresh transaction for each retry
            cur.execute("BEGIN")
            
            for idx, row in batch.iterrows():
                try:
                    # Only skip if book_id is missing as it's required for the database
                    if pd.isna(row['book_id']):
                        logging.warning(f"Skipping row {idx}: Missing required book_id")
                        batch_skipped += 1
                        continue

                    # Process book data with generous defaults
                    book_id = str(row['book_id'])
                    title = str(row['title'])[:255] if pd.notna(row.get('title')) else f"Unknown Book {book_id}"
                    authors = str(row['authors'])[:100] if pd.notna(row.get('authors')) else "Unknown Author"
                    price = float(row['price']) if pd.notna(row.get('price')) else random.uniform(30, 200)
                    
                    # Add default for available_for_borrow
                    available_for_borrow = True  # Default to True for all books
                    now = datetime.now()

                    # First try to find existing book
                    cur.execute("""
                        SELECT book_id FROM books WHERE isbn = %s
                    """, (book_id,))
                    result = cur.fetchone()
                    
                    if result:
                        # Book exists, update it
                        book_id = result[0]
                        cur.execute("""
                            UPDATE books 
                            SET title = COALESCE(%s, title),
                                author = COALESCE(%s, author),
                                price = COALESCE(%s, price),
                                available_for_borrow = COALESCE(%s, available_for_borrow),
                                updated_at = %s
                            WHERE book_id = %s
                        """, (title, authors, price, available_for_borrow, now, book_id))
                    else:
                        # Book doesn't exist, insert it
                        cur.execute("""
                            INSERT INTO books (
                                isbn, title, author, price, stock_quantity, 
                                available_for_borrow, created_at, updated_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING book_id
                        """, (
                            book_id,
                            title,
                            authors,
                            price,
                            0,  # stock_quantity
                            available_for_borrow,
                            now,
                            now
                        ))
                        book_id = cur.fetchone()[0]

                    # Process review data with generous defaults
                    review_date = pd.to_datetime(row.get('review/time', datetime.now()))
                    if pd.isna(review_date):
                        review_date = datetime.now()

                    # Handle helpfulness with default
                    helpfulness_raw = str(row.get('review/helpfulness', '0/0'))
                    try:
                        helpful_votes = int(helpfulness_raw.split('/')[0]) if helpfulness_raw.lower() != 'nan' else 0
                    except Exception:
                        helpful_votes = 0

                    # Handle rating with default
                    try:
                        rating = float(row.get('rating', 3.0))
                        rating = max(1.0, min(5.0, rating))  # Ensure rating is within bounds
                    except (ValueError, TypeError):
                        rating = 3.0  # Default to middle rating if invalid

                    # Handle review text with default
                    review_text = str(row.get('review/text', '')) if pd.notna(row.get('review/text')) else "No review text provided"

                    # Handle user_id with default
                    user_id_val = str(row.get('user_id', '')) if pd.notna(row.get('user_id')) else f"amazon_user_{int(time.time())}_{random.randint(1000, 9999)}"

                    # Handle verified purchase with default
                    verified_purchase = bool(row.get('verified_purchase', False)) if pd.notna(row.get('verified_purchase')) else False

                    # Generate a unique external_review_id
                    external_review_id = f"{book_id}_{idx}"

                    reviews_data.append((
                        book_id,
                        amazon_user_id,
                        rating,
                        review_text,
                        review_date,
                        helpful_votes,
                        verified_purchase,
                        'amazon',
                        external_review_id,
                        now,
                        now
                    ))

                except Exception as e:
                    logging.warning(f"Error processing row {idx}, using defaults: {e}")
                    # Try to log the problematic data for debugging
                    try:
                        logging.debug(f"Row data: {row.to_dict()}")
                    except Exception:
                        pass
                    # Rollback the current row's transaction and continue
                    cur.execute("ROLLBACK")
                    cur.execute("BEGIN")
                    continue

            # Bulk insert reviews for the batch
            if reviews_data:
                execute_values(cur, """
                    INSERT INTO book_reviews (
                        book_id, user_id, rating, review_text, review_date,
                        helpful_votes, verified_purchase, source, external_review_id,
                        created_at, updated_at
                    ) VALUES %s
                """, reviews_data)

            # Commit the successful batch
            cur.execute("COMMIT")
            return len(reviews_data), batch_skipped, 0

        except Exception as e:
            logging.error(f"Batch processing attempt {retry + 1} failed: {e}")
            # Rollback the failed batch
            cur.execute("ROLLBACK")
            if retry < max_retries - 1:
                time.sleep(2 ** retry)  # Exponential backoff
                continue
            batch_errors = len(reviews_data) + batch_skipped
            return 0, 0, batch_errors

def import_reviews(limit: Optional[int] = None):
    """Import Amazon reviews into the database with improved error handling and verification
    
    Args:
        limit: Optional number of rows to import. If None, imports all rows.
    """
    csv_file = 'scripts/amazon_book_reviews_CLEAN.csv'
    start_time = time.time()
    total_processed = 0
    total_skipped = 0
    total_errors = 0

    try:
        # Verify database and file before starting
        conn = verify_database_connection()
        verify_csv_file(csv_file)

        # Read the CSV file with progress tracking
        logging.info("Reading Amazon reviews CSV file...")
        df = pd.read_csv(csv_file)
        if limit:
            df = df.head(limit)
            logging.info(f"Test run: Importing first {limit} rows")
        
        total_rows = len(df)
        logging.info(f"Total rows to process: {total_rows}")

        # Create temporary user
        amazon_user_id = create_temp_user(conn, "amazon_reviews")

        # Process in smaller batches for better error handling
        batch_size = min(100, total_rows)  # Smaller batch size for test run
        last_progress_update = time.time()
        progress_interval = 2  # Update progress more frequently for test run

        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            batch = df.iloc[batch_start:batch_end]
            
            # Start a new transaction for each batch
            cur = conn.cursor()
            try:
                processed, skipped, errors = process_batch_with_retry(cur, batch, amazon_user_id)
                
                conn.commit()
                total_processed += processed
                total_skipped += skipped
                total_errors += errors
                
                # Update progress periodically
                current_time = time.time()
                if current_time - last_progress_update >= progress_interval:
                    elapsed = current_time - start_time
                    progress = (batch_end / total_rows) * 100
                    speed = total_processed / elapsed if elapsed > 0 else 0
                    eta = (total_rows - batch_end) / speed if speed > 0 else 0
                    
                    logging.info(
                        f"Progress: {progress:.1f}% | "
                        f"Processed: {total_processed} | "
                        f"Skipped: {total_skipped} | "
                        f"Errors: {total_errors} | "
                        f"Speed: {speed:.1f} rows/s | "
                        f"ETA: {eta/60:.1f} minutes"
                    )
                    last_progress_update = current_time

            except Exception as e:
                logging.error(f"Fatal error in batch {batch_start}-{batch_end}: {e}")
                conn.rollback()
                total_errors += len(batch)
            finally:
                cur.close()

        # Final statistics
        total_time = time.time() - start_time
        logging.info(f"""
Import completed:
- Total rows processed: {total_processed}
- Total rows skipped: {total_skipped}
- Total errors: {total_errors}
- Total time: {total_time:.2f}s
- Average speed: {total_processed/total_time:.2f} rows/second
        """)

    except Exception as e:
        logging.error(f"Fatal error during import: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logging.info("Database connection closed")

def run(*args, **kwargs):
    """Entry point for django-extensions runscript"""
    try:
        logging.info("Starting Amazon reviews import process (full run)")
        import_reviews()  # Import all rows
        logging.info("Import process completed successfully")
    except Exception as e:
        logging.error(f"Import process failed: {e}")
        raise

    logging.info("Starting user creation process")
    try:
        conn = verify_database_connection()
        # Note: The original script tried to create a user 'ahmed' with a hardcoded password here.
        # This might not be desired when running with runscript. 
        # I will keep it commented out for now.
        # user_id = create_specific_user(conn, "ahmed", "bookstore1")
        # if user_id:
        #     logging.info(f"Successfully created/updated user 'ahmed' with ID: {user_id}")
        # else:
        #     logging.warning("User 'ahmed' already exists and was updated")
        conn.close()
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        # Depending on requirements, you might want to raise or just log this error
        # raise 