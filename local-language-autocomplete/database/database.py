
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "autocomplete.db"

SAMPLE_WORDS = [
    ("ਪੰਜਾਬ", 100),
    ("ਪੰਜਾਬੀ", 90),
    ("ਪੰਜਾਬੀਅਤ", 40),
    ("ਪਿਆਰ", 80),
    ("ਪਿਤਾ", 35),
    ("ਪਿੰਡ", 70),
    ("ਪਾਣੀ", 75),
    ("ਪੜ੍ਹਾਈ", 65),
    ("ਪੁਸਤਕ", 30),
    ("ਪਰਿਵਾਰ", 60),
    ("ਪ੍ਰਕਾਸ਼", 25),
    ("ਕਿਤਾਬ", 85),
    ("ਕਿਸਾਨ", 70),
    ("ਕੰਮ", 90),
    ("ਕੁਦਰਤ", 45),
    ("ਘਰ", 100),
    ("ਗੁਰੂ", 80),
    ("ਗੁਰਦੁਆਰਾ", 75),
    ("ਸਕੂਲ", 90),
    ("ਸਿੱਖਿਆ", 85),
    ("ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ", 100),
    ("ਸੁੰਦਰ", 60),
    ("ਸਮਾਂ", 70),
    ("ਦੋਸਤ", 85),
    ("ਦਿਲ", 80),
    ("ਮਾਂ", 100),
    ("ਮਿਹਨਤ", 65),
    ("ਮੁਸਕਾਨ", 50),
    ("ਰੱਬ", 70),
    ("ਰਸਤਾ", 55),
]


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS words (
                word TEXT PRIMARY KEY,
                frequency INTEGER NOT NULL DEFAULT 1
                    CHECK (frequency >= 0)
            )
        """)

        connection.executemany("""
            INSERT OR IGNORE INTO words (word, frequency)
            VALUES (?, ?)
        """, SAMPLE_WORDS)


def get_all_words():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT word, frequency
            FROM words
        """).fetchall()

    return [
        (row["word"], row["frequency"])
        for row in rows
    ]


def increase_frequency(word):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE words
            SET frequency = frequency + 1
            WHERE word = ?
        """, (word,))

        return cursor.rowcount > 0


def add_word(word):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO words (word, frequency)
            VALUES (?, 1)
            ON CONFLICT(word)
            DO UPDATE SET frequency = frequency + 1
        """, (word,))


def get_word_count():
    with get_connection() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM words"
        ).fetchone()[0]
