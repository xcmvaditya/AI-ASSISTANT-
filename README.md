# Update packages first
pkg update && pkg upgrade -y

# Install required dependencies
pkg install python git python-pip ffmpeg mpv -y

# Install Python packages
pip install gtts wikipedia pyttsx3

# Clone your repository
git clone https://github.com/xcmvaditya/AI-ASSISTANT-.git

# Navigate to the directory
cd AI-ASSISTANT-

# Make the script executable
chmod +x aditya_ai.py

# Run the assistant
python aditya_ai.py
