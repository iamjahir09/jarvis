from django.shortcuts import render
from django.http import JsonResponse
import json
import subprocess
import pyautogui
import webbrowser
import os
import ctypes
import platform
import psutil
from datetime import datetime
import re
import wikipedia
import requests
import screen_brightness_control as sbc
from plyer import notification
import threading
import time
import google.generativeai as genai
import pyperclip
from pathlib import Path
import random

# --- CONFIGURATION ---
OPENWEATHERMAP_API_KEY = "7e6655d516cc0d5d24f0343a9cc8584b"
NEWS_API_KEY = "557c58a57feb495aa23c551c96c7d77e"
GEMINI_API_KEY = "AIzaSyDGgiLFSZb-iAsrhASDCJefia6Ok9B7ehY"

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("AI model initialized successfully")
except Exception as e:
    print(f"Failed to configure Gemini: {e}")
    model = None

# Test the model connection
def test_ai_model():
    """Test if AI model is working"""
    if model:
        try:
            test_response = model.generate_content("Say 'AI is working'")
            if test_response and hasattr(test_response, 'text'):
                print("AI model test successful")
                return True
        except Exception as e:
            print(f"AI model test failed: {e}")
    return False

# --- CORE SPEECH FUNCTION ---
def speak(text, wait=False):
    """Reliable text-to-speech function with blocking option"""
    try:
        safe_text = str(text).replace('"', '')
        if platform.system() == 'Windows':
            if wait:
                # Blocking call for important messages
                subprocess.run(
                    f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{safe_text}\')"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.3)
            else:
                # Non-blocking for less critical messages
                subprocess.Popen(
                    f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{safe_text}\')"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        else:
            print(f"Speech not supported on {platform.system()}")
    except Exception as e:
        print(f"Error in speak function: {e}")

# --- LANGUAGE FUNCTIONS ---
def get_language_from_command(command):
    """Detect programming language from command with voice feedback"""
    language_map = {
        'python': ['python', 'py', 'django', 'flask', 'fastapi'],
        'java': ['java', 'spring', 'maven'],
        'javascript': ['javascript', 'js', 'node', 'nodejs', 'react', 'vue', 'angular'],
        'html': ['html', 'web', 'website', 'webpage', 'frontend'],
        'css': ['css', 'style', 'styling', 'bootstrap'],
        'c++': ['c++', 'cpp', 'c plus plus'],
        'c#': ['c#', 'c sharp', 'csharp', 'dotnet'],
        'go': ['go', 'golang'],
        'rust': ['rust'],
        'php': ['php', 'laravel', 'wordpress'],
        'ruby': ['ruby', 'rails'],
        'swift': ['swift', 'ios'],
        'kotlin': ['kotlin', 'android'],
        'typescript': ['typescript', 'ts'],
        'sql': ['sql', 'database', 'mysql', 'postgresql']
    }
    
    command_lower = command.lower()
    for lang, keywords in language_map.items():
        if any(keyword in command_lower for keyword in keywords):
            speak(f"Detected {lang} as programming language")
            return lang
    
    speak("Using Python as default language")
    return 'python'

def get_file_extension(language):
    """Get file extension for given language"""
    extensions = {
        'python': 'py',
        'java': 'java',
        'javascript': 'js',
        'html': 'html',
        'css': 'css',
        'c++': 'cpp',
        'c#': 'cs',
        'go': 'go',
        'rust': 'rs',
        'php': 'php',
        'ruby': 'rb',
        'swift': 'swift',
        'kotlin': 'kt',
        'typescript': 'ts',
        'sql': 'sql'
    }
    return extensions.get(language.lower(), 'txt')

# --- CODE GENERATION FUNCTIONS ---
def type_with_effect(text):
    """Type text with visual effect in VS Code"""
    try:
        lines = text.split('\n')
        for line in lines:
            pyperclip.copy(line)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
            time.sleep(0.1)
    except Exception as e:
        print(f"Typing error: {e}")
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')

def generate_code(description, language='python'):
    """Generate code using AI with voice feedback"""
    if not model:
        speak("AI model is not available", wait=True)
        return None
    
    speak(f"Generating {language} code for: {description}", wait=True)
    
    # Enhanced prompts for different languages
    if language == 'python':
        prompt = f"""You are an expert Python developer. Create a complete, professional Python project for: {description}

Requirements:
1. Write clean, well-documented code with proper imports
2. Use proper Python conventions (PEP 8)
3. Include error handling where appropriate
4. Add meaningful comments and docstrings
5. Structure code with functions/classes as needed
6. Include example usage or main execution block
7. Make it production-ready and scalable

Return ONLY the Python code without any markdown or explanations."""

    elif language == 'javascript':
        prompt = f"""You are an expert JavaScript/Node.js developer. Create a complete, professional JavaScript project for: {description}

Requirements:
1. Write modern JavaScript (ES6+) code
2. Include proper error handling and validation
3. Use appropriate design patterns
4. Add comprehensive comments
5. Structure with functions/classes/modules
6. Make it production-ready and efficient
7. Include example usage

Return ONLY the JavaScript code without any markdown or explanations."""

    elif language == 'java':
        prompt = f"""You are an expert Java developer. Create a complete, professional Java project for: {description}

Requirements:
1. Write clean, object-oriented Java code
2. Follow Java naming conventions
3. Include proper exception handling
4. Add Javadoc comments
5. Structure with appropriate classes and methods
6. Make it production-ready and maintainable
7. Include main method with example usage

Return ONLY the Java code without any markdown or explanations."""

    elif language in ['html', 'web']:
        prompt = f"""You are an expert web developer. Create a complete, professional web project for: {description}

Requirements:
1. Write semantic HTML5 with modern CSS3
2. Include responsive design principles
3. Add JavaScript for interactivity if needed
4. Use proper web standards and accessibility
5. Structure with clean, organized code
6. Make it production-ready and cross-browser compatible
7. Include all necessary meta tags and structure

Return ONLY the code without any markdown or explanations."""

    else:
        prompt = f"""You are an expert {language} developer. Create a complete, professional {language} project for: {description}

Requirements:
1. Write clean, well-structured code
2. Follow {language} best practices and conventions
3. Include proper error handling
4. Add meaningful comments
5. Structure appropriately for the language
6. Make it production-ready and efficient
7. Include example usage

Return ONLY the {language} code without any markdown or explanations."""
    
    try:
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text') and response.text:
            # Clean the response text
            code_text = response.text.strip()
            # Remove markdown code blocks if present
            if code_text.startswith('```'):
                lines = code_text.split('\n')
                if len(lines) > 2:
                    code_text = '\n'.join(lines[1:-1])
            speak("Professional code generated successfully", wait=True)
            return code_text
        else:
            speak("Failed to generate code", wait=True)
            return None
    except Exception as e:
        speak(f"Code generation error: {str(e)}", wait=True)
        print(f"Detailed error: {e}")
        return None

def create_code_file(description, language='python'):
    """Create professional code project with proper structure"""
    try:
        # Create main projects directory
        projects_dir = Path.home() / "Desktop" / "JARVIS_Projects"
        projects_dir.mkdir(exist_ok=True)
        
        # Generate unique project name
        clean_desc = re.sub(r'[^\w\s]', '', description.lower())
        clean_desc = re.sub(r'\s+', '_', clean_desc)[:25]
        timestamp = datetime.now().strftime("%m%d_%H%M")
        project_name = f"{clean_desc}_{timestamp}"
        
        # Create project directory
        project_dir = projects_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Generate code
        code = generate_code(description, language)
        if not code:
            # Enhanced fallback code templates
            speak("Using enhanced fallback template", wait=True)
            if language == 'python':
                code = f'''"""
{description}
Generated by JARVIS - Professional Python Project
Created on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import os
import sys
from datetime import datetime


class {clean_desc.title().replace('_', '')}:
    """
    Main class for {description}
    """
    
    def __init__(self):
        self.created_at = datetime.now()
        print(f"Initialized {description} at {{self.created_at}}")
    
    def run(self):
        """
        Main execution method
        """
        print("Hello World from JARVIS!")
        print(f"Project: {description}")
        # TODO: Implement your logic here
        pass


def main():
    """
    Main function to run the application
    """
    app = {clean_desc.title().replace('_', '')}()
    app.run()


if __name__ == "__main__":
    main()
'''
            elif language == 'javascript':
                code = f'''/**
 * {description}
 * Generated by JARVIS - Professional JavaScript Project
 * Created on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 */

class {clean_desc.title().replace('_', '')} {{
    constructor() {{
        this.createdAt = new Date();
        console.log(`Initialized {description} at ${{this.createdAt}}`);
    }}
    
    run() {{
        console.log("Hello World from JARVIS!");
        console.log("Project: {description}");
        // TODO: Implement your logic here
    }}
}}

// Main execution
const app = new {clean_desc.title().replace('_', '')}();
app.run();

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {clean_desc.title().replace('_', '')};
}}
'''
            elif language == 'html':
                code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{description.title()}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 600px;
        }}
        
        h1 {{
            color: #764ba2;
            margin-bottom: 1rem;
        }}
        
        .footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{description.title()}</h1>
        <p>Generated by JARVIS - Professional Web Project</p>
        <p>Created on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="footer">
            <p>Powered by JARVIS AI Assistant</p>
        </div>
    </div>
    
    <script>
        console.log("JARVIS Web Project Initialized");
        console.log("Project: {description}");
    </script>
</body>
</html>
'''
            else:
                code = f"// {description}\n// Generated by JARVIS\n// Created: {datetime.now()}\n\nconsole.log('Hello World!');"
        
        # Determine filename and create file
        ext = get_file_extension(language)
        if language == 'html':
            filename = "index.html"
        elif language == 'python':
            filename = "main.py"
        elif language == 'javascript':
            filename = "main.js"
        else:
            filename = f"main.{ext}"
        
        filepath = project_dir / filename
        
        # Save code to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Create additional project files
        create_project_files(project_dir, language, description)
        
        speak(f"Professional project created: {project_name}", wait=True)
        
        # Try to open VS Code with the project
        open_project_in_editor(project_dir, filepath)
        
        return {
            "status": "success",
            "project_path": str(project_dir),
            "project_name": project_name,
            "main_file": filename,
            "message": f"Professional project '{project_name}' created successfully!"
        }
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        speak(error_msg, wait=True)
        print(f"Detailed error: {e}")
        return {"status": "error", "message": error_msg}

def create_project_files(project_dir, language, description):
    """Create additional project files like README, requirements, etc."""
    try:
        # Create README file
        readme_content = f"""# {description.title()}

Generated by JARVIS AI Assistant
Created on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Description
{description}

## Technology
- Language: {language.title()}
- Created with: JARVIS AI Assistant

## How to Run
"""
        
        if language == 'python':
            readme_content += """
```bash
python main.py
```

## Requirements
See requirements.txt for dependencies.
"""
            # Create requirements.txt
            with open(project_dir / "requirements.txt", 'w') as f:
                f.write("# Project dependencies\n# Add your requirements here\n")
                
        elif language == 'javascript':
            readme_content += """
```bash
node main.js
```

## Package Information
See package.json for project details.
"""
            # Create package.json
            package_json = f'''{{
    "name": "{project_dir.name}",
    "version": "1.0.0",
    "description": "{description}",
    "main": "main.js",
    "scripts": {{
        "start": "node main.js"
    }},
    "author": "JARVIS AI",
    "license": "MIT"
}}'''
            with open(project_dir / "package.json", 'w') as f:
                f.write(package_json)
                
        elif language == 'html':
            readme_content += """
Open index.html in a web browser.

## Files
- index.html: Main HTML file
- style.css: Styling (if separate)
- script.js: JavaScript functionality (if separate)
"""

        # Write README
        with open(project_dir / "README.md", 'w') as f:
            f.write(readme_content)
            
    except Exception as e:
        print(f"Error creating project files: {e}")

def open_project_in_editor(project_dir, main_file):
    """Open the project in VS Code or default editor"""
    vscode_paths = [
        r"C:\Users\pc\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        "code"  # If VS Code is in PATH
    ]
    
    vscode_opened = False
    for vscode_path in vscode_paths:
        try:
            if vscode_path == "code":
                # Try using command line to open the entire project
                result = subprocess.run([vscode_path, str(project_dir)], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    vscode_opened = True
                    speak("VS Code opened with full project", wait=True)
                    break
            else:
                # Try using full path to open project
                if os.path.exists(vscode_path):
                    subprocess.Popen([vscode_path, str(project_dir)])
                    vscode_opened = True
                    speak("VS Code opened with project folder", wait=True)
                    break
        except Exception as e:
            print(f"Failed to open with {vscode_path}: {e}")
            continue
    
    if not vscode_opened:
        # Fallback - open main file with default editor
        try:
            os.startfile(str(main_file))
            speak("Opened main file with default editor", wait=True)
        except Exception as e:
            speak("Project created but couldn't open editor", wait=True)

# --- COMMAND FUNCTIONS ---
def open_notepad():
    try:
        speak("Opening Notepad", wait=True)
        os.startfile('notepad.exe')
        return "Opened Notepad"
    except Exception as e:
        speak(f"Error opening Notepad: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def open_calculator():
    try:
        speak("Opening Calculator", wait=True)
        subprocess.Popen('calc.exe')
        return "Opened Calculator"
    except Exception as e:
        speak(f"Error opening Calculator: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def open_website(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        speak(f"Opening {url}", wait=True)
        webbrowser.open(url)
        return f"Opened: {url}"
    except Exception as e:
        speak(f"Error opening website: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def take_screenshot():
    try:
        speak("Taking screenshot", wait=True)
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = desktop / filename
        
        pyautogui.screenshot(filepath)
        speak(f"Screenshot saved as {filename}", wait=True)
        return f"Screenshot saved: {filename}"
    except Exception as e:
        speak(f"Error taking screenshot: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def shutdown_system():
    speak("System will shutdown in 5 seconds", wait=True)
    os.system('shutdown /s /t 5')
    return "Shutting down"

def restart_system():
    speak("System will restart in 5 seconds", wait=True)
    os.system('shutdown /r /t 5')
    return "Restarting"

def lock_system():
    try:
        speak("Locking system", wait=True)
        ctypes.windll.user32.LockWorkStation()
        return "System locked"
    except Exception as e:
        speak(f"Error locking system: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def unlock_laptop():
    try:
        speak("Unlocking laptop", wait=True)
        # Uses stored credentials
        subprocess.run([
            "powershell",
            "-command",
            "$cred = cmdkey /generic:JARVIS_UNLOCK | Out-String; "
            "Start-Process -FilePath 'explorer.exe' -Credential $cred"
        ], shell=True)
        return "Laptop unlocked successfully"
    except Exception as e:
        speak(f"Error unlocking laptop: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def adjust_volume(action):
    try:
        if action == "up":
            speak("Increasing volume", wait=True)
            pyautogui.press('volumeup', presses=5)
            return "Volume increased"
        elif action == "down":
            speak("Decreasing volume", wait=True)
            pyautogui.press('volumedown', presses=5)
            return "Volume decreased"
        elif action == "mute":
            speak("Toggling mute", wait=True)
            pyautogui.press('volumemute')
            return "Volume muted"
    except Exception as e:
        speak(f"Error adjusting volume: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def set_brightness(level):
    try:
        speak(f"Setting brightness to {level}%", wait=True)
        sbc.set_brightness(level)
        return f"Brightness set to {level}%"
    except Exception as e:
        speak(f"Error setting brightness: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def get_system_info():
    try:
        speak("Getting system information", wait=True)
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery() if hasattr(psutil, 'sensors_battery') else None
        
        info = f"CPU Usage: {cpu}%, Memory Usage: {mem.percent}%"
        if battery:
            status = "charging" if battery.power_plugged else "discharging"
            info += f", Battery: {battery.percent}% ({status})"
        
        speak(info, wait=True)
        return info
    except Exception as e:
        speak(f"Error getting system info: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def search_wikipedia(query):
    try:
        speak(f"Searching Wikipedia for {query}", wait=True)
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=2)
        speak("Wikipedia says: " + summary, wait=True)
        return f"Wikipedia: {summary}"
    except wikipedia.exceptions.PageError:
        speak(f"No Wikipedia page found for {query}", wait=True)
        return f"No results for {query}"
    except wikipedia.exceptions.DisambiguationError:
        speak(f"Multiple matches for {query}, please be specific", wait=True)
        return f"Ambiguous query: {query}"
    except Exception as e:
        speak(f"Wikipedia search error: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def get_weather(city):
    try:
        speak(f"Checking weather for {city}", wait=True)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if data['cod'] == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            result = f"In {city}: {temp}°C, {desc}"
            speak(result, wait=True)
            return result
        else:
            speak(f"Could not find weather for {city}", wait=True)
            return f"Weather not found for {city}"
    except Exception as e:
        speak(f"Weather check error: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def get_news():
    try:
        speak("Getting latest news", wait=True)
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        headlines = []
        speak("Top news headlines:", wait=True)
        for i, article in enumerate(data['articles'][:3]):
            headline = article['title']
            headlines.append(f"{i+1}. {headline}")
            speak(f"{i+1}. {headline}", wait=True)
            time.sleep(1)
        
        return "News: " + ", ".join(headlines)
    except Exception as e:
        speak(f"News error: {str(e)}", wait=True)
        return f"Error: {str(e)}"

def set_reminder(text, minutes):
    try:
        speak(f"Setting reminder: {text} in {minutes} minutes", wait=True)
        
        def reminder():
            time.sleep(int(minutes) * 60)
            speak(f"Reminder: {text}", wait=True)
            notification.notify(
                title="JARVIS Reminder",
                message=text,
                timeout=10
            )
        
        threading.Thread(target=reminder, daemon=True).start()
        return f"Reminder set for {text} in {minutes} minutes"
    except Exception as e:
        speak(f"Reminder error: {str(e)}", wait=True)
        return f"Error: {str(e)}"

# --- MAIN COMMAND PROCESSOR ---
def process_command(command):
    command = command.lower().strip()
    print(f"Processing command: {command}")
    
    if not command:
        speak("No command received", wait=True)
        return "No command"
    
    try:
        # Coding commands
        if any(cmd in command for cmd in ['write code', 'generate code', 'create script', 'how to code', 'code']):
            language = get_language_from_command(command)
            description = re.sub(r'^(write code for|generate code for|create a|how to code|code|generate|write|create)', '', command).strip()
            
            if description:
                return create_code_file(description, language)
            else:
                speak("Please describe what code to generate", wait=True)
                return "No description"
        
        # Application commands
        elif 'open notepad' in command:
            return open_notepad()
        elif 'open calculator' in command:
            return open_calculator()
        elif 'open youtube' in command:
            return open_website('youtube.com')
        elif 'open website' in command:
            url = command.replace('open website', '').strip()
            if url:
                return open_website(url)
            else:
                speak("Please specify website", wait=True)
                return "No website"
        
        # System commands
        elif 'take screenshot' in command:
            return take_screenshot()
        elif 'shutdown' in command:
            return shutdown_system()
        elif 'restart' in command:
            return restart_system()
        elif 'lock' in command:
            return lock_system()
        elif 'unlock' in command:
            return unlock_laptop()
        elif 'volume up' in command:
            return adjust_volume('up')
        elif 'volume down' in command:
            return adjust_volume('down')
        elif 'mute' in command:
            return adjust_volume('mute')
        elif 'brightness' in command:
            try:
                level = int(re.search(r'\d+', command).group())
                if 0 <= level <= 100:
                    return set_brightness(level)
                else:
                    speak("Brightness must be 0-100", wait=True)
                    return "Invalid brightness"
            except:
                speak("Specify brightness level (0-100)", wait=True)
                return "No brightness"
        
        # Information commands
        elif 'time' in command:
            current_time = datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}", wait=True)
            return f"Time: {current_time}"
        elif 'date' in command:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {current_date}", wait=True)
            return f"Date: {current_date}"
        elif 'system info' in command:
            return get_system_info()
       
        elif 'wikipedia' in command:
            query = command.replace('wikipedia', '').strip()
            if query:
                return search_wikipedia(query)
            else:
                speak("Specify search query", wait=True)
                return "No query"
        elif 'weather' in command:
            city = command.replace('weather', '').replace('in', '').strip()
            if city:
                return get_weather(city)
            else:
                speak("Specify city name", wait=True)
                return "No city"
        elif 'news' in command:
            return get_news()
        
        # Reminder command
        elif 'remind me to' in command:
            try:
                parts = command.split(' in ')
                task = parts[0].replace('remind me to', '').strip()
                minutes = parts[1].strip()
                if task and minutes:
                    return set_reminder(task, minutes)
            except:
                speak("Say: 'remind me to [task] in [minutes]'", wait=True)
                return "Invalid reminder"
        
        # Greetings
        elif any(word in command for word in ['hello', 'hi', 'hey', 'jarvis']):
            greetings = ["Hello sir!", "Hi there!", "Greetings!", "How can I help?"]
            response = random.choice(greetings)
            speak(response, wait=True)
            return response
        
        else:
            speak("Command not recognized", wait=True)
            return "Unknown command"
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        speak(error_msg, wait=True)
        return error_msg

# --- DJANGO VIEWS ---
def home(request):
    """Render the main page"""
    return render(request, 'index.html')

def process_voice(request):
    """Process voice commands via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command', '')
            response = process_command(command)
            return JsonResponse({'response': response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)