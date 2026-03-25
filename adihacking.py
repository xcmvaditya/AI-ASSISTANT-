#!/data/data/com.termux/files/usr/bin/python

from gtts import gTTS
import os
import datetime
import wikipedia
import subprocess
import sys
import time
import random
import json
import threading
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AdityaAI:
    def __init__(self):
        self.name = "Aditya AI Assistant"
        self.version = "1.0"
        self.creator = "Aditya"
        # Use Termux home directory for temporary files
        self.temp_dir = Path.home() / ".aditya_temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.audio_file = self.temp_dir / "output.mp3"
        
        self.commands = {
            'time': 'Show current time',
            'date': 'Show current date',
            'calculate': 'Calculate mathematical expressions',
            'wikipedia': 'Search Wikipedia',
            'weather': 'Get weather info (requires curl)',
            'joke': 'Tell a random joke',
            'note': 'Save a note',
            'readnotes': 'Read saved notes',
            'systeminfo': 'Show system information',
            'battery': 'Show battery status',
            'camera': 'Open camera (if available)',
            'music': 'Play music from storage',
            'chat': 'Chat mode (conversation)',
            'help': 'Show all commands',
            'exit': 'Exit assistant'
        }
        self.notes_file = Path.home() / "aditya_notes.json"
        self.chat_history = []
        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the Python programmer go to therapy? He had too many unresolved issues!",
            "What do you call a fake noodle? An impasta!",
            "Why don't scientists trust atoms? Because they make up everything!",
            "What did the computer do at lunchtime? Had a byte!",
            "Why was the JavaScript developer sad? Because he didn't know how to 'null' his feelings!",
            "What's a computer's favorite beat? An algorithm!"
        ]
        
    def speak(self, text):
        """Text to speech function"""
        print(f"{Colors.CYAN}{self.name}: {Colors.END}{text}")
        try:
            # Try to use espeak if gTTS fails (works without internet)
            tts = gTTS(text=text, lang='en')
            tts.save(str(self.audio_file))
            
            # Try different players for Termux
            players = [
                f"mpv {self.audio_file} > /dev/null 2>&1",
                f"play {self.audio_file} > /dev/null 2>&1",
                f"aplay {self.audio_file} > /dev/null 2>&1"
            ]
            
            played = False
            for player in players:
                if os.system(player) == 0:
                    played = True
                    break
            
            if not played:
                # If no audio player works, just show text
                print(f"{Colors.WARNING}[Audio not supported, text only]{Colors.END}")
                
            # Clean up audio file after playing
            try:
                if self.audio_file.exists():
                    self.audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            # Fallback to espeak if gTTS fails
            try:
                os.system(f"espeak '{text}' > /dev/null 2>&1")
            except:
                print(f"{Colors.RED}Speech error: {e}{Colors.END}")
    
    def display_banner(self):
        """Display cool ASCII banner"""
        banner = f"""
{Colors.BLUE}{Colors.BOLD}
    ╔═══════════════════════════════════════════╗
    ║     █████╗ ██████╗ ██╗████████╗██╗   ██╗ █████╗     ║
    ║    ██╔══██╗██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝██╔══██╗    ║
    ║    ███████║██║  ██║██║   ██║    ╚████╔╝ ███████║    ║
    ║    ██╔══██║██║  ██║██║   ██║     ╚██╔╝  ██╔══██║    ║
    ║    ██║  ██║██████╔╝██║   ██║      ██║   ██║  ██║    ║
    ║    ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝    ║
    ║                                                   ║
    ║         {Colors.GREEN}AI Assistant by Aditya {Colors.BLUE}                   ║
    ║              Version {self.version}                          ║
    ╚═══════════════════════════════════════════════╝
{Colors.END}"""
        print(banner)
    
    def show_help(self):
        """Display all available commands"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}Available Commands:{Colors.END}\n")
        for cmd, desc in self.commands.items():
            print(f"  {Colors.CYAN}{cmd:15}{Colors.END} - {desc}")
        print(f"\n{Colors.WARNING}Tip: You can use natural language like 'what time is it?'{Colors.END}\n")
    
    def save_note(self, note):
        """Save a note to file"""
        try:
            notes = {}
            if self.notes_file.exists():
                with open(self.notes_file, 'r') as f:
                    notes = json.load(f)
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notes[timestamp] = note
            
            with open(self.notes_file, 'w') as f:
                json.dump(notes, f, indent=2)
            
            self.speak("Note saved successfully!")
            return True
        except Exception as e:
            print(f"{Colors.RED}Failed to save note: {e}{Colors.END}")
            return False
    
    def read_notes(self):
        """Read all saved notes"""
        try:
            if not self.notes_file.exists():
                self.speak("No notes found!")
                return
            
            with open(self.notes_file, 'r') as f:
                notes = json.load(f)
            
            if not notes:
                self.speak("No notes available.")
                return
            
            self.speak(f"Found {len(notes)} notes. Reading them now.")
            for timestamp, note in notes.items():
                print(f"\n{Colors.GREEN}[{timestamp}]{Colors.END}")
                print(f"{note}\n")
                time.sleep(1)
        except Exception as e:
            print(f"{Colors.RED}Error reading notes: {e}{Colors.END}")
    
    def get_weather(self):
        """Get weather information (requires internet)"""
        try:
            result = subprocess.run(['curl', '-s', 'wttr.in?format=%l:+%c+%t+%w'], 
                                   capture_output=True, text=True, timeout=10)
            weather_info = result.stdout.strip()
            if weather_info:
                self.speak(f"Weather info: {weather_info}")
            else:
                self.speak("Unable to fetch weather. Check internet connection.")
        except subprocess.TimeoutExpired:
            self.speak("Weather request timed out.")
        except Exception as e:
            print(f"{Colors.RED}Weather service error: {e}{Colors.END}")
            self.speak("Weather service unavailable. Install curl: pkg install curl")
    
    def get_system_info(self):
        """Display system information"""
        try:
            # Get storage info
            storage = subprocess.run(['df', '-h', '/data'], capture_output=True, text=True)
            # Get memory info (if available)
            try:
                memory = subprocess.run(['free', '-h'], capture_output=True, text=True)
                memory_info = memory.stdout.splitlines()[1]
            except:
                memory_info = "Memory info not available"
            
            # Get uptime
            uptime = subprocess.run(['uptime'], capture_output=True, text=True)
            
            info = f"""
{Colors.BOLD}System Information:{Colors.END}
{Colors.CYAN}Storage:{Colors.END}
{storage.stdout.splitlines()[1] if storage.stdout else 'Storage info not available'}

{Colors.CYAN}Memory:{Colors.END}
{memory_info}

{Colors.CYAN}Uptime:{Colors.END}
{uptime.stdout.strip() if uptime.stdout else 'Uptime not available'}"""
            print(info)
            self.speak("System information displayed on screen.")
        except Exception as e:
            print(f"{Colors.RED}Error getting system info: {e}{Colors.END}")
    
    def get_battery(self):
        """Get battery status"""
        try:
            battery = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=5)
            if battery.returncode == 0:
                data = json.loads(battery.stdout)
                percentage = data.get('percentage', 'Unknown')
                status = data.get('status', 'Unknown')
                self.speak(f"Battery at {percentage} percent. Status: {status}")
            else:
                self.speak("Battery information not available")
        except subprocess.TimeoutExpired:
            self.speak("Battery check timed out.")
        except Exception as e:
            print(f"{Colors.RED}Battery error: {e}{Colors.END}")
            self.speak("Error reading battery status")
    
    def play_music(self):
        """Play music from storage"""
        self.speak("Opening music player. Navigate to your music folder.")
        try:
            # Try common music directories
            music_dirs = [
                "/sdcard/Music/",
                "/storage/emulated/0/Music/",
                "/storage/sdcard/Music/"
            ]
            
            for music_dir in music_dirs:
                if os.path.exists(music_dir):
                    os.system(f"termux-open {music_dir} > /dev/null 2>&1")
                    break
            else:
                self.speak("Music folder not found")
        except:
            self.speak("Please specify music path manually")
    
    def tell_joke(self):
        """Tell a random joke"""
        joke = random.choice(self.jokes)
        self.speak(joke)
    
    def chat_mode(self):
        """Enter chat conversation mode"""
        self.speak("Entering chat mode. You can talk to me naturally. Type 'exit' to return to normal mode.")
        print(f"{Colors.GREEN}Chat Mode Active. Type your messages:{Colors.END}\n")
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}You: {Colors.END}").lower().strip()
                
                if user_input in ['exit', 'quit', 'back']:
                    self.speak("Exiting chat mode.")
                    break
                
                # Check for various queries
                if any(word in user_input for word in ['time', 'clock']):
                    time_now = datetime.datetime.now().strftime("%I:%M %p")
                    self.speak(f"The time is {time_now}")
                
                elif any(word in user_input for word in ['date', 'day']):
                    date_today = datetime.datetime.now().strftime("%B %d, %Y")
                    self.speak(f"Today is {date_today}")
                
                elif 'joke' in user_input:
                    self.tell_joke()
                
                elif 'weather' in user_input:
                    self.get_weather()
                
                elif 'hello' in user_input or 'hi' in user_input:
                    self.speak(f"Hello! How can I help you?")
                
                elif 'how are you' in user_input:
                    self.speak("I'm doing great! Thanks for asking.")
                
                elif 'your name' in user_input:
                    self.speak(f"I am {self.name}, created by {self.creator}.")
                
                elif 'thank' in user_input:
                    self.speak("You're welcome!")
                
                else:
                    self.speak(f"You said: {user_input}. I'm still learning. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                self.speak("Exiting chat mode.")
                break
    
    def process_command(self, command):
        """Process user commands"""
        command_lower = command.lower()
        
        # Natural language processing
        if any(word in command_lower for word in ['time', 'clock']):
            time_now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {time_now}")
        
        elif any(word in command_lower for word in ['date', 'day']):
            date_today = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {date_today}")
        
        elif 'calculate' in command_lower or 'compute' in command_lower:
            try:
                expression = command_lower.replace('calculate', '').replace('compute', '').strip()
                # Remove any words and keep math expression
                import re
                expression = re.sub(r'[^0-9+\-*/%.() ]', '', expression)
                result = eval(expression)
                self.speak(f"The result is {result}")
            except Exception as e:
                self.speak(f"Sorry, I couldn't calculate that. Error: {str(e)}")
        
        elif 'wikipedia' in command_lower or 'search' in command_lower:
            try:
                topic = command_lower.replace('wikipedia', '').replace('search', '').strip()
                if not topic:
                    self.speak("What would you like to search for?")
                    return
                self.speak(f"Searching Wikipedia for {topic}...")
                summary = wikipedia.summary(topic, sentences=2)
                self.speak(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                self.speak(f"Multiple results found. Please be more specific.")
            except wikipedia.exceptions.PageError:
                self.speak(f"Sorry, I couldn't find that on Wikipedia.")
            except Exception as e:
                self.speak(f"Wikipedia error: {str(e)}")
        
        elif 'weather' in command_lower:
            self.get_weather()
        
        elif 'joke' in command_lower:
            self.tell_joke()
        
        elif 'note' in command_lower:
            if 'read' in command_lower or 'show' in command_lower:
                self.read_notes()
            else:
                self.speak("What would you like to save?")
                note_text = input(f"{Colors.BOLD}Note: {Colors.END}")
                if note_text.strip():
                    self.save_note(note_text)
        
        elif 'systeminfo' in command_lower:
            self.get_system_info()
        
        elif 'battery' in command_lower:
            self.get_battery()
        
        elif 'camera' in command_lower:
            self.speak("Opening camera...")
            photo_path = self.temp_dir / "photo.jpg"
            os.system(f"termux-camera-photo {photo_path} > /dev/null 2>&1")
            if photo_path.exists():
                self.speak("Photo captured successfully!")
        
        elif 'music' in command_lower:
            self.play_music()
        
        elif 'chat' in command_lower:
            self.chat_mode()
        
        elif 'help' in command_lower or 'commands' in command_lower:
            self.show_help()
        
        elif 'exit' in command_lower or 'bye' in command_lower or 'quit' in command_lower:
            return False
        
        else:
            self.speak("Sorry, I didn't understand that. Type 'help' to see available commands.")
        
        return True
    
    def run(self):
        """Main loop"""
        self.display_banner()
        self.speak(f"Hello! I am {self.name}. Ready for your commands.")
        print(f"{Colors.WARNING}Type 'help' to see all commands or 'chat' for conversation mode.{Colors.END}\n")
        
        while True:
            try:
                command = input(f"{Colors.BOLD}{Colors.GREEN}You: {Colors.END}").strip()
                
                if not command:
                    continue
                
                # Check for exit first
                if command.lower() in ['exit', 'bye', 'quit', 'goodbye']:
                    self.speak("Goodbye! Have a great day!")
                    break
                
                # Process the command
                result = self.process_command(command)
                if result is False:
                    break
                
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}Goodbye!{Colors.END}")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.END}")
                self.speak("An error occurred. Please try again.")

if __name__ == "__main__":
    assistant = AdityaAI()
    assistant.run()
