#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Voice Assistant for Lab 3 with Touch Sensor
Interactive voice assistant using speech recognition, Ollama AI, text-to-speech, and MPR121 touch sensor

Dependencies:
- ollama (API client)
- speech_recognition
- pyaudio
- espeak
- adafruit-circuitpython-mpr121
"""

# pip3 install adafruit-circuitpython-mpr121 -> install in ollama_venv

import speech_recognition as sr
import subprocess
import requests
import json
import time
import sys
import re
import board
import busio
import adafruit_mpr121

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'UTF-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    import codecs
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

TTS_ENGINE = 'espeak'

# Initialize I2C and MPR121
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)


class OllamaVoiceAssistant:
    def __init__(self, model_name="phi3:mini", ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # --- Score Tracking State ---
        self.player_scores = {}  # Dictionary to store player name -> score
        self.score_initialized = False
        self.waiting_for_score_update = False
        # ----------------------------

        # Test Ollama connection
        self.test_ollama_connection()

        # Adjust for ambient noise
        print("Calibrating mic... Please stay quiet for 3 seconds.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
        self.recognizer.pause_threshold = 0.6  # Allow short pauses
        print("Ready for conversation!")

    def test_ollama_connection(self):
        """Test if Ollama is running and the model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if self.model_name in model_names:
                    print(f"Ollama is running with {self.model_name} model")
                else:
                    print(f"Model {self.model_name} not found. Available models: {model_names}")
                    if model_names:
                        self.model_name = model_names[0]
                        print(f"Using {self.model_name} instead")
            else:
                raise Exception("Ollama API not responding")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running: 'ollama serve'")
            sys.exit(1)

    def speak(self, text):
        """Convert text to speech"""
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        print(f"Assistant: {clean_text}")
        subprocess.run(['espeak', clean_text], check=False)

    def listen(self):
        """Listen for speech and convert to text"""
        try:
            timeout = 5
            print("Listening...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)

            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()

        except sr.WaitTimeoutError:
            print("No speech detected, timing out...")
            if self.waiting_for_score_update:
                self.waiting_for_score_update = False
                self.speak("Timeout. Please say 'update score' again when you're ready.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

    def query_ollama(self, prompt, system_prompt=None):
        """Send a query to Ollama and get response"""
        try:
            data = {"model": self.model_name, "prompt": prompt, "stream": False}
            if system_prompt:
                data["system"] = system_prompt

            response = requests.post(f"{self.ollama_url}/api/generate", json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Sorry, I could not generate a response.')
            else:
                return f"Error: Ollama API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            return "Sorry, the response took too long. Please try again."
        except Exception as e:
            return f"Error communicating with Ollama: {e}"

    # --- Touch Sensor for Player Count ---
    def get_num_players_via_touch(self, max_players=12, timeout=10):
        """
        Detect number of players via single pad touch.
        Each pad corresponds to a number of players: pad 0 = 1 player, pad 1 = 2 players, etc.
        """
        self.speak(f"Please touch a pad to indicate the number of players (1-{max_players}).")

        start_time = time.time()
        while True:
            for i in range(max_players):
                if mpr121[i].value:
                    num_players = i + 1
                    self.speak(f"{num_players} players detected")
                    return num_players

            if time.time() - start_time > timeout:
                self.speak("Timeout. Defaulting to 3 players.")
                return 3

    # --- Score Tracking Methods ---
    def initialize_scores(self, initial_amount=10000):
        """Ask user for number of players via touch sensor and initialize scores."""
        num_players = self.get_num_players_via_touch()
        players = [f"user{i+1}" for i in range(num_players)]
        self.player_scores = {player.lower(): initial_amount for player in players}
        self.score_initialized = True
        player_list = ", ".join(players)
        return f"Game started! {player_list} all begin with ${initial_amount}. Let the game begin!"

    def update_score(self, player_name, amount, operation):
        """Updates a player's score and returns the new balance."""
        player_name = player_name.lower()
        if player_name not in self.player_scores:
            return f"Sorry, I don't see a player named {player_name}."

        try:
            amount = int(amount)
            if amount < 0:
                return "Please state a positive amount."

            if operation == 'subtract':
                self.player_scores[player_name] -= amount
                action_word = "paid"
            elif operation == 'add':
                self.player_scores[player_name] += amount
                action_word = "received"
            else:
                return "Internal error: Invalid operation."

            new_balance = self.player_scores[player_name]
            self.waiting_for_score_update = False

            return f"Understood. {player_name.capitalize()} {action_word} ${amount}. Their new balance is ${new_balance}. Scores are updated!"
        except ValueError:
            return "I couldn't understand the amount. Please state it clearly."

    def parse_score_command(self, user_input):
        """Parse commands like 'user1 plus 300', 'user 2 - 500', etc."""
        player_names_pattern = r"user\s*1|user\s*2|user\s*3|user\s*4|user\s*5|user\s*6|user\s*7|user\s*8|user\s*9|user\s*10|user\s*11|user\s*12"

        patterns = [
            rf"(?P<player>{player_names_pattern})\s+(?P<op>plus|add|received|got|gained)\s+(?P<amount>\d+)",
            rf"(?P<player>{player_names_pattern})\s+(?P<op>minus|subtract|paid|lost|owes)\s+(?P<amount>\d+)",
            rf"(?P<player>{player_names_pattern})\s*(?P<op>\+|\-)\s*(?P<amount>\d+)",
            rf"(?P<op>plus|add|received|got|gained)\s+(?P<amount>\d+)\s+(?:to|for)\s+(?P<player>{player_names_pattern})",
            rf"(?P<op>minus|subtract|paid|lost|owes)\s+(?P<amount>\d+)\s+(?:from)\s+(?P<player>{player_names_pattern})",
        ]

        for pat in patterns:
            match = re.search(pat, user_input, re.IGNORECASE)
            if match:
                player = match.group("player").replace(" ", "")
                amount = match.group("amount")
                op = match.group("op").lower()
                if op in ["minus", "subtract", "paid", "lost", "owes", "-"]:
                    operation = "subtract"
                else:
                    operation = "add"
                return player, amount, operation

        return None

    def display_scores(self):
        """Returns a string listing all current player scores."""
        if not self.player_scores:
            return "No game in progress. Say 'start game' to begin."
        score_lines = [f"{name.capitalize()}: ${score:,.0f}" for name, score in self.player_scores.items()]
        return "Current scores are: " + " | ".join(score_lines)
    # ---------------------------------

    def run_conversation(self):
        """Main conversation loop"""
        print("\nOllama Voice Assistant Started!")
        print("Say 'hello' to start, 'exit' to quit.")
        print("Say 'start game' to begin tracking scores.")
        print("Say 'update score' to start the two-step process for score changes.")
        print("Say 'show scores' to check balances.")
        print("=" * 50)

        system_prompt = "You are a helpful voice assistant. Keep your responses concise and conversational."

        self.speak("Hello! I'm your Monopoly game assistant. How can I help you today?")

        while True:
            try:
                user_input = self.listen()
                if user_input is None:
                    continue

                # Exit
                if any(word in user_input for word in ['exit', 'quit', 'bye']):
                    self.speak("Goodbye! Have a great day!")
                    break

                # Step 2: waiting for score
                if self.waiting_for_score_update and self.score_initialized:
                    score_command = self.parse_score_command(user_input)
                    print("DEBUG parsed:", score_command)
                    if score_command:
                        player, amount, operation = score_command
                        response = self.update_score(player, amount, operation)
                        self.speak(response)
                        continue
                    else:
                        self.speak("Sorry, I didn't catch that. Say 'user one plus 300' or 'user two minus 500'.")
                        continue

                # Start game
                if 'start game' in user_input and not self.score_initialized:
                    response = self.initialize_scores()
                    self.speak(response)
                    continue

                # Show scores
                if 'show score' in user_input or 'current balance' in user_input:
                    response = self.display_scores()
                    self.speak(response)
                    continue

                # Trigger score update
                if ('update score' in user_input or 'change score' in user_input) and self.score_initialized:
                    self.waiting_for_score_update = True
                    self.speak("Ready to update. Please say which user and how much.")
                    continue

                # Greetings
                if any(word in user_input for word in ['hello', 'hi', 'hey']):
                    self.speak("Hello! What would you like to do?")
                    continue

                # General queries → Ollama
                print("Thinking...")
                response = self.query_ollama(user_input, system_prompt)
                self.speak(response)

            except KeyboardInterrupt:
                print("\nConversation interrupted by user")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.speak("Sorry, I encountered an error. Let's try again.")


def main():
    """Main function to run the voice assistant"""
    print("Starting Ollama Voice Assistant...")

    try:
        assistant = OllamaVoiceAssistant()
        assistant.run_conversation()
    except Exception as e:
        print(f"Failed to start assistant: {e}")


if __name__ == "__main__":
    main()
