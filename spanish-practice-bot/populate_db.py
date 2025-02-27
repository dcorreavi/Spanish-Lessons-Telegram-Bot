from database import VocabularyDB
from audio_utils import generate_audio

def populate_travel_vocabulary():
    db = VocabularyDB()
    
    # Example vocabulary for A1 level, Travel topic
    a1_travel_vocab = [
         ("aeropuerto", "аэропорт", "lesson_2"),
        ("avión", "самолет", "lesson_2"),
        ("maleta", "чемодан", "lesson_2"),
        ("billete", "билет", "lesson_2"),
        ("salida", "выход", "lesson_2"),
        ("estación de tren", "железнодорожный вокзал", "lesson_3"),
        ("tren", "поезд", "lesson_3"),
        ("autobús", "автобус", "lesson_3"),
        ("taxi", "такси", "lesson_3"),
        ("destino", "пункт назначения", "lesson_3"),
        ("excursión", "экскурсия", "lesson_4"),
        ("guía turístico", "гид", "lesson_4"),
        ("turista", "турист", "lesson_4"),
        ("museo", "музей", "lesson_4"),
        ("monumento", "памятник", "lesson_4"),
        ("plaza", "площадь", "lesson_5"),
        ("mercado", "рынок", "lesson_5"),
        ("restaurante", "ресторан", "lesson_5"),
        ("comida típica", "традиционная еда", "lesson_5"),
        ("fotografía", "фотография", "lesson_5"),
        # Add more words as needed
    ]
    
    for word, translation, lesson in a1_travel_vocab:
        audio_path = generate_audio(word)
        db.add_word(word, translation, "a1", "topic_travel", audio_path, lesson)

if __name__ == "__main__":
    populate_travel_vocabulary() 