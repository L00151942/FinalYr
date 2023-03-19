import cv2
import mediapipe as mp
import time

y = 50
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0) # or cap = cv2.VideoCapture('video.mp4')

while True:
    # Read a frame from the video
    ret, frame = cap.read()

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

    # IMPORTANT: Flip image before printing text
    frame = cv2.flip(frame, 1)

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
        for hand_landmarks in results.multi_hand_landmarks:
            # get the coordinates of the landmark (9 = centre of hand)
            handPosition = hand_landmarks.landmark[9].y
            y = 100 - ((handPosition * 135) - 18.5)
            # volBar Height and Text
            if y >= 100:
                radioVolumeTxt = cv2.putText(frame, f"{100}%", (575, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                volBar = cv2.rectangle(frame, (618, 418), (607, 62), (0, 255, 0), -1)
            elif y <= 0:
                radioVolumeTxt = cv2.putText(frame, f"{0}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                volBar = cv2.rectangle(frame, (618, 418), (618, 418), (0, 0, 0), -1)
            else:
                radioVolumeTxt = cv2.putText(frame, f"{int(y)}%", (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
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


# Print y in console
    if cv2.waitKey(1) & 0xFF == ord('y'):
        print(y)

    # Show the image
    cv2.imshow('MediaPipe Hand Gesture Recognition', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
