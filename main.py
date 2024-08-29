import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
import random
import openai

# Initialize the OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Dictionary of Bollywood songs with their YouTube URLs
bollywood_songs = {
    "apna bana lai": "https://youtu.be/ElZfdU54Cp8",
    "kesariya": "https://youtu.be/BddP6PYo2gs",
    "aayi nai": "https://youtu.be/nFgsBxw-zWQ",
    "raataan lambiyan": "https://www.youtube.com/watch?v=pyG2aehb3Ws",
    "tum hi ho": "https://www.youtube.com/watch?v=Umqb9KENgmk",
    "nashe si chadh gayi": "https://www.youtube.com/watch?v=Wd2B8OAotU8",
    "tera ban jaunga": "https://www.youtube.com/watch?v=Q2WJscCOVag",
    "pal pal dil ke paas": "https://www.youtube.com/watch?v=H3RzzJGKmZ4",
    "gerua": "https://www.youtube.com/watch?v=AEIVhBS6baE",
    "agar tum saath ho": "https://www.youtube.com/watch?v=sK7riqg2mr4"
}

def speak(text):
    """Speak the given text using the initialized TTS engine."""
    engine.say(text)
    engine.runAndWait()

def record_audio(duration=5, fs=44100):
    """Record audio for a specified duration and at a specified sample rate."""
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete.")
    return np.array(recording, dtype=np.int16)

def get_news():
    """Fetches top news headlines using the News API."""
    api_key = '26cf1031a3e04976a24b243e80c25cfa'  # Your News API key
    endpoint = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(endpoint)
    news_data = response.json()
    if news_data["status"] == "ok":
        headlines = [article['title'] for article in news_data['articles'][:5]]  # Get top 5 headlines
        news_headlines = '... '.join(headlines)  # Create a single string with all headlines
        return news_headlines
    else:
        return "Failed to fetch news, please check the API key and connection."

def speak_news():
    """Speaks the latest news headlines."""
    news = get_news()
    speak("Here are the top news headlines: " + news)

def get_openai_response(prompt):
    """Fetch a response from OpenAI's API based on the given prompt."""
    try:
        print(f"Sending prompt to OpenAI: {prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are General Assistant Jarvis, skilled in general tasks like Alexa."},
                {"role": "user", "content": prompt}
            ]
        )
        print("OpenAI response received")
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "Sorry, I couldn't process your request."

def listen_for_wake_word():
    """Continuously listen for the wake word 'Jarvis' and respond."""
    print("Listening for the wake word...")
    while True:
        audio_data = record_audio()
        if audio_data is None:
            continue
        audio = sr.AudioData(audio_data.tobytes(), 44100, 2)
        try:
            speech_as_text = recognizer.recognize_google(audio)
            print(f"Recognized words: {speech_as_text}")
            if "jarvis" in speech_as_text.lower():
                print("Wake word 'Jarvis' heard.")
                speak("Yeah")
                listen_for_commands()
        except sr.UnknownValueError:
            print("Could not understand audio, waiting for wake word again...")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def listen_for_commands():
    """Listen for further commands after the wake word is recognized."""
    print("Listening for commands...")
    audio_data = record_audio()
    if audio_data is None:
        return
    audio = sr.AudioData(audio_data.tobytes(), 44100, 2)
    try:
        command = recognizer.recognize_google(audio)
        print(f"Command received: {command}")
        process_command(command)
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Please repeat your command.")
    except sr.RequestError as e:
        print(f"Error during command processing; {e}")

def process_command(command):
    """Process the recognized command by opening specified websites, playing music, or using OpenAI."""
    command = command.lower()
    print(f"Processing command: {command}")
    
    if "open google" in command:
        webbrowser.open('https://www.google.com')
        print("Opening Google...")
        speak("Opening Google...")
    elif command.startswith("play"):
        song_name = command.split("play", 1)[1].strip()
        song_url = bollywood_songs.get(song_name.lower())
        if song_url:
            webbrowser.open(song_url)
            print(f"Playing {song_name}...")
            speak(f"Playing {song_name}...")
        else:
            random_song = random.choice(list(bollywood_songs.items()))
            webbrowser.open(random_song[1])
            print(f"Song '{song_name}' not found. Playing random song: {random_song[0]}")
            speak(f"Song '{song_name}' not found. Playing random song: {random_song[0]}")
    elif "news" in command:
        speak_news()
    else:
        # Use OpenAI to generate a response for any other commands
        openai_response = get_openai_response(command)
        print(f"OpenAI response: {openai_response}")
        speak(openai_response)

if __name__ == "__main__":
    speak("Initializing Jarvis...")
    listen_for_wake_word()
