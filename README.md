# 🎙️ AI Voice Assistant (Self-Upgrading)

A powerful voice assistant built with Python that can recognize speech, respond with natural voice, perform smart tasks like checking the weather, playing music, sending emails, taking screenshots, and even **upgrade its own code** using AI models like Gemini or ChatGPT!

---

## 🚀 Features

- ✅ Voice-activated using a customizable **wake word** (default: `assistant`)
- 🗣️ Natural speech recognition and text-to-speech
- 🔍 Wikipedia search and summary
- 🌤️ Real-time weather info (via OpenWeather API)
- 📰 Latest news headlines (via NewsAPI)
- 📧 Send emails securely
- 🎵 Play music from your system
- 🖼️ Take screenshots and save to desktop
- 💻 System info retrieval
- 🧠 Smart chatbot fallback responses
- 🧩 Install Python packages on the go via voice
- 🔄 **Self-upgrades its own code** with Gemini/ChatGPT suggestions
- 🔒 Error-handled and logs all events

---

## 📂 Project Structure

```
bash
.
├── assistant.py              # Main voice assistant logic
├── requirements.txt          # All Python dependencies
├── README.md                 # This file
├── email_credentials.json    # (Ignored) Secure email config
├── upgrade_versions/         # Stores upgraded versions
├── .gitignore                # Exclude sensitive or temp files
🧪 How to Run
```

Install dependencies:
```
pip install -r requirements.txt
```

##Add your API keys:

Replace placeholders like YOUR_NEWS_API_KEY and YOUR_WEATHER_API_KEY

Or use a .env file with environment variables

Run the assistant:

python genpy.py
🔐 Environment & Security
Ensure these files are kept secure and ignored in Git:

email_credentials.json (Gmail login)

.env (optional secure config file)

Use .gitignore to avoid exposing private data.
