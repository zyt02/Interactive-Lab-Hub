#!/usr/bin/env python3
"""
Uses Moondream to classify whether a captured hand shows thumbs up or thumbs down.
"""

import cv2
import requests
import base64
import time
import json

def capture_image(filename="captured_image.jpg"):
    """Capture image from webcam using OpenCV"""
    print("Opening camera...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None
    
    print("Camera warming up...")
    time.sleep(2)
    for _ in range(30):
        cap.read()
    
    print("Capturing in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("*CLICK*")
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Could not capture image")
        return None
    
    cv2.imwrite(filename, frame)
    print(f"Image saved as: {filename}")
    return filename


def ask_moondream(image_path, prompt):
    """Send image and prompt to local Moondream model"""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    print(f"\nAsking Moondream: {prompt}")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "moondream:latest",
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            # Extract response text depending on Moondream API format
            result = data.get("response") or data.get("output") or ""
            return result.strip()
        else:
            print(f"Error: Moondream returned {response.status_code}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None


def detect_thumbs(image_path):
    """Use Moondream to classify thumbs gesture"""
    classification_prompt = (
        "Look at the image, is there a hand showing a thumbs up or thumbs down gesture?"
        "reply 'up' if the hand shows a thumbs up gesture, 'down' if it shows a thumbs down gesture, "
        "or 'none' if it is unclear or not a hand gesture."
    )
    
    result = ask_moondream(image_path, classification_prompt)

    if not result:
        print("No response from Moondream.")
        return None

    print(f"\nMoondream detected: {result}")
    if "up" in result.lower():
        print("Goooddd! 👍")
        return "Goooddd!"
    elif "down" in result.lower():
        print("Baaadddd 👎")
        return "Baaadddd"
    else:
        print("Could not determine thumbs gesture.")
        return None


def main():
    print("Thumbs Up / Down Recognition via Moondream")
    print("=" * 50)

    image_path = capture_image()
    if not image_path:
        print("Failed to capture image.")
        return

    detect_thumbs(image_path)
    print("Done!")


if __name__ == "__main__":
    main()
