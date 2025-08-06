from django.shortcuts import render
from django.http import JsonResponse
from .voice_commands import process_command
import json

def home(request):
    return render(request, 'index.html')

def process_voice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        command = data.get('command', '')
        response = process_command(command)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)

import subprocess

def unlock_laptop():
    try:
        # Uses stored credentials
        subprocess.run([
            "powershell",
            "-command",
            "$cred = cmdkey /generic:JARVIS_UNLOCK | Out-String; "
            "Start-Process -FilePath 'explorer.exe' -Credential $cred"
        ], shell=True)
        return "Laptop unlocked successfully"
    except Exception as e:
        return f"Error: {str(e)}"