import streamlit as st
import speech_recognition as sr
import string
import wave
import io
from difflib import SequenceMatcher

st.set_page_config(
    page_title="AI Oral Reading Assessment Tool",
    page_icon="📘",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background-color: #cfe8cf;
}

h1, h2, h3 {
    color: #0b3d0b;
}

p, label, div {
    color: #123d12;
}

textarea, input {
    background-color: #f3fff3 !important;
    color: #123d12 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input {
    background-color: #f3fff3 !important;
    color: #123d12 !important;
}

.stTextArea textarea {
    background-color: #f3fff3 !important;
    color: #123d12 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #f3fff3 !important;
    color: #123d12 !important;
}

.stButton > button {
    background-color: #2e7d32;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
}

.stButton > button:hover {
    background-color: #1b5e20;
    color: white;
}

div[data-testid="metric-container"] {
    background-color: #f3fff3;
    border: 1px solid #9ccc9c;
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


def clean_text(text):
    text = text.lower()
    return text.translate(str.maketrans("", "", string.punctuation)).strip()


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def analyze_words(target_words, spoken_words):
    correct_count = 0
    missed_words = []
    substituted_words = []
    likely_mispronounced = []

    max_len = max(len(target_words), len(spoken_words))

    for i in range(max_len):
        target = target_words[i] if i < len(target_words) else None
        spoken = spoken_words[i] if i < len(spoken_words) else None

        if target is None and spoken is not None:
            substituted_words.append(f"(extra word: {spoken})")
            continue

        if target is not None and spoken is None:
            missed_words.append(target)
            continue

        if target == spoken:
            correct_count += 1
        else:
            score = similarity(target, spoken)
            if score >= 0.6:
                likely_mispronounced.append(f"{target} → {spoken}")
            else:
                substituted_words.append(f"{target} → {spoken}")

    return correct_count, missed_words, substituted_words, likely_mispronounced


def get_wav_duration(uploaded_audio):
    audio_bytes = uploaded_audio.getvalue()
    with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    return duration, audio_bytes


def assess_audio_bytes(passage, audio_bytes, reading_time):
    recognizer = sr.Recognizer()

    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio_data = recognizer.record(source)

    spoken_text = recognizer.recognize_google(audio_data)

    target_words = clean_text(passage).split()
    spoken_words = clean_text(spoken_text).split()

    correct_count, missed_words, substituted_words, likely_mispronounced = analyze_words(
        target_words, spoken_words
    )

    total_words = len(target_words)
    accuracy = (correct_count / total_words) * 100 if total_words > 0 else 0
    words_per_minute = (len(spoken_words) / reading_time) * 60 if reading_time > 0 else 0

    if accuracy >= 95 and words_per_minute >= 120:
        level = "Advanced"
    elif accuracy >= 85 and words_per_minute >= 100:
        level = "Proficient"
    elif accuracy >= 70 and words_per_minute >= 80:
        level = "Developing"
    else:
        level = "Beginning"

    return {
        "spoken_text": spoken_text,
        "correct_count": correct_count,
        "total_words": total_words,
        "accuracy": accuracy,
        "reading_time": reading_time,
        "words_per_minute": words_per_minute,
        "missed_words": missed_words,
        "substituted_words": substituted_words,
        "likely_mispronounced": likely_mispronounced,
        "level": level,
    }


st.markdown("""
# 📘 AI Oral Reading Assessment Tool
### Senior High School Version

This AI-powered tool evaluates oral reading performance using speech recognition and reading analytics.
""")

st.divider()

with st.sidebar:
    st.header("⏱ Recording Guide")
    st.write("Use the microphone widget below to start and stop recording manually.")
    st.write("**Maximum recording time:** 2 minutes")
    st.write("Read clearly and stay close to the microphone.")
    st.write("After stopping the recording, click **Evaluate Recording**.")

student_name = st.text_input("Student Name")
grade_level = st.selectbox("Grade Level", ["Grade 11", "Grade 12"])

passage = st.text_area(
    "Reading Passage",
    """Education helps students develop knowledge, skills, and values that they can use in daily life.
It also prepares them to make wise decisions, solve problems, and contribute to their community.
Through reading and learning, students become more confident, responsible, and ready for the future.""",
    height=180
)

st.subheader("🎙 Record Oral Reading")
recorded_audio = st.audio_input("Click to record, then stop when done")

if recorded_audio is not None:
    try:
        duration, audio_bytes = get_wav_duration(recorded_audio)

        with st.sidebar:
            st.metric("Recorded Time", f"{duration:.2f} sec")

        st.audio(recorded_audio)

        if duration > 120:
            st.error("Recording is longer than 2 minutes. Please record again and keep it within the limit.")
        else:
            if st.button("✅ Evaluate Recording"):
                if not student_name.strip():
                    st.warning("Please enter the student's name first.")
                else:
                    try:
                        result = assess_audio_bytes(passage, audio_bytes, duration)

                        st.success("Assessment complete!")

                        st.subheader("Student Information")
                        st.write(f"**Name:** {student_name}")
                        st.write(f"**Grade Level:** {grade_level}")

                        st.subheader("Recognized Reading")
                        st.write(result["spoken_text"])

                        st.subheader("Assessment Results")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Accuracy", f"{result['accuracy']:.2f}%")
                        col2.metric("WPM", f"{result['words_per_minute']:.2f}")
                        col3.metric("Level", result["level"])

                        st.write(f"**Correct Words:** {result['correct_count']}/{result['total_words']}")
                        st.write(f"**Reading Time:** {result['reading_time']:.2f} seconds")

                        if result["missed_words"]:
                            st.write("**Missed Words:** " + ", ".join(result["missed_words"]))
                        else:
                            st.write("**Missed Words:** None")

                        if result["substituted_words"]:
                            st.write("**Substituted Words:** " + ", ".join(result["substituted_words"]))
                        else:
                            st.write("**Substituted Words:** None")

                        if result["likely_mispronounced"]:
                            st.write("**Likely Mispronounced Words:** " + ", ".join(result["likely_mispronounced"]))
                        else:
                            st.write("**Likely Mispronounced Words:** None")

                        st.subheader("Reading Interpretation")

                        if result["level"] == "Advanced":
                            st.success("The student demonstrates excellent reading fluency.")
                        elif result["level"] == "Proficient":
                            st.info("The student shows good reading ability with minor improvements needed.")
                        elif result["level"] == "Developing":
                            st.warning("The student needs more practice to improve reading fluency.")
                        else:
                            st.error("The student requires intensive reading intervention.")

                        st.caption("Note: Likely mispronounced words are estimated from recognized speech and are only approximate.")

                    except sr.UnknownValueError:
                        st.error("Sorry, the speech was not understood.")
                    except sr.RequestError:
                        st.error("Speech recognition service is unavailable.")
                    except Exception as e:
                        st.error(f"An error occurred during evaluation: {e}")

    except wave.Error:
        st.error("The recorded audio could not be processed. Please record again.")

st.divider()
st.caption("AI Oral Reading Assessment Tool | Developed for Senior High School Literacy Support")