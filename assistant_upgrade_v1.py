import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import random
import smtplib
import json
import requests
import re
import subprocess
import sys
import time
import threading
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Use a female voice (index 1 may vary)
engine.setProperty('rate', 150)  # Adjust speech rate

# Initialize recognizer
r = sr.Recognizer()

# Global variables for state management
user_name = None  # Store user's name after introduction
wake_word = "assistant"  # Customizable wake word

# Helper Functions
def speak(text):
    """Speaks the given text."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error(f"Error during speech: {e}")
        print(f"Error during speech: {e}")  # Print to console as a fallback

def listen():
    """Listens for user input and returns the recognized text."""
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1  # Adjust for silence
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-us')
        print(f"User said: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        print("I didn't catch that. Could you please repeat?")
        speak("I didn't catch that. Could you please repeat?")  # Voice feedback
        return ""  # Return empty string if nothing is recognized
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        speak("I'm having trouble connecting to the internet. Please check your connection.")
        return ""  # Return empty string on error

def send_email(to, content):
    """Sends an email using Gmail."""
    # Sensitive information should be stored securely (e.g., environment variables)
    with open("email_credentials.json", "r") as f:  # Store email/password locally and securely. DO NOT COMMIT SECRETL!!!
        credentials = json.load(f)

    sender_email = credentials["email"]
    sender_password = credentials["password"]

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to, content)
        server.close()
        speak("Email has been sent!")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        speak("Sorry, I was unable to send the email.")

def get_news(num_articles=3):
    """Fetches and speaks the latest news headlines."""
    try:
        url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_NEWS_API_KEY"  # Replace with your News API key
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        news_json = response.json()

        articles = news_json.get("articles")
        if articles:
            speak("Here are the top news headlines:")
            for i, article in enumerate(articles[:num_articles]):
                title = article.get("title")
                description = article.get("description")
                speak(f"Headline {i+1}: {title}. {description if description else 'No further details available.'}")
        else:
            speak("I couldn't retrieve any news at the moment.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        speak("I encountered an error while fetching news. Please check your internet connection or API key.")
    except (KeyError, ValueError) as e:
        logging.error(f"Error parsing news data: {e}")
        speak("I encountered an error while parsing the news data. Please try again later.")

def play_music():
    """Plays a random music file from the music directory."""
    music_dir = 'C:\\Users\\YourUsername\\Music'  # Replace with your music directory
    try:
        songs = os.listdir(music_dir)
        if songs:
            random_song = random.choice(songs)
            os.startfile(os.path.join(music_dir, random_song))
            speak(f"Playing {random_song}")
        else:
            speak("There are no songs in the specified music directory.")
    except FileNotFoundError:
        speak("The music directory was not found. Please update the music directory path in the code.")
    except Exception as e:
        logging.error(f"Error playing music: {e}")
        speak("An error occurred while trying to play music.")

def open_website(url):
    """Opens the given URL in the default web browser."""
    try:
        webbrowser.open(url)
        speak(f"Opening {url}")
    except webbrowser.Error as e:
        logging.error(f"Error opening website {url}: {e}")
        speak(f"I couldn't open {url}.  Please check the URL.")
    except Exception as e:
        logging.error(f"Unexpected error opening website {url}: {e}")
        speak("An unexpected error occurred while trying to open the website.")

def get_weather(city):
    """Fetches and speaks the current weather for a given city."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_WEATHER_API_KEY&units=metric" # Replace with your Weather API key
        response = requests.get(url)
        response.raise_for_status() # Raise HTTPError for bad responses
        weather_data = response.json()

        if weather_data["cod"] == 200:
            temperature = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            description = weather_data["weather"][0]["description"]

            speak(f"The current weather in {city} is {description}, with a temperature of {temperature} degrees Celsius and humidity of {humidity} percent.")
        else:
            speak(f"I couldn't retrieve the weather for {city}.  Error code: {weather_data['cod']}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        speak("I encountered an error while fetching weather data. Please check your internet connection or API key.")
    except (KeyError, ValueError) as e:
        logging.error(f"Error parsing weather data: {e}")
        speak("I encountered an error while parsing the weather data.  Please try again later.")

def take_screenshot():
    """Takes a screenshot and saves it to the desktop."""
    try:
        import pyautogui
        now = datetime.datetime.now()
        filename = f"screenshot_{now.strftime('%Y-%m-%d_%H-%M-%S')}.png"
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        speak(f"Screenshot saved to {filepath}")
    except ImportError:
        speak("You need to install the pyautogui library.  Please say 'install pyautogui'.")
    except Exception as e:
        logging.error(f"Error taking screenshot: {e}")
        speak("An error occurred while taking the screenshot.")

def install_package(package_name):
  """Installs a Python package using pip."""
  try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    speak(f"Successfully installed {package_name}")
  except subprocess.CalledProcessError as e:
    logging.error(f"Error installing package {package_name}: {e}")
    speak(f"Failed to install {package_name}. Please check the package name or your internet connection.")

def chatbot_response(query):
    """Provides a default chatbot response when no specific command is matched."""
    responses = [
        "I'm still learning, can you be more specific?",
        "Could you please rephrase that?",
        "I'm not sure I understand.  How else can I help?",
        "Let me think about that...",
        "That's an interesting question."
    ]
    return random.choice(responses)

def get_time():
    """Tells the current time."""
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")  # Format as HH:MM AM/PM
    speak(f"The time is {current_time}")

def get_date():
    """Tells the current date."""
    today = datetime.date.today()
    speak(f"Today's date is {today.strftime('%A, %B %d, %Y')}") # Format example: Monday, July 24, 2023

def system_info():
    """Speaks the system's information"""
    try:
        import platform
        speak("Here is the system information:")
        speak(f"System: {platform.system()}")
        speak(f"Node Name: {platform.node()}")
        speak(f"Release: {platform.release()}")
        speak(f"Version: {platform.version()}")
        speak(f"Machine: {platform.machine()}")
        speak(f"Processor: {platform.processor()}")
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        speak("I'm sorry, I couldn't retrieve the system information.")

# Main Program Logic
def main():
    """Main function to handle user interaction."""
    global user_name, wake_word

    speak("Initializing...")
    speak(f"Hello, I am your assistant.  My wake word is '{wake_word}'.")

    while True:
        query = listen()

        if not query: # Skip if speech recognition failed
            continue

        if wake_word in query:
            query = query.replace(wake_word, "").strip() #remove wake word
            logging.info(f"Received command: {query}")

            try:
                if "hello" in query or "hi" in query:
                    if user_name:
                        speak(f"Hello {user_name}! How can I help you today?")
                    else:
                        speak("Hello! What is your name?")
                        name = listen()
                        if name:
                            user_name = name
                            speak(f"Nice to meet you, {user_name}! How can I help you today?")
                        else:
                            speak("Okay, hello! How can I help you today?")

                elif "how are you" in query:
                    speak("I am doing well, thank you for asking!")

                elif "what are you doing" in query:
                    speak("I am currently running on a computer server, waiting for your requests and trying my best to answer them. I don't experience the world in the same way humans do, so I don't 'do' things in the same way either. I'm essentially processing information and generating responses. Is there anything specific you'd like me to do or any information you'd like me to provide?")

                elif "time" in query:
                    get_time()

                elif "date" in query:
                    get_date()

                elif "wikipedia" in query:
                    speak("Searching Wikipedia...")
                    query = query.replace("wikipedia", "")
                    try:
                        results = wikipedia.summary(query, sentences=2)
                        speak("According to Wikipedia:")
                        speak(results)
                    except wikipedia.exceptions.PageError:
                        speak("I couldn't find that on Wikipedia.")
                    except wikipedia.exceptions.DisambiguationError as e:
                        speak(f"Wikipedia found several possible results. Could you be more specific? {e.options}")

                elif "open youtube" in query:
                    open_website("https://www.youtube.com")

                elif "open google" in query:
                    open_website("https://www.google.com")

                elif "search google for" in query:
                    search_term = query.replace("search google for", "").strip()
                    open_website(f"https://www.google.com/search?q={search_term}")

                elif "play music" in query:
                    play_music()

                elif "news" in query:
                    get_news()

                elif "weather" in query:
                    speak("For what city?")
                    city = listen()
                    if city:
                        get_weather(city)
                    else:
                        speak("I didn't hear the city name.  Please try again.")

                elif "send email" in query:
                    try:
                        speak("To whom should I send the email?")
                        to = listen()

                        if not re.match(r"[^@]+@[^@]+\.[^@]+", to):
                            speak("That doesn't seem like a valid email address. Please try again.")
                            continue

                        speak("What should I say?")
                        content = listen()
                        send_email(to, content)
                    except Exception as e:
                        logging.error(f"Error sending email: {e}")
                        speak("I'm sorry, I couldn't send the email.")

                elif "take a screenshot" in query:
                    take_screenshot()

                elif "install" in query:
                  package_name = query.replace("install", "").strip()
                  install_package(package_name)

                elif "system info" in query:
                    system_info()

                elif "change wake word to" in query:
                    new_wake_word = query.replace("change wake word to", "").strip()
                    wake_word = new_wake_word
                    speak(f"Okay, I have updated the wake word to '{wake_word}'.")

                elif "exit" in query or "quit" in query or "stop" in query:
                    speak("Goodbye!")
                    break

                else:
                    response = chatbot_response(query)
                    speak(response)

            except Exception as e:
                logging.error(f"An unexpected error occurred: {traceback.format_exc()}")
                speak("I encountered an unexpected error. Please check the logs for details.")

if __name__ == "__main__":
    main()