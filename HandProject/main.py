import cv2
import mediapipe as mp
import time
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Volume Control Config
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume.SetMasterVolumeLevel(-10.0, None) # default volume
volumeRange = volume.GetVolumeRange()
minV = volumeRange[0]
maxV = volumeRange[1]

# Radio control variable config
y = 50

# MediaPipe variable Config
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0) # or cap = cv2.VideoCapture('video.mp4')

while True:
    # Read a frame from the video
    ret, frame = cap.read()

    # Gesture recognition variable config
    fingerCount = 0  # Initially set finger count to 0 for each cap

    # FPS variables
    start_time = time.time()  # start the timer
    ret, frame = cap.read()  # read a frame from the video
    fps = 1 / (time.time() - start_time)   # calculate fps

    # Convert the image to RGB and process it with MediaPipe
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand landmarks on the image
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Get hand index to check label (left or right)
            handIndex = results.multi_hand_landmarks.index(hand_landmarks)
            handLabel = results.multi_handedness[handIndex].classification[0].label

            # Set variable to keep landmarks positions (x and y)
            handLandmarks = []

            # Fill list with x and y positions of each landmark
        for landmarks in hand_landmarks.landmark:
            handLandmarks.append([landmarks.x, landmarks.y])

            # Test conditions for each finger: Count is increased if finger is
            #   considered raised.
            # Thumb: TIP x position must be greater or lower than IP x position,
            #   depending on hand label.
        if handLabel == "Left" and handLandmarks[4][0] > handLandmarks[3][0]:
            fingerCount = fingerCount + 1
        elif handLabel == "Right" and handLandmarks[4][0] < handLandmarks[3][0]:
            fingerCount = fingerCount + 1

            # Other fingers: TIP y position must be lower than PIP y position,
            #   as image origin is in the upper left corner.
        if handLandmarks[8][1] < handLandmarks[6][1]:  # Index finger
            fingerCount = fingerCount + 1
        if handLandmarks[12][1] < handLandmarks[10][1]:  # Middle finger
            fingerCount = fingerCount + 1
        if handLandmarks[16][1] < handLandmarks[14][1]:  # Ring finger
            fingerCount = fingerCount + 1
        if handLandmarks[20][1] < handLandmarks[18][1]:  # Pinky
            fingerCount = fingerCount + 1

    # IMPORTANT: Flip image before printing text
    frame = cv2.flip(frame, 1)

    # Display finger count
    if fingerCount >= 3:
        gestureText = cv2.putText(frame, f"Gesture: Open Palm", (5, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    elif fingerCount < 3:
        gestureText = cv2.putText(frame, f"Gesture: Closed Fist", (5, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    gestureText = cv2.putText(frame, f"Fingers: {str(fingerCount)}", (5, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # FPS COUNTER
    # Draw black background rectangle
    cv2.rectangle(frame, (700, 0), (560, 20), (0, 0, 0), -1)
    # add fps text to the frame
    cv2.putText(frame, f"FPS: {fps:.2f}", (565, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Min MAX Line
    cv2.rectangle(frame, (0, 60), (640, 420), (232, 232, 232), 1)

    # VolBar outline
    cv2.rectangle(frame, (605, 60), (620, 420), (0, 0, 0), 2)

# Print hand landmarks as radio volume.
    if results.multi_hand_landmarks:
        if fingerCount >= 3:
            for hand_landmarks in results.multi_hand_landmarks:
                # get the coordinates of the hand landmark (9 = centre of hand) and manipulate it to equal the volume
                handPosition = hand_landmarks.landmark[9].y
                y = 100 - ((handPosition * 135) - 18.5)

                # Set the Pc's volume where the coordinated equal the MinMax volume range
                pcVolume = np.interp(y, [0, 100], [minV, maxV])
                volume.SetMasterVolumeLevel(pcVolume, None)

                # volBar Height and Text
                if y >= 100:
                    radioVolumeTxt = cv2.putText(frame, f"{100}%", (575, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    volBar = cv2.rectangle(frame, (618, 418), (607, 62), (0, 255, 0), -1)
                elif y <= 0:
                    radioVolumeTxt = cv2.putText(frame, f"{0}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    volBar = cv2.rectangle(frame, (618, 418), (618, 418), (0, 0, 0), -1)
                    volume.GetMute()
                else:
                    radioVolumeTxt = cv2.putText(frame, f"{int(y)}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    volBar = cv2.rectangle(frame, (607, 402 - int(y * 3.4)), (618, 418), (0, 255, 0), -1)
        else:
            # volBar Height and Text
            if y >= 100:
                radioVolumeTxt = cv2.putText(frame, f"{100}%", (575, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0),
                                             2)
                volBar = cv2.rectangle(frame, (618, 418), (607, 62), (0, 255, 0), -1)
            elif y <= 0:
                radioVolumeTxt = cv2.putText(frame, f"{0}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                volBar = cv2.rectangle(frame, (618, 418), (618, 418), (0, 0, 0), -1)
                volume.GetMute()
            else:
                radioVolumeTxt = cv2.putText(frame, f"{int(y)}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255, 255, 255), 2)
                volBar = cv2.rectangle(frame, (607, 402 - int(y * 3.4)), (618, 418), (0, 255, 0), -1)
    else:
        if y >= 100:
            radioVolumeTxt = cv2.putText(frame, f"{100}%", (575, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            volBar = cv2.rectangle(frame, (618, 418), (607, 62), (0, 255, 0), -1)
        elif y <= 0:
            radioVolumeTxt = cv2.putText(frame, f"{0}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            volBar = cv2.rectangle(frame, (618, 418), (618, 418), (0, 0, 0), -1)
        else:
            radioVolumeTxt = cv2.putText(frame, f"{int(y)}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            volBar = cv2.rectangle(frame, (607, 402 - int(y * 3.4)), (618, 418), (0, 255, 0), -1)

    # Show the image
    cv2.imshow('Vehicle Control System', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

#references
# https://www.geekering.com/categories/computer-vision/marcellacavalcanti/hand-tracking-and-finger-counting-in-python-with-mediapipe/
