import os
import re
import sys
import subprocess
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import random
import smtplib
import ssl
import requests
import json
import psutil
import time
import threading
import traceback

# --- Gemini Integration ---
import google.generativeai as genai

API_KEY = "GEMINI_API_KEY"  # Replace with your actual API key
BASE_FILENAME = "assistant_upgrade"
VERSION_PREFIX = "v"
FILE_EXTENSION = ".py"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

MAX_HISTORY = 10
history = []
exit_phrases = [
    "exit", "quit", "goodbye", "bye", "see you", "i'm done",
    "stop now", "enough", "i have to go", "talk later", "ok exit"
]

def build_context(history):
    return "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in history[-MAX_HISTORY:]])

def print_history(history):
    print("\n--- Chat History ---")
    for i, turn in enumerate(history[-MAX_HISTORY:], 1):
        print(f"{i}. You: {turn['user']}")
        print(f"   AI: {turn['ai']}")
    print("--------------------\n")

def is_exit_intent(text):
    text = text.lower()
    return any(phrase in text for phrase in exit_phrases)

def is_upgrade_intent(text):
    return "upgrade yourself" in text.lower() or "improve yourself" in text.lower()

def is_review_intent(text):
    return "review code" in text.lower() or "check your upgrade" in text.lower()

def is_restart_intent(text):
    return "restart with upgrade" in text.lower() or "run new version" in text.lower()

def get_next_version_filename(base_path="."):
    files = [f for f in os.listdir(base_path) if re.match(rf"{BASE_FILENAME}_{VERSION_PREFIX}\d+{FILE_EXTENSION}", f)]
    versions = [int(re.findall(rf"{VERSION_PREFIX}(\d+)", f)[0]) for f in files]
    next_version = max(versions) + 1 if versions else 1
    return f"{BASE_FILENAME}_{VERSION_PREFIX}{next_version}{FILE_EXTENSION}"

def suggest_code_upgrade(history):
    context = build_context(history)
    upgrade_prompt = (
        f"You are a Python voice chatbot assistant. Improve your code with features like better speech UX, "
        f"error handling, NLP commands, and code upgrading. Return only the full upgraded Python script.\n\n"
        f"Recent conversation:\n{context}"
    )
    print("🛠 Asking Gemini to upgrade the assistant...")
    response = model.generate_content(upgrade_prompt)

    if "```python" in response.text:
        code = response.text.split("```python")[1].split("```")[0].strip()
    else:
        code = response.text.strip()

    filename = get_next_version_filename()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n✅ Upgrade saved as: {filename}")
    speak(f"I have upgraded myself and saved version {filename}.")
    return filename

def review_code_file():
    files = sorted(
        [f for f in os.listdir() if re.match(rf"{BASE_FILENAME}_{VERSION_PREFIX}\d+{FILE_EXTENSION}", f)],
        key=lambda x: int(re.findall(rf"{VERSION_PREFIX}(\d+)", x)[0]),
        reverse=True
    )
    if not files:
        print("❌ No upgrade files to review.")
        speak("There are no upgraded files to review.")
        return

    with open(files[0], "r", encoding="utf-8") as f:
        code = f.read()

    review_prompt = (
        f"You're a Python expert. Review the following code and suggest improvements:\n\n{code}"
    )

    print("🔍 Asking Gemini to review the latest upgrade...")
    response = model.generate_content(review_prompt)
    print("\n📋 Review:\n")
    print(response.text)
    speak("Here's the review of the latest code version.")

def restart_with_upgrade():
    files = sorted(
        [f for f in os.listdir() if re.match(rf"{BASE_FILENAME}_{VERSION_PREFIX}\d+{FILE_EXTENSION}", f)],
        key=lambda x: int(re.findall(rf"{VERSION_PREFIX}(\d+)", x)[0]),
        reverse=True
    )
    if not files:
        speak("No upgraded file found to run.")
        return
    latest_file = files[0]
    speak(f"Restarting with version {latest_file}")
    print(f"🚀 Running: {latest_file}")
    subprocess.Popen([sys.executable, latest_file])
    sys.exit(0)

# --- Assistant Core ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)
recognizer = sr.Recognizer()

try:
    with open("knowledge_base.json", "r") as f:
        knowledge_base = json.load(f)
except FileNotFoundError:
    knowledge_base = {}
except json.JSONDecodeError:
    print("Error: Invalid JSON in knowledge_base.json.  Using empty knowledge base.")
    knowledge_base = {}

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-us')
            print(f"User: {query}\n")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you please repeat?")
            return ""
        except sr.RequestError as e:
            speak(f"Sorry, I'm having trouble connecting to the internet.  Error: {e}")
            return ""
        except sr.WaitTimeoutError:
            speak("Sorry, I didn't hear anything. Please try again.")
            return ""
        except Exception as e:
            speak(f"An unexpected error occurred during speech recognition: {e}")
            print(traceback.format_exc())
            return ""

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I am your virtual assistant. How can I help you today?")

def send_email(receiver_email, subject, message):
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, f"Subject: {subject}\n\n{message}")
        speak("Email sent successfully!")
    except Exception as e:
        speak(f"Sorry, I couldn't send the email. Error: {e}")
        print(traceback.format_exc())

def get_weather(city):
    api_key = "WEATHER_API_KEY"  # Replace with your actual OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    url = f"{base_url}?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["cod"] != "404":
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            speak(f"The weather in {city} is {weather_description} with a temperature of {temperature} degrees Celsius and humidity of {humidity} percent.")
        else:
            speak("Sorry, I couldn't find weather information for that city.")
    except requests.exceptions.RequestException as e:
        speak(f"Sorry, I encountered a network error while fetching weather data: {e}")
        print(traceback.format_exc())
    except (KeyError, IndexError) as e:
        speak(f"Sorry, I couldn't parse the weather data.  The API response may have changed. Error: {e}")
        print(traceback.format_exc())
    except Exception as e:
        speak(f"An unexpected error occurred while getting weather: {e}")
        print(traceback.format_exc())

def control_volume(action):
    try:
        if action == "increase":
            if sys.platform == "win32":
                os.system("nircmd.exe changesysvolume 6553")
            else:
                speak("Volume control is not fully supported on this platform yet.")
        elif action == "decrease":
            if sys.platform == "win32":
                os.system("nircmd.exe changesysvolume -6553")
            else:
                speak("Volume control is not fully supported on this platform yet.")
        elif action == "mute":
            if sys.platform == "win32":
                os.system("nircmd.exe mutesysvolume 1")
            else:
                speak("Volume control is not fully supported on this platform yet.")
        elif action == "unmute":
            if sys.platform == "win32":
                os.system("nircmd.exe mutesysvolume 0")
            else:
                speak("Volume control is not fully supported on this platform yet.")
        else:
            speak("I don't understand that volume command.")
    except FileNotFoundError:
        speak("Error: nircmd.exe not found. Please install it and add it to your system's PATH.")
    except Exception as e:
        speak(f"An error occurred while controlling the volume: {e}")
        print(traceback.format_exc())

def get_system_stats():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory()
        speak(f"CPU usage is at {cpu_usage} percent, and memory usage is at {memory_usage} percent")
    except Exception as e:
        speak(f"An error occurred while getting system stats: {e}")
        print(traceback.format_exc())

def search_knowledge_base(query):
    for key, value in knowledge_base.items():
        if key in query:
            return value
    return None

def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

def background_task():
    while True:
        now = datetime.datetime.now()
        if now.hour == 7 and now.minute == 0:
            speak("Good morning! This is your daily reminder.")
        time.sleep(60)

def get_voice_input():
    with sr.Microphone() as source:
        print("Listening... (say 'upgrade yourself' or 'review code')")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            user_input = recognizer.recognize_google(audio)
            print(f"You (voice): {user_input}")
            return user_input
        except:
            return None

def run_assistant():
    wish_me()
    background_thread = threading.Thread(target=background_task, daemon=True)
    background_thread.start()

    global history
    while True:
        # Try voice input first, fallback to text
        query = get_voice_input()
        if not query:
            query = input("You (type): ")
        if not query:
            continue

        # Gemini triggers
        if is_exit_intent(query):
            print("Exiting chat.")
            speak("Goodbye. Chat closed.")
            break
        if query.lower() == "show history":
            print_history(history)
            speak("Here is your chat history.")
            continue
        if is_upgrade_intent(query):
            suggest_code_upgrade(history)
            continue
        if is_review_intent(query):
            review_code_file()
            continue
        if is_restart_intent(query):
            restart_with_upgrade()
            break

        # Add to chat context for Gemini
        context = build_context(history)
        prompt = f"{context}\nUser: {query}\nAI:"
        # If not a Gemini command, process as normal assistant
        # Save Gemini's response for context, but only use for chat, not for commands
        ai_response = ""
        # --- NLP Command Handling ---
        if "wikipedia" in query:
            try:
                speak("Searching Wikipedia...")
                q = query.replace("wikipedia", "")
                results = wikipedia.summary(q, sentences=2)
                speak("According to Wikipedia...")
                ai_response = results
                speak(results)
            except wikipedia.exceptions.PageError:
                ai_response = "Sorry, I couldn't find that on Wikipedia."
                speak(ai_response)
            except wikipedia.exceptions.DisambiguationError as e:
                ai_response = f"Wikipedia returned multiple results for that query.  Please be more specific.  Here are some options: {e.options}"
                speak(ai_response)
            except Exception as e:
                ai_response = f"An error occurred while searching Wikipedia: {e}"
                speak(ai_response)
                print(traceback.format_exc())

        elif "open youtube" in query:
            ai_response = "Opening YouTube..."
            speak(ai_response)
            webbrowser.open("https://www.youtube.com")

        elif "open google" in query:
            ai_response = "Opening Google..."
            speak(ai_response)
            webbrowser.open("https://www.google.com")

        elif "open stackoverflow" in query:
            ai_response = "Opening Stack Overflow..."
            speak(ai_response)
            webbrowser.open("https://stackoverflow.com")

        elif "play music" in query or "play song" in query:
            music_dir = 'C:\\Music'
            try:
                songs = os.listdir(music_dir)
                if songs:
                    random_song = random.choice(songs)
                    ai_response = f"Playing: {random_song}"
                    speak(ai_response)
                    os.startfile(os.path.join(music_dir, random_song))
                else:
                    ai_response = "Sorry, your music directory is empty."
                    speak(ai_response)
            except FileNotFoundError:
                ai_response = "Sorry, I couldn't find the music directory. Please update the path."
                speak(ai_response)
            except Exception as e:
                ai_response = f"An error occurred while playing music: {e}"
                speak(ai_response)
                print(traceback.format_exc())

        elif "the time" in query:
            str_time = datetime.datetime.now().strftime("%I:%M %p")
            ai_response = f"The time is {str_time}"
            speak(ai_response)

        elif "the date" in query:
            str_date = datetime.datetime.now().strftime("%B %d, %Y")
            ai_response = f"Today is {str_date}"
            speak(ai_response)

        elif "open code" in query:
            code_path = "C:\\VSCode\\Code.exe"
            try:
                os.startfile(code_path)
                ai_response = "Opening Visual Studio Code..."
                speak(ai_response)
            except FileNotFoundError:
                ai_response = "Sorry, I couldn't find the VS Code executable. Please update the path."
                speak(ai_response)
            except Exception as e:
                ai_response = f"An error occurred while opening VS Code: {e}"
                speak(ai_response)
                print(traceback.format_exc())

        elif "send email" in query:
            try:
                speak("To whom should I send the email?")
                receiver = listen()
                if not receiver:
                    continue
                receiver_email = receiver.replace("at", "@").replace("dot", ".")
                speak("What is the subject of the email?")
                subject = listen()
                if not subject:
                    continue
                speak("What is the message you want to send?")
                message = listen()
                if not message:
                    continue
                send_email(receiver_email, subject, message)
                ai_response = "Email sent."
            except Exception as e:
                ai_response = f"An error occurred while sending the email: {e}"
                speak(ai_response)
                print(traceback.format_exc())

        elif "weather in" in query:
            city = query.replace("weather in", "").strip()
            get_weather(city)
            ai_response = f"Weather for {city} requested."

        elif "increase volume" in query:
            control_volume("increase")
            ai_response = "Increasing volume."

        elif "decrease volume" in query:
            control_volume("decrease")
            ai_response = "Decreasing volume."

        elif "mute volume" in query:
            control_volume("mute")
            ai_response = "Muting volume."

        elif "unmute volume" in query:
            control_volume("unmute")
            ai_response = "Unmuting volume."

        elif "system stats" in query or "system status" in query:
            get_system_stats()
            ai_response = "System stats requested."

        elif "search" in query:
            try:
                q = query.replace("search", "").strip()
                ai_response = f"Searching the web for {q}..."
                speak(ai_response)
                webbrowser.open(f"https://www.google.com/search?q={q}")
            except Exception as e:
                ai_response = f"An error occurred during the web search: {e}"
                speak(ai_response)
                print(traceback.format_exc())

        elif "what is" in query or "who is" in query:
            answer = search_knowledge_base(query)
            if answer:
                ai_response = answer
                speak(answer)
            else:
                try:
                    speak("Searching Wikipedia for an answer...")
                    results = wikipedia.summary(query, sentences=2)
                    ai_response = results
                    speak(results)
                except wikipedia.exceptions.PageError:
                    ai_response = "Sorry, I couldn't find an answer to that question."
                    speak(ai_response)
                except wikipedia.exceptions.DisambiguationError as e:
                    ai_response = f"Wikipedia returned multiple results for that query.  Please be more specific.  Here are some options: {e.options}"
                    speak(ai_response)
                except Exception as e:
                    ai_response = f"An error occurred while searching: {e}"
                    speak(ai_response)
                    print(traceback.format_exc())

        elif "check internet" in query or "internet connection" in query:
            if check_internet_connection():
                ai_response = "The internet connection is working."
                speak(ai_response)
            else:
                ai_response = "There is no internet connection."
                speak(ai_response)

        elif "exit" in query or "quit" in query or "stop" in query or "goodbye" in query:
            ai_response = "Goodbye! Have a great day."
            speak(ai_response)
            break

        else:
            # Fallback to Gemini chat for general conversation
            response = chat.send_message(prompt)
            ai_response = response.text.strip()
            print(f"AI: {ai_response}")
            speak(ai_response)

        # Save to history for Gemini context
        history.append({"user": query, "ai": ai_response})
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

if __name__ == "__main__":
    try:
        run_assistant()
    except Exception as e:
        print(f"A fatal error occurred: {e}")
        print(traceback.format_exc())
        input("Press Enter to exit...")