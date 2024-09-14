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
import threading
from playsound import playsound

# Initialize the speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

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

# Convert number words to digits
def word_to_number(word):
    word_to_num_map = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
        "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
        "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20
    }
    return word_to_num_map.get(word.lower(), None)

# Extract the first number from a command
def extract_number(command):
    words = command.split()
    for word in words:
        if word.isdigit():  # Check if the word is a digit
            return int(word)
        elif word_to_number(word) is not None:  # Check if it's a number word
            return word_to_number(word)
    return None

# Function to handle math operations
def calculate(expression):
    try:
        expression = re.sub(r'[^\d+\-*/().]', '', expression)
        expression = expression.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
        result = eval(expression)
        speak(f"The result of {expression} is {result}.")
    except Exception as e:
        speak("Sorry, I couldn't calculate that.")
        print(e)

# Function to detect math operations
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

# Function to tell the current date
def tell_date():
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {current_date}")

# Function to get weather info (using OpenWeatherMap API)
def get_weather(city):
    api_key = "89724d8fea32b2c6b1570a57f4b993a9"
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

# Function to get news (using NewsAPI)
def get_news():
    api_key = "b7e50c3e7bc54f71a8b5969f17655587"
    base_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(base_url)
        data = response.json()
        if data["status"] == "ok":
            articles = data["articles"][:5]
            for i, article in enumerate(articles, 1):
                speak(f"News {i}: {article['title']}")
        else:
            speak("Sorry, I couldn't fetch the news.")
    except:
        speak("Sorry, there was a problem connecting to the news service.")

# Function to tell jokes
def tell_joke():
    jokes = [
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "What do you call fake spaghetti? An impasta!",
        "Why don’t some couples go to the gym? Because some relationships don’t work out."
    ]
    speak(random.choice(jokes))

# Function to play an alarm sound and announce that the timer is done
def timer_finished():
    speak("Time is up!")
    playsound('alarm.mp3')  # Play alarm sound from the file (replace with actual path)

# Function to set a timer with optional input extraction
def set_timer(command=None):
    if command:
        seconds = extract_number(command)
        if seconds:
            speak(f"Timer set for {seconds} seconds.")
            timer_thread = threading.Thread(target=lambda: (time.sleep(seconds), timer_finished()))
            timer_thread.start()
        else:
            speak("Sorry, I couldn't understand the time duration.")
    else:
        while True:
            speak("For how many seconds?")
            response = listen()
            seconds = extract_number(response)
            if seconds:
                speak(f"Timer set for {seconds} seconds.")
                timer_thread = threading.Thread(target=lambda: (time.sleep(seconds), timer_finished()))
                timer_thread.start()
                break
            else:
                speak("I didn't catch that. Please say the number of seconds clearly.")

# Function to play music from a folder
def play_music():
    music_dir = "C:\\path\\to\\your\\music\\folder"
    songs = os.listdir(music_dir)
    if songs:
        os.startfile(os.path.join(music_dir, songs[0]))
        speak(f"Playing {songs[0]}")
    else:
        speak("I couldn't find any music in the folder.")

# Function to open an application
def open_application(app_name):
    if "notepad" in app_name:
        os.system("start notepad.exe")
        speak("Opening Notepad")
    elif "calculator" in app_name:
        os.system("start calc.exe")
        speak("Opening Calculator")
    else:
        speak(f"Sorry, I can't open {app_name} right now.")

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

# Main function to handle commands after activation word
def take_command():
    last_active_time = None
    active_duration = 30  # Jonah stays active for 30 seconds

    while True:
        if not last_active_time or (time.time() - last_active_time > active_duration):
            if listen_for_activation():
                last_active_time = time.time()
        else:
            command = listen()

            if command == "none":
                continue

            last_active_time = time.time()

            if "set a timer" in command:
                set_timer(command)
            elif "time" in command:
                tell_time()
            elif "date" in command:
                tell_date()
            elif "weather" in command:
                city = re.search(r'weather in (\w+)', command)
                if city:
                    get_weather(city.group(1))
                else:
                    speak("Which city?")
                    city = listen()
                    get_weather(city)
            elif "reminder" in command:
                speak("What should I remind you about?")
                task = listen()
                speak("In how many seconds?")
                duration = extract_number(listen())
                set_reminder(duration, task)
            elif "play music" in command:
                play_music()
            elif "news" in command:
                get_news()
            elif "joke" in command:
                tell_joke()
            elif "google" in command:
                query = re.search(r'google (.+)', command)
                if query:
                    google_search(query.group(1))
                else:
                    speak("What do you want to search for?")
                    google_search(listen())
            elif "wikipedia" in command:
                query = re.search(r'wikipedia (.+)', command)
                if query:
                    wikipedia_search(query.group(1))
                else:
                    speak("What would you like to know?")
                    wikipedia_search(listen())
            elif "open" in command:
                app_name = re.search(r'open (.+)', command)
                if app_name:
                    open_application(app_name.group(1))
                else:
                    speak("Which application should I open?")
                    open_application(listen())
            elif detect_math_operation(command):
                calculate(command)
            elif "exit" in command or "stop" in command:
                speak("Goodbye!")
                break
            else:
                speak("Sorry, I don't understand that command yet.")

# Function to listen for activation word ("Jonah")
def listen_for_activation():
    while True:
        print("Waiting for activation word...")
        command = listen()
        if "jonah" in command:
            speak("Yes?")
            return True  # Activation word detected

# Run the virtual assistant
if __name__ == "__main__":
    speak("Hello! Call me by saying Jonah to ask for assistance.")
    take_command()
