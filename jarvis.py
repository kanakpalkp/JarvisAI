import datetime
import json
import platform
import subprocess
import webbrowser
import urllib.request
import urllib.error

import speech_recognition as sr


# ---------------- CONFIGURATION ----------------

MODEL = "llama3.2:1b"
OLLAMA_URL = "http://localhost:11434/api/chat"

recognizer = sr.Recognizer()

conversation = [
    {
        "role": "system",
        "content": (
            "Tum Jarvis ho, ek friendly personal AI assistant. "
            "User se natural Hinglish mein baat karo. "
            "Hindi ko Roman Hindi mein likho. "
            "Answers simple, useful aur clear rakho. "
            "Programming questions mein examples do. "
            "Agar kisi baat ka answer nahi pata, toh honestly batao."
        )
    }
]


# ---------------- SPEAK ----------------

def speak(text):
    print(f"\nJARVIS: {text}")
    subprocess.run(["say", text], check=False)


# ---------------- LISTEN ----------------

def listen():
    try:
        with sr.Microphone(device_index=2) as source:
            print("\n🎤 JARVIS: Haan, bolo...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        print("JARVIS: Tumhari baat samajh raha hoon...")

        command = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )

        print(f"\nYOU: {command}")

        return command.lower().strip()

    except sr.WaitTimeoutError:
        print("JARVIS: Awaaz nahi aayi. Dobara bolo.")

    except sr.UnknownValueError:
        speak("Maaf karna, main samajh nahi paaya.")

    except sr.RequestError:
        speak("Speech recognition service connect nahi ho rahi.")

    except OSError as error:
        print("Microphone error:", error)

    return ""


# ---------------- LOCAL AI ----------------

def ask_ai(question):
    global conversation

    conversation.append({
        "role": "user",
        "content": question
    })

    payload = {
        "model": MODEL,
        "messages": conversation,
        "stream": False
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result["message"]["content"].strip()

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        # Keep recent conversation to limit memory usage.
        if len(conversation) > 11:
            conversation = [conversation[0]] + conversation[-10:]

        speak(answer)

    except urllib.error.URLError:
        # Remove the unanswered question from conversation history.
        conversation.pop()

        speak(
            "Local AI se connection nahi ho raha. "
            "Check karo ki Ollama chal raha hai."
        )

    except Exception as error:
        conversation.pop()
        print("AI error:", error)
        speak("Maaf karna, AI response mein problem aa gayi.")


# ---------------- COMMANDS ----------------

def handle_command(command):

    if any(word in command for word in [
        "band ho ja", "band karo", "exit", "quit",
        "बंद करो", "बंद हो जा"
    ]):
        speak("Theek hai. Jarvis band ho raha hai.")
        return False

    elif any(word in command for word in [
        "time", "टाइम", "समय", "kitne baje"
    ]):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"Abhi time hai {current_time}.")

    elif any(word in command for word in [
        "date", "तारीख", "aaj ki date", "आज की तारीख"
    ]):
        today = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Aaj ki date hai {today}.")

    elif "youtube" in command or "यूट्यूब" in command:
        speak("YouTube khol raha hoon.")
        webbrowser.open("https://www.youtube.com")

    elif "google" in command or "गूगल" in command:
        speak("Google khol raha hoon.")
        webbrowser.open("https://www.google.com")

    elif "vscode" in command or "visual studio code" in command:
        speak("Visual Studio Code khol raha hoon.")
        subprocess.Popen(["open", "-a", "Visual Studio Code"])

    elif any(word in command for word in [
        "system info", "system information", "सिस्टम की जानकारी"
    ]):
        info = platform.machine()
        speak(f"Tumhara system architecture {info} hai.")

    else:
        # Unknown commands go to the local AI.
        ask_ai(command)

    return True


# ---------------- MAIN PROGRAM ----------------

def main():
    speak("Namaste! Main Jarvis hoon.")
    speak("Mera local AI brain ready hai. Bolo, kya poochna hai?")

    while True:
        command = listen()

        if command and not handle_command(command):
            break


if __name__ == "__main__":
    main()