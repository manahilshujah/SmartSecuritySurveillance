import sqlite3
import os

DATABASE_NAME = "database/surveillance.db"

# Create database folder if it doesn't exist
os.makedirs("database", exist_ok=True)


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
        image TEXT,
        video TEXT
    )
    """)

    connection.commit()
    connection.close()


def insert_detection(date, time, event, people, confidence, image, video):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO detections
    (date, time, event, people, confidence, image, video)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (date, time, event, people, confidence, image, video))

    connection.commit()
    connection.close()