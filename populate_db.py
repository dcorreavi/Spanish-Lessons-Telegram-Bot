from database import VocabularyDB
from audio_utils import generate_audio

def populate_travel_vocabulary():
    db = VocabularyDB()
    
    # Example vocabulary for A1 level, Travel topic
    from database import VocabularyDB
from audio_utils import generate_audio

def populate_travel_vocabulary():
    db = VocabularyDB()
    
    # Vocabulary for B1 level, Travel topic
    a1_hobbies_vocab = [
            # Lesson 1
            ("leer", "читать", "lesson_1"),
            ("correr", "бегать", "lesson_1"),
            ("nadar", "плавать", "lesson_1"),
            ("escuchar música", "слушать музыку", "lesson_1"),
            ("ver películas", "смотреть фильмы", "lesson_1"),
            
            # Lesson 2
            ("cantar", "петь", "lesson_2"),
            ("dibujar", "рисовать", "lesson_2"),
            ("bailar", "танцевать", "lesson_2"),
            ("hacer ejercicio", "заниматься спортом", "lesson_2"),
            ("ir al cine", "идти в кино", "lesson_2"),
            
            # Lesson 3
            ("jugar", "играть", "lesson_3"),
            ("cocinar", "готовить", "lesson_3"),
            ("viajar", "путешествовать", "lesson_3"),
            ("hacer senderismo", "заниматься пешими прогулками", "lesson_3"),
            ("fotografía", "фотография", "lesson_3"),
            
            # Lesson 4
            ("pasear", "гулять", "lesson_4"),
            ("ir a conciertos", "ходить на концерты", "lesson_4"),
            ("tejer", "вязать", "lesson_4"),
            ("jugar al fútbol", "играть в футбол", "lesson_4"),
            ("coleccionar", "коллекционировать", "lesson_4"),
            
            # Lesson 5
            ("escribir", "писать", "lesson_5"),
            ("hacer jardinería", "заниматься садоводством", "lesson_5"),
            ("practicar yoga", "заниматься йогой", "lesson_5"),
            ("ver televisión", "смотреть телевизор", "lesson_5"),
            ("pintar", "красить", "lesson_5"),
        ]
    
    for word, translation, lesson in a1_hobbies_vocab:
        audio_path = generate_audio(word)
        db.add_word(word, translation, "a1", "topic_hobbies", audio_path, lesson)

if __name__ == "__main__":
    populate_travel_vocabulary() 