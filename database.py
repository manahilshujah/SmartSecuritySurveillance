import sqlite3

DATABASE_NAME = "database/surveillance.db"

def initialize_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT,
        event TEXT,
        people INTEGER,
        confidence REAL,
        image TEXT
    )
    """)

    connection.commit()
    connection.close()


def insert_detection(date, time, event, people, confidence, image):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO detections
    (date, time, event, people, confidence, image)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (date, time, event, people, confidence, image))

    connection.commit()
    connection.close()