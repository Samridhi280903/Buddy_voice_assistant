import speech_recognition as sr
import pywhatkit
import pyjokes
import requests
import datetime
import os
import openai
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "New Delhi")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

notes = []  # Stores notes in memory
reminders = []  # Stores reminders in memory
user_name = ""  # To store user's name

openai.api_key = OPENAI_API_KEY

def speak(text):
    print(f"Assistant: {text}")
    tts = gTTS(text=text, lang='en')
    tts.save("./sounds/output.mp3")
    sound = AudioSegment.from_mp3("./sounds/output.mp3")
    sound.export("./sounds/output.wav", format="wav")
    play(AudioSegment.from_wav("./sounds/output.wav"))

def get_audio() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!.....")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError as e:
        speak(f"Could not request results; {e}")
        return ""

def get_weather():
    if not API_KEY:
        speak("API key for weather is missing.")
        return
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    try:
        reaction = requests.get(url)
        data = reaction.json()
        if data.get("cod") != 200:
            speak("Failed to retrieve weather information.")
            return
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        speak(f"Currently in {CITY}, it's {weather} with a temperature of {temperature} degrees Celsius.")
    except requests.RequestException:
        speak("Sorry, I couldn't fetch the weather details right now.")

def tell_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    speak(f"The current time is {current_time}")

def set_reminder():
    speak("What should I remind you about?")
    reminder = get_audio()
    if reminder:
        reminders.append(reminder)
        speak(f"Reminder noted: {reminder}")

def take_note():
    speak("What would you like to note down?")
    note = get_audio()
    if note:
        notes.append(note)
        speak("Note saved.")

def read_notes():
    if notes:
        speak("Here are your saved notes:")
        for note in notes:
            speak(note)
    else:
        speak("You have no saved notes.")

def read_reminders():
    if reminders:
        speak("Here are your reminders:")
        for item in reminders:
            speak(item)
    else:
        speak("You have no reminders.")

def get_news():
    speak("Here are the top news headlines today.")
    news_items = [
        "India launches new satellite for weather tracking.",
        "Major update released for Android devices.",
        "Scientists discover water traces on Mars.",
        "Local elections set to begin next week."
    ]
    for item in news_items:
        speak(item)

def ask_llm(question):
    if not OPENAI_API_KEY:
        speak("Sorry, the AI feature is not available because the API key is missing.")
        return
    try:
        reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful personal assistant."},
                {"role": "user", "content": question}
            ]
        )
        reply = reply['choices'][0]['message']['content'].strip()
        speak(reply)
    except openai.error.OpenAIError as e:
        speak("Sorry, I couldn't get a response from AI.")

# Initial greeting and asking for username
speak("Hey there! I am your Buddy. What should I call you?")
user_name = get_audio()
if user_name:
    speak(f"Hello {user_name}! How are you today?")
    response = get_audio().lower()
    if "fine" in response or "good" in response:
        speak("That's great to hear! I'm always here and ready to help you with whatever you need.")

while True:
    user_query = get_audio().lower()

    if not user_query:
        continue

    if "stop" in user_query or "exit" in user_query or "goodbye" in user_query:
        speak("Goodbye! Have a great day!")
        break

    elif "youtube" in user_query:
        speak("Okay, I will bring that up on YouTube for you")
        pywhatkit.playonyt(user_query)

    elif "joke" in user_query:
        joke = pyjokes.get_joke()
        speak(joke)

    elif "weather" in user_query or "temperature" in user_query:
        get_weather()

    elif "time" in user_query:
        tell_time()

    elif "reminder" in user_query and ("read" in user_query or "show" in user_query):
        read_reminders()

    elif "reminder" in user_query:
        set_reminder()

    elif "note" in user_query and ("read" in user_query or "show" in user_query):
        read_notes()

    elif "note" in user_query:
        take_note()

    elif "news" in user_query:
        get_news()

    else:
        ask_llm(user_query)
