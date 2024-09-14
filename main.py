import speech_recognition as sr
import pyttsx3
import datetime
import requests
import random
import wikipedia
import os
import webbrowser
import time
import re

# Initialize the speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # You can change the index for different voices

# Function to make the assistant speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech using the microphone
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        try:
            print("Recognizing...")
            command = r.recognize_google(audio)
            print(f"User said: {command}\n")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return "None"
        except sr.RequestError:
            print("Sorry, there's an issue with the service.")
            return "None"

# Function to listen for activation word ("Jonah")
def listen_for_activation():
    while True:
        print("Waiting for activation word...")
        command = listen()
        if "jonah" in command:
            speak("Yes?")
            return True  # Activation word detected

# Function to handle math operations
def calculate(expression):
    try:
        # Remove non-math words like "what is", "calculate", etc.
        expression = re.sub(r'[^\d+\-*/().]', '', expression)

        # Replace words with operators
        expression = expression.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
        
        # Evaluate the expression
        result = eval(expression)
        speak(f"The result of {expression} is {result}.")
    except Exception as e:
        speak("Sorry, I couldn't calculate that.")
        print(e)

# Function to handle math queries more flexibly
def detect_math_operation(command):
    math_keywords = ["plus", "minus", "times", "divided by", "+", "-", "*", "/"]
    for keyword in math_keywords:
        if keyword in command:
            return True
    return False

# Function to tell the current time
def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current_time}")

# Function to get weather info (using OpenWeatherMap API)
def get_weather(city):
    api_key = "youropenweatherapikey"  # Replace with your API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(base_url)
        data = response.json()
        
        if data["cod"] == 200:
            weather = data['weather'][0]['description']
            temperature = data['main']['temp']
            city_name = data['name']
            speak(f"The weather in {city_name} is {weather} with a temperature of {temperature}°C.")
        else:
            speak(f"Sorry, I couldn't fetch the weather for {city}.")
    except:
        speak("Sorry, there was a problem connecting to the weather service.")

# Function to get the latest news (using NewsAPI)
def get_news():
    api_key = "yournewsapikey"  # Replace with your NewsAPI key
    base_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    
    try:
        response = requests.get(base_url)
        data = response.json()
        if data["status"] == "ok":
            articles = data["articles"][:5]  # Get top 5 headlines
            for i, article in enumerate(articles, 1):
                speak(f"News {i}: {article['title']}")
        else:
            speak("Sorry, I couldn't fetch the news.")
    except:
        speak("Sorry, there was a problem connecting to the news service.")

# Function to set a reminder (with a timer)
def set_reminder(duration, task):
    speak(f"Setting a reminder for {task} in {duration} seconds.")
    time.sleep(duration)
    speak(f"Reminder: It's time to {task}.")

# Function to play music from a folder
def play_music():
    music_dir = "C:\\path\\to\\your\\music\\folder"  # Replace with your music directory
    songs = os.listdir(music_dir)
    if songs:
        os.startfile(os.path.join(music_dir, songs[0]))  # Plays the first song in the folder
        speak(f"Playing {songs[0]}")
    else:
        speak("I couldn't find any music in the folder.")

# Function to perform a Google search
def google_search(query):
    speak(f"Searching for {query} on Google.")
    webbrowser.open(f"https://www.google.com/search?q={query}")

# Function to perform a Wikipedia search
def wikipedia_search(query):
    speak(f"Searching for {query} on Wikipedia.")
    try:
        summary = wikipedia.summary(query, sentences=2)
        speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        speak("There are multiple results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find anything on Wikipedia.")

# Main function to handle commands after the activation word "Jonah" is spoken
def take_command():
    last_active_time = None  # Track the last time Jonah was active
    active_duration = 30  # Jonah stays active for 30 seconds

    while True:
        # Check if Jonah should listen for the activation word or if he is still within the active window
        if not last_active_time or (time.time() - last_active_time > active_duration):
            if listen_for_activation():
                last_active_time = time.time()
        else:
            command = listen()

            # If no command is understood (returns "None"), silently ignore
            if command == "none":
                continue

            # Update last active time with each understood command
            last_active_time = time.time()

            # Time command
            if "time" in command:
                tell_time()
            # Weather command
            elif "weather" in command:
                speak("Which city?")
                city = listen()
                if city != "None":
                    get_weather(city)
            # Reminder command
            elif "reminder" in command:
                speak("What should I remind you about?")
                task = listen()
                speak("In how many seconds?")
                duration = int(listen())  # Assume user says number in seconds
                set_reminder(duration, task)
            # Music command
            elif "play music" in command:
                play_music()
            # News command
            elif "news" in command:
                get_news()
            # Google search command
            elif "google" in command:
                speak("What do you want to search for?")
                query = listen()
                google_search(query)
            # Wikipedia command
            elif "wikipedia" in command:
                speak("What would you like to know?")
                query = listen()
                wikipedia_search(query)
            # Calculation command (detect math operation)
            elif detect_math_operation(command):
                calculate(command)
            # Exit or stop command
            elif "exit" in command or "stop" in command:
                speak("Goodbye!")
                break
            else:
                speak("Sorry, I don't understand that command yet.")

# Run the virtual assistant
if __name__ == "__main__":
    speak("Hello! Call me by saying Jonah to ask for assistance.")
    take_command()
