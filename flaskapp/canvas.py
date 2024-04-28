import cv2
import mediapipe as mp
import numpy as np
import os
import math

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#Take webcam input:
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 5)
width = 1280
height = 720
cap.set(3, width)
cap.set(4, height)

imgCanvas = np.zeros((height, width, 3), np.uint8)

#Get header images from the image directory
script_dir = os.path.dirname(os.path.abspath(__file__))
folderPath = os.path.join(script_dir, 'Images')

myList = os.listdir(folderPath)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)

#Default setting:
header = overlayList[0]
drawColor = (0, 0, 255)
thickness = 20
tipIds = [4, 8, 12, 16, 20] 
xp, yp = [0, 0]

with mp_hands.Hands(min_detection_confidence=0.85, min_tracking_confidence=0.5, max_num_hands=1) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            break
            
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                points = []
                for lm in hand_landmarks.landmark:
                    points.append([int(lm.x * width), int(lm.y * height)])

                #If hand is detected initialize coordinates
                if len(points) != 0:
                    x1, y1 = points[8]  # Index finger
                    x2, y2 = points[12] # Middle finger
                    x3, y3 = points[4]  # Thumb
                    x4, y4 = points[20] # Pinky

                    #Checking if a finger/thumb is up
                    fingers = []
                    if points[tipIds[0]][0] < points[tipIds[0] - 1][0]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                    for id in range(1, 5):
                        if points[tipIds[id]][1] < points[tipIds[id] - 2][1]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                    #Selection Mode - Two fingers are up
                    nonSel = [0, 3, 4] # indexes of the fingers that need to be down in the Selection Mode
                    if (fingers[1] and fingers[2]) and all(fingers[i] == 0 for i in nonSel):
                        xp, yp = [x1, y1]

                        # Selecting the colors and the eraser on the screen
                        if(y1 < 125):
                            if(170 < x1 < 295):
                                header = overlayList[0]
                                drawColor = (255 , 0, 0)
                            elif(436 < x1 < 561):
                                header = overlayList[3]
                                drawColor = (95, 0, 189)
                            elif(700 < x1 < 825):
                                header = overlayList[2]
                                drawColor = (0, 255, 255)
                            elif(980 < x1 < 1105):
                                header = overlayList[1]
                                drawColor = (0, 0, 0)

                        cv2.rectangle(image, (x1-10, y1-15), (x2+10, y2+23), drawColor, cv2.FILLED)

                    #Stand by Mode
                    nonStand = [0, 2, 3]
                    if (fingers[1] and fingers[4]) and all(fingers[i] == 0 for i in nonStand):
                        cv2.line(image, (xp, yp), (x4, y4), drawColor, 5) 
                        xp, yp = [x1, y1]

                    #Draw Mode
                    nonDraw = [0, 2, 3, 4]
                    if fingers[1] and all(fingers[i] == 0 for i in nonDraw):
                        
                        cv2.circle(image, (x1, y1), int(thickness/2), drawColor, cv2.FILLED) 
                        if xp==0 and yp==0:
                            xp, yp = [x1, y1]
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
                        xp, yp = [x1, y1]

                    #Clear the canvas
                    if all(fingers[i] == 0 for i in range(0, 5)):
                        imgCanvas = np.zeros((height, width, 3), np.uint8)
                        xp, yp = [x1, y1]

                    #Adjust the thickness 
                    selecting = [1, 1, 0, 0, 0] 
                    setting = [1, 1, 0, 0, 1]  
                    if all(fingers[i] == j for i, j in zip(range(0, 5), selecting)) or all(fingers[i] == j for i, j in zip(range(0, 5), setting)):
                        r = int(math.sqrt((x1-x3)**2 + (y1-y3)**2)/3)
                        
                        # Get the middle point between fingers
                        x0, y0 = [(x1+x3)/2, (y1+y3)/2]
                        
                        # Getting the vector that is orthogonal
                        v1, v2 = [x1 - x3, y1 - y3]
                        v1, v2 = [-v2, v1]

                        #Normalizing it 
                        mod_v = math.sqrt(v1**2 + v2**2)
                        v1, v2 = [v1/mod_v, v2/mod_v]
                        
                        # Draw the circle that represents the draw thickness
                        c = 3 + r
                        x0, y0 = [int(x0 - v1*c), int(y0 - v2*c)]
                        cv2.circle(image, (x0, y0), int(r/2), drawColor, -1)

                        #Set the thickness
                        if fingers[4]:                        
                            thickness = r
                            cv2.putText(image, 'Check', (x4-25, y4-8), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0,0,0), 1)

                        xp, yp = [x1, y1]

        #Set the header
        header_height = 125
        header_width = width

        header = cv2.resize(header, (header_width, header_height))
        image[0:125, 0:width] = header

        #Camera image with the drawing made in imgCanvas
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 5, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(image, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        cv2.imshow('MediaPipe Hands', img)
        if cv2.waitKey(3) == 13:
            break

cap.release()
cv2.destroyAllWindows()