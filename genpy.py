import google.generativeai as genai
import os
import speech_recognition as sr
import pyttsx3
import subprocess
import sys
import re

# Configuration
API_KEY = "GEMINI_API_KEY"  # Replace with your actual API key
BASE_FILENAME = "assistant_upgrade"
VERSION_PREFIX = "v"
FILE_EXTENSION = ".py"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

recognizer = sr.Recognizer()
engine = pyttsx3.init()
history = []
MAX_HISTORY = 10
exit_phrases = [
    "exit", "quit", "goodbye", "bye", "see you", "i'm done",
    "stop now", "enough", "i have to go", "talk later", "ok exit"
]

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_voice_input():
    with sr.Microphone() as source:
        print("Listening... (say 'upgrade yourself' or 'review code')")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You (voice): {user_input}")
            return user_input
        except:
            return None

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

# 🔁 Main loop
while True:
    user_input = get_voice_input()
    if not user_input:
        user_input = input("You (type): ")
    if is_exit_intent(user_input):
        print("Exiting chat.")
        speak("Goodbye. Chat closed.")
        break
    if user_input.lower() == "show history":
        print_history(history)
        speak("Here is your chat history.")
        continue
    if is_upgrade_intent(user_input):
        suggest_code_upgrade(history)
        continue
    if is_review_intent(user_input):
        review_code_file()
        continue
    if is_restart_intent(user_input):
        restart_with_upgrade()
        break

    context = build_context(history)
    prompt = f"{context}\nUser: {user_input}\nAI:"
    response = chat.send_message(prompt)
    ai_response = response.text.strip()
    print(f"AI: {ai_response}")
    speak(ai_response)
    history.append({"user": user_input, "ai": ai_response})
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
