import sqlite3
from typing import List, Tuple

class VocabularyDB:
    def __init__(self, db_name: str = "vocabulary.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    level TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    audio_path TEXT
                )
            ''')
            conn.commit()

    def add_word(self, word: str, translation: str, level: str, topic: str, audio_path: str, lesson: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vocabulary (word, translation, level, topic, audio_path, lesson)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (word, translation, level, topic, audio_path, lesson))
            conn.commit()

    def get_topic_words(self, level: str, topic: str, lesson: str, limit: int = 5) -> List[Tuple]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT word, translation, audio_path 
                FROM vocabulary 
                WHERE level = ? AND topic = ? AND lesson = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (level, topic, lesson, limit))
            return cursor.fetchall()

    def get_next_lesson(self, level: str, topic: str, sent_lessons: list) -> str | None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT lesson 
                FROM vocabulary 
                WHERE level = ? AND topic = ? AND lesson NOT IN (?)
            ''', (level, topic, ','.join(sent_lessons)))
            lessons = cursor.fetchall()
            return lessons[0][0] if lessons else None  # Return the first lesson not sent 