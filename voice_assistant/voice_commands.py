import pyautogui
import webbrowser
import os
import subprocess
import ctypes
import platform
import psutil
from datetime import datetime
import winshell
from win32com.client import Dispatch
import wikipedia
import requests
import screen_brightness_control as sbc
import cv2
import numpy as np
from plyer import notification
import speedtest
import threading
import time

# --- CONFIGURATION ---
# Add your API keys here
OPENWEATHERMAP_API_KEY = "7e6655d516cc0d5d24f0343a9cc8584b" # Your OpenWeatherMap key
NEWS_API_KEY = "557c58a57feb495aa23c551c96c7d77e"             # Your NewsAPI key

# Optional safety configs for PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


# --- CORE SPEAK FUNCTION ---
def speak(text):
    """
    Uses Windows PowerShell to speak text. This method is non-blocking and very reliable,
    avoiding the errors from other libraries in a web server environment.
    """
    try:
        # IMPORTANT: Escape single quotes for PowerShell
        safe_text = text.replace("'", "''")
        
        # Create the PowerShell command
        command = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{safe_text}\')"'
        
        # Run the command in a new process without showing a window
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error in speak function: {e}")

# --- COMMAND FUNCTIONS ---
# Each function performs an action and uses speak() for real-time feedback.

def open_notepad():
    try:
        speak("Opening Notepad")
        os.startfile('notepad.exe')
        return 'Opened Notepad'
    except Exception as e:
        speak("Sorry, I could not open Notepad.")
        return f'Error: {str(e)}'

def open_website(url):
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        speak(f"Opening {url}")
        webbrowser.open(url)
        return f'Opening website: {url}'
    except Exception as e:
        speak("Sorry, I could not open that website.")
        return f'Error: {str(e)}'

def open_youtube():
    return open_website('https://www.youtube.com')

def take_screenshot():
    try:
        speak("Taking a screenshot.")
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        full_path = os.path.join(desktop, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(full_path)
        speak("Screenshot saved to your desktop.")
        return f'Screenshot saved as {filename}'
    except Exception as e:
        speak("Sorry, I failed to take a screenshot.")
        return f'Error: {str(e)}'

def shutdown_system():
    speak("System will shutdown in 5 seconds. Goodbye Sir.")
    os.system('shutdown /s /t 5')
    return 'System shutdown initiated'

def restart_system():
    speak("System will restart in 5 seconds.")
    os.system('shutdown /r /t 5')
    return 'System restart initiated'

def lock_system():
    try:
        speak("Locking the system.")
        ctypes.windll.user32.LockWorkStation()
        return 'System locked'
    except Exception as e:
        speak("Sorry, I could not lock the system.")
        return f'Error: {str(e)}'

def get_system_info():
    try:
        mem = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)
        response_text = f"The current CPU usage is {cpu_usage} percent, and memory usage is at {mem.percent} percent."
        speak(response_text)
        return response_text
    except Exception as e:
        speak("Sorry, I could not retrieve system information.")
        return f'Error: {str(e)}'

def check_battery_status():
    try:
        battery = psutil.sensors_battery()
        if battery:
            status = "charging" if battery.power_plugged else "discharging"
            response_text = f"The battery is at {battery.percent} percent and is currently {status}."
            speak(response_text)
            return response_text
        else:
            speak("I could not find a battery in this system.")
            return "Battery info not available"
    except Exception as e:
        speak("Sorry, I could not check the battery status.")
        return f'Error: {str(e)}'

def search_wikipedia(query):
    try:
        speak(f"Searching Wikipedia for {query}.")
        summary = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia...")
        time.sleep(1) # Pause slightly before reading the summary
        speak(summary)
        return f'Wikipedia: {summary}'
    except wikipedia.exceptions.PageError:
        speak(f"Sorry, I could not find a Wikipedia page for {query}.")
        return f"Page for '{query}' not found."
    except wikipedia.exceptions.DisambiguationError:
        speak(f"Your query {query} is ambiguous. Please be more specific.")
        return f"'{query}' is ambiguous."
    except Exception as e:
        speak("Sorry, the Wikipedia search failed.")
        return f'Error: {str(e)}'

def get_weather(city):
    try:
        speak(f"Checking the weather in {city}.")
        url = f"http://api.openweathermap.org/data/2.5/weather?appid={OPENWEATHERMAP_API_KEY}&q={city}&units=metric"
        data = requests.get(url).json()
        
        if data["cod"] != "404":
            temp = round(data["main"]["temp"])
            desc = data["weather"][0]["description"]
            response_text = f"The current temperature in {city} is {temp} degrees Celsius, with {desc}."
            speak(response_text)
            return response_text
        else:
            speak(f"I'm sorry, I could not find the city {city}.")
            return "City not found"
    except Exception as e:
        speak("Sorry, the weather check failed.")
        return f'Error: {str(e)}'

def get_news():
    try:
        speak("Getting the latest headlines from India.")
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        news = requests.get(url).json()
        
        speak("Here are the top three headlines.")
        headlines = []
        for i, article in enumerate(news["articles"][:3]):
            headline = article['title']
            headlines.append(f"{i+1}. {headline}")
            speak(f"Headline {i+1}: {headline}")
            time.sleep(1) # Pause between headlines
        return "Top Headlines:\n" + "\n".join(headlines)
    except Exception as e:
        speak("Sorry, the news update failed.")
        return f'Error: {str(e)}'

def set_reminder(text, minutes):
    try:
        speak(f"Okay, I will remind you to {text} in {minutes} minutes.")
        
        def remind():
            sleep_duration = int(minutes) * 60
            time.sleep(sleep_duration)
            reminder_text = f"Sir, this is a reminder to {text}."
            speak(reminder_text)
            notification.notify(
                title="JARVIS Reminder",
                message=reminder_text,
                timeout=20
            )
        
        # A simple thread is the correct way to handle a timed delay
        threading.Thread(target=remind, daemon=True).start()
        return f'Reminder set for {minutes} minutes.'
    except Exception as e:
        speak("Sorry, I could not set the reminder.")
        return f'Error: {str(e)}'


# --- MAIN COMMAND PROCESSOR ---
def process_command(command):
    command = command.lower().strip()
    print(f"Received command: '{command}'")

    if not command:
        return "No command received"

    # --- Command Routing ---
    if any(word in command for word in ['hello', 'hi', 'jarvis', 'are you there']):
        speak("Yes sir, at your service.")
        return "JARVIS is active"
        
    elif 'open notepad' in command:
        return open_notepad()
        
    elif 'open youtube' in command:
        return open_youtube()

    elif 'open website' in command:
        url = command.replace('open website', '').strip()
        return open_website(url) if url else speak("Which website should I open?")
        
    elif 'screenshot' in command:
        return take_screenshot()

    elif 'lock system' in command or 'lock the pc' in command:
        return lock_system()

    elif 'shutdown system' in command:
        return shutdown_system()

    elif 'restart system' in command:
        return restart_system()

    elif 'system information' in command or 'system status' in command:
        return get_system_info()
        
    elif 'battery status' in command or 'check battery' in command:
        return check_battery_status()

    elif 'wikipedia' in command:
        query = command.replace('wikipedia', '').strip()
        return search_wikipedia(query) if query else speak("What should I search on Wikipedia?")

    elif 'weather in' in command:
        # Assumes format "weather in [city]"
        city = command.split('in')[-1].strip()
        return get_weather(city) if city else speak("Which city's weather do you want?")

    elif 'news' in command:
        return get_news()

    elif 'remind me to' in command:
        try:
            # Assumes format "remind me to [task] in [number] minutes"
            parts = command.split(' in ')
            time_part = parts[-1]
            task_part = ' in '.join(parts[:-1]).replace('remind me to', '').strip()
            minutes = ''.join(filter(str.isdigit, time_part))
            
            if task_part and minutes:
                return set_reminder(task_part, minutes)
            else:
                raise ValueError("Invalid format")
        except Exception:
            speak("I didn't understand the reminder. Please say it like: remind me to check the email in 5 minutes.")
            return "Invalid reminder format"

    elif 'what is the time' in command or 'current time' in command:
        time_now = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {time_now}")
        return f"Time: {time_now}"
        
    elif 'what is today\'s date' in command or 'current date' in command:
        date_now = datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {date_now}")
        return f"Date: {date_now}"
        
    elif 'search for' in command:
        query = command.replace('search for', '').strip()
        if query:
            speak(f"Searching Google for {query}")
            webbrowser.open(f"https://google.com/search?q={query}")
            return f"Searching for: {query}"
        else:
            return speak("What would you like me to search for?")
    
    else:
        speak("I did not understand that command. Should I search for it on Google?")
        # As a fallback, you can decide whether to search or just reply
        return "Unknown command"


# --- STARTUP SCRIPT ---
# This runs only once when the Django server starts
speak(f"JARVIS system initialized at {datetime.now().strftime('%I:%M %p')}. All systems are online and ready.")