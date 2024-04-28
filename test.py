import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# Get the list of available voices
voices = engine.getProperty('voices')

# Print available voices
for voice in voices:
    print("Voice:")
    print(" - ID: %s" % voice.id)
    print(" - Name: %s" % voice.name)
    print(" - Languages: %s" % voice.languages)
    print(" - Gender: %s" % voice.gender)
    print(" - Age: %s" % voice.age)
    print(" ")

# Set voice (optional)
engine.setProperty('voice', voices[1].id)  # Set the voice you want to use

# Set the text you want to convert to speech
text = "Hello, this is a test. How are you doing today?"

# Convert text to speech
engine.say(text)

# Wait for the speech to finish
engine.runAndWait()
