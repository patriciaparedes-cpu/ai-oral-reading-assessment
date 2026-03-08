import speech_recognition as sr
import time
import string

passage = """
Education helps students develop knowledge, skills, and values that they can use in daily life.
It also prepares them to make wise decisions, solve problems, and contribute to their community.
Through reading and learning, students become more confident, responsible, and ready for the future.
"""

print("SENIOR HIGH SCHOOL ORAL READING ASSESSMENT")
print("Read this passage aloud:")
print(passage)

input("Press ENTER when you are ready to read...")

recognizer = sr.Recognizer()

def clean_text(text):
    text = text.lower()
    return text.translate(str.maketrans("", "", string.punctuation))

with sr.Microphone() as source:
    print("Listening...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    start_time = time.time()
    audio = recognizer.listen(source)
    end_time = time.time()

try:
    spoken_text = recognizer.recognize_google(audio)

    print("\nYou said:")
    print(spoken_text)

    target_words = clean_text(passage).split()
    spoken_words = clean_text(spoken_text).split()

    correct_count = 0
    missed_words = []

    for word in target_words:
        if word in spoken_words:
            correct_count += 1
        else:
            missed_words.append(word)

    total_words = len(target_words)
    accuracy = (correct_count / total_words) * 100

    reading_time = end_time - start_time
    words_per_minute = (len(spoken_words) / reading_time) * 60 if reading_time > 0 else 0

    print(f"\nCorrect words: {correct_count}/{total_words}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Reading time: {reading_time:.2f} seconds")
    print(f"Words per minute: {words_per_minute:.2f}")

    if missed_words:
        print("Missed words:", ", ".join(missed_words))
    else:
        print("Missed words: None")

    # Performance level
    if accuracy >= 95 and words_per_minute >= 120:
        level = "Advanced"
    elif accuracy >= 85 and words_per_minute >= 100:
        level = "Proficient"
    elif accuracy >= 70 and words_per_minute >= 80:
        level = "Developing"
    else:
        level = "Beginning"

    print(f"Performance Level: {level}")

except sr.UnknownValueError:
    print("Sorry, I could not understand the speech.")
except sr.RequestError:
    print("Could not request results from speech recognition service.")