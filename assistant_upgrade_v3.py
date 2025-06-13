import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import random
import json
import requests
import re
import subprocess
import wolframalpha
import geocoder

# --- Gemini Integration ---
import google.generativeai as genai

API_KEY = "GEMINI_API_KEY"  # <-- Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

# --- Initialization ---
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)
recognizer = sr.Recognizer()

# Wolfram Alpha Client (replace with your API key)
try:
    wolfram_client = wolframalpha.Client("API_KEY")  # <-- Replace with your Wolfram Alpha API key
except Exception as e:
    wolfram_client = None
    print(f"Wolfram Alpha initialization failed: {e}")
    print("Wolfram Alpha functionality will be disabled.")

EMAIL_CONFIG_FILE = "email_config.json"

def load_email_config(filename):
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print(f"Error: {filename} not found.  Please create it with your email credentials.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}.  Please check the file.")
        return None

email_config = load_email_config(EMAIL_CONFIG_FILE)

def speak(audio):
    print(f"Assistant: {audio}")
    engine.say(audio)
    engine.runAndWait()

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning! sir")
    elif 12 <= hour < 18:
        speak("Good Afternoon! sir")
    else:
        speak("Good Evening! sir")
    speak("jarvis here!. How may I help you?")

def take_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.pause_threshold = 1
            recognizer.energy_threshold = 400
            audio = recognizer.listen(source)
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-us')
        print(f"User: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand. Could you please repeat?")
        return "None"
    except sr.RequestError as e:
        speak(f"Sorry, there was an error connecting to the Google Speech Recognition service: {e}")
        return "None"
    except Exception as e:
        speak(f"An unexpected error occurred during speech recognition: {e}")
        return "None"

def send_email(to, content):
    if email_config is None:
        speak("Email configuration is missing.  Please set up email_config.json.")
        return
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_config['email'], email_config['password'])
        server.sendmail(email_config['email'], to, content)
        server.close()
        speak("Email has been sent!")
    except Exception as e:
        print(f"Email sending failed: {e}")
        speak(f"Sorry, I was unable to send the email. Error: {e}")

def get_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            return g.latlng
        else:
            speak("Could not determine your location.")
            return None
    except Exception as e:
        print(f"Error getting location: {e}")
        speak("An error occurred while trying to determine your location.")
        return None

# --- Main Program ---

if __name__ == "__main__":
    wish_me()
    while True:
        query = take_command()

        if query == "None" or not query.strip():
            continue

        # --- NLP Command Handling ---

        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia:")
                speak(results)
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find that on Wikipedia.")
            except wikipedia.exceptions.DisambiguationError as e:
                speak(f"There are multiple results for that query. Please be more specific. Options include: {e.options}")
            except Exception as e:
                speak(f"An error occurred while searching Wikipedia: {e}")

        elif 'open youtube' in query:
            speak("Opening YouTube...")
            webbrowser.open("https://www.youtube.com")

        elif 'open google' in query:
            speak("Opening Google...")
            webbrowser.open("https://www.google.com")

        elif 'open stackoverflow' in query:
            speak("Opening Stack Overflow...")
            webbrowser.open("https://stackoverflow.com")

        elif 'play music' in query or 'play song' in query:
            music_dir = 'C:\\Users\\YourUserName\\Music'
            try:
                songs = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f))]
                if songs:
                    song = random.choice(songs)
                    os.startfile(os.path.join(music_dir, song))
                    speak(f"Playing {song}")
                else:
                    speak("No songs found in the specified directory.")
            except FileNotFoundError:
                speak("Music directory not found. Please update the directory path in the code.")
            except Exception as e:
                speak(f"An error occurred while playing music: {e}")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {strTime}")

        elif 'open code' in query:
            codePath = "C:\\Users\\YourUserName\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            try:
                os.startfile(codePath)
                speak("Opening Visual Studio Code")
            except FileNotFoundError:
                speak("Visual Studio Code not found. Please update the path in the code.")
            except Exception as e:
                speak(f"An error occurred while opening VS Code: {e}")

        elif 'send email' in query:
            if email_config is None:
                speak("Email configuration is missing. Please set up email_config.json.")
                continue
            try:
                speak("To whom do you want to send the email?")
                to = take_command()
                if "@" not in to:
                    speak("That doesn't seem like a valid email address. Please try again.")
                    continue
                speak("What should I say?")
                content = take_command()
                send_email(to, content)
            except Exception as e:
                speak(f"An error occurred while sending the email: {e}")

        elif 'search' in query:
            query = query.replace("search", "")
            try:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                speak(f"Searching Google for {query}")
            except Exception as e:
                speak(f"An error occurred during the search: {e}")

        elif 'weather' in query:
            try:
                api_key = "WEATHER_API_KEY"  # <-- Replace with your OpenWeatherMap API key
                base_url = "http://api.openweathermap.org/data/2.5/weather?"
                speak("Tell me the city name")
                city_name = take_command()
                complete_url = base_url + "appid=" + api_key + "&q=" + city_name
                response = requests.get(complete_url)
                x = response.json()
                if x["cod"] != "404":
                    y = x["main"]
                    current_temperature = y["temp"]
                    current_humidity = y["humidity"]
                    z = x["weather"]
                    weather_description = z[0]["description"]
                    temperature_celsius = current_temperature - 273.15
                    speak(f"The temperature in {city_name} is {temperature_celsius:.2f} degrees Celsius. The humidity is {current_humidity} percent, and the weather is {weather_description}")
                else:
                    speak("City not found")
            except Exception as e:
                speak(f"An error occurred while getting the weather: {e}")

        elif 'news' in query:
            try:
                api_key = "NEW_API_KEY"  # <-- Replace with your News API key
                url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
                response = requests.get(url)
                news_json = response.json()
                if news_json["status"] == "ok":
                    articles = news_json["articles"]
                    speak("Here are the top news headlines:")
                    for i, article in enumerate(articles[:5]):
                        speak(f"Headline {i+1}: {article['title']}")
                else:
                    speak("Could not retrieve news headlines.")
            except Exception as e:
                speak(f"An error occurred while getting news: {e}")

        elif 'tell me a joke' in query:
            try:
                response = requests.get("https://official-joke-api.appspot.com/random_joke")
                joke_json = response.json()
                speak(joke_json['setup'])
                speak(joke_json['punchline'])
            except Exception as e:
                speak(f"An error occurred while getting a joke: {e}")

        elif 'what is your location' in query:
            location = get_location()
            if location:
                speak(f"Your approximate location is: Latitude {location[0]}, Longitude {location[1]}")
            else:
                speak("I was unable to determine your location.")

        elif 'calculate' in query or 'what is' in query:
            if wolfram_client:
                try:
                    result = wolfram_client.query(query)
                    answer = next(result.results).text
                    speak(f"The answer is {answer}")
                except StopIteration:
                    speak("Sorry, I couldn't find an answer to that question.")
                except Exception as e:
                    speak(f"An error occurred while using Wolfram Alpha: {e}")
            else:
                speak("Wolfram Alpha is not configured. Please provide a valid API key.")

        elif 'system info' in query or 'computer specs' in query:
            try:
                import platform
                speak("Gathering system information...")
                system_info = platform.uname()
                speak(f"System: {system_info.system}")
                speak(f"Node Name: {system_info.node}")
                speak(f"Release: {system_info.release}")
                speak(f"Version: {system_info.version}")
                speak(f"Machine: {system_info.machine}")
                speak(f"Processor: {system_info.processor}")
            except Exception as e:
                speak(f"Could not retrieve system information: {e}")

        elif 'launch application' in query:
            app_name = query.replace('launch application', '').strip()
            try:
                subprocess.Popen([app_name])
                speak(f"Launching {app_name}")
            except FileNotFoundError:
                speak(f"Application '{app_name}' not found.  Make sure it's in your system's PATH or provide the full path.")
            except Exception as e:
                speak(f"Could not launch application: {e}")

        elif 'exit' in query or 'quit' in query or 'stop' in query:
            speak("Okay, goodbye!")
            break

        else:
            # --- Gemini fallback for general conversation ---
            try:
                response = chat.send_message(query)
                gemini_reply = response.text.strip()
                speak(gemini_reply)
            except Exception as e:
                speak("Sorry, I couldn't process that with Gemini.")
