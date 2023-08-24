# Import necessary libraries
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
import cvzone
import time
import random

# Initialize the webcam capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width
cap.set(4, 720)   # Set height

# Initialize the hand detector with specified parameters
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Define the polynomial coefficients for converting pixel distance to real-world distance
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)

# Initialize variables for the target circle and game parameters
cx, cy = 250, 250   # Initial position of the target circle
color = (255, 0, 255)  # Initial color of the target circle
counter = 0  # Counter for tracking successful hits
score = 0    # Player's score
timeStart = time.time()  # Start time of the game
totalTime = 20  # Total time for the game in seconds

while True:
    # Capture a frame from the webcam
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip the frame horizontally for a mirrored view

    # Check if the game time is still within the specified total time
    if time.time() - timeStart < totalTime:

        # Detect hands in the frame
        hands = detector.findHands(img, draw=False)

        if hands:
            lmList = hands[0]['lmList']
            x, y, w, h = hands[0]['bbox']
            x1, y1 = lmList[5][:2]  # Position of the tip of the index finger
            x2, y2 = lmList[17][:2]  # Position of the tip of the middle finger

            # Calculate the pixel distance between the two fingers
            distance = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
            A, B, C = coff
            distanceCM = A * distance ** 2 + B * distance + C

            # Check if the fingers are close enough to the target for a hit
            if distanceCM < 40 and x < cx < x + w and y < cy < y + h:
                counter = 1  # Start the counter for tracking successful hits

            # Draw a rectangle around the hand and display the calculated distance
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3)
            cvzone.putTextRect(img, f'{int(distanceCM)} cm', (x + 5, y - 10))

        if counter:
            counter += 1
            color = (0, 250, 0)
            if counter == 3:
                cx = random.randint(100, 1100)  # Move the target circle to a random position
                cy = random.randint(100, 600)
                color = (255, 0, 255)
                score += 1
                counter = 0  # Reset the counter after a successful hit

        # Draw the target circle and additional circles for visual effects
        cv2.circle(img, (cx, cy), 30, color, cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 20, (255, 255, 255), 2)
        cv2.circle(img, (cx, cy), 30, (50, 50, 50), 2)

        # Display the remaining time and player's score
        cvzone.putTextRect(img, F'Time: {int(totalTime - (time.time() - timeStart))}', (1000, 75), scale=3, offset=20)
        cvzone.putTextRect(img, f'Score: {str(score).zfill(2)}', (60, 75), scale=3, offset=20)

    else:
        # Game over screen with final score and restart instructions
        cvzone.putTextRect(img, 'Game Over', (400, 400), scale=5, offset=30, thickness=7)
        cvzone.putTextRect(img, f'Your Score: {score}', (450, 500), scale=3, offset=20)
        cvzone.putTextRect(img, f'Press R to restart', (460, 575), scale=2, offset=10)

    # Display the image
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    # Check if the player pressed the 'R' key to restart the game
    if key == ord('r'):
        timeStart = time.time()  # Reset the game start time
        score = 0  # Reset the player's score
