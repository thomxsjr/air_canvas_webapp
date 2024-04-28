from flask import Flask, render_template, Response, session, request, redirect
import cv2
import mediapipe as mp
import numpy as np
import os
import math
import pyrebase

app = Flask(__name__)

config = {
'apiKey': "AIzaSyDivnkmsK4dBJpSDI2Le_Nl6oL9vqJwmMY",
'authDomain': "aircanvasflaskapp.firebaseapp.com",
'projectId': "aircanvasflaskapp",
'storageBucket': "aircanvasflaskapp.appspot.com",
'messagingSenderId': "930383551956",
'appId': "1:930383551956:web:c79ea45ebd49f808ec8a41",
'databaseURL': 'https://aircanvasflaskapp-default-rtdb.asia-southeast1.firebasedatabase.app/'
};

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
app.secret_key = 'secret'


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, 'Images')

# Load header images from the image directory
my_list = os.listdir(folder_path)
overlay_list = [cv2.imread(os.path.join(folder_path, im_path)) for im_path in my_list]

# Default settings
header = overlay_list[0]
draw_color = (0, 0, 255)
thickness = 20
tip_ids = [4, 8, 12, 16, 20] 
xp, yp = [0, 0]

@app.route('/')
def welcome():
    return render_template('welcome.html')
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            return render_template('index.html')
        except:
            return 'Failed To Login'
    else:
        return render_template('login.html')
    
@app.route('/signup', methods=["POST", "GET"])
def signup():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            return render_template('index.html')
        except:
            return 'Failed To Login'
    else:  
        return render_template('signup.html')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')




@app.route('/start_drawing')
def start_drawing():

    return 'Drawing started'


def gen_frames():
    global thickness
    global draw_color
    global header
    global xp
    global yp  # global variables

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 5)
    width = 640
    height = 720
    cap.set(3, width)
    cap.set(4, height)

    img_canvas = np.zeros((height, width, 3), np.uint8)

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

                    if len(points) != 0:
                        x1, y1 = points[8]  # Index finger
                        x2, y2 = points[12] # Middle finger
                        x3, y3 = points[4]  # Thumb
                        x4, y4 = points[20] # Pinky

                        fingers = []
                        if points[tip_ids[0]][0] < points[tip_ids[0] - 1][0]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                        for id in range(1, 5):
                            if points[tip_ids[id]][1] < points[tip_ids[id] - 2][1]:
                                fingers.append(1)
                            else:
                                fingers.append(0)

                        non_sel = [0, 3, 4]
                        if (fingers[1] and fingers[2]) and all(fingers[i] == 0 for i in non_sel):
                            xp, yp = [x1, y1]

                            if(y1 < 125):
                                if(170 < x1 < 295):
                                    header = overlay_list[0]
                                    draw_color = (255 , 0, 0)
                                elif(436 < x1 < 561):
                                    header = overlay_list[3]
                                    draw_color = (95, 0, 189)
                                elif(700 < x1 < 825):
                                    header = overlay_list[2]
                                    draw_color = (0, 255, 255)
                                elif(980 < x1 < 1105):
                                    header = overlay_list[1]
                                    draw_color = (0, 0, 0)

                            cv2.rectangle(image, (x1-10, y1-15), (x2+10, y2+23), draw_color, cv2.FILLED)

                        non_stand = [0, 2, 3]
                        if (fingers[1] and fingers[4]) and all(fingers[i] == 0 for i in non_stand):
                            cv2.line(image, (xp, yp), (x4, y4), draw_color, 5) 
                            xp, yp = [x1, y1]

                        non_draw = [0, 2, 3, 4]
                        if fingers[1] and all(fingers[i] == 0 for i in non_draw):
                            cv2.circle(image, (x1, y1), int(thickness/2), draw_color, cv2.FILLED) 
                            if xp==0 and yp==0:
                                xp, yp = [x1, y1]
                            cv2.line(img_canvas, (xp, yp), (x1, y1), draw_color, thickness)
                            xp, yp = [x1, y1]

                        if all(fingers[i] == 0 for i in range(0, 5)):
                            img_canvas = np.zeros((height, width, 3), np.uint8)
                            xp, yp = [x1, y1]

                        selecting = [1, 1, 0, 0, 0] 
                        setting = [1, 1, 0, 0, 1]  
                        if all(fingers[i] == j for i, j in zip(range(0, 5), selecting)) or all(fingers[i] == j for i, j in zip(range(0, 5), setting)):
                            r = int(math.sqrt((x1-x3)**2 + (y1-y3)**2)/3)
                            x0, y0 = [(x1+x3)/2, (y1+y3)/2]
                            v1, v2 = [x1 - x3, y1 - y3]
                            v1, v2 = [-v2, v1]
                            mod_v = math.sqrt(v1**2 + v2**2)
                            v1, v2 = [v1/mod_v, v2/mod_v]
                            c = 3 + r
                            x0, y0 = [int(x0 - v1*c), int(y0 - v2*c)]
                            cv2.circle(image, (x0, y0), int(r/2), draw_color, -1)

                            if fingers[4]:                        
                                thickness = r
                                cv2.putText(image, 'Check', (x4-25, y4-8), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0,0,0), 1)

                            xp, yp = [x1, y1]

            header_height = 125
            header_width = width

            header_resized = cv2.resize(header, (header_width, header_height))
            image[0:125, 0:width] = header_resized

            img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
            _, img_inv = cv2.threshold(img_gray, 5, 255, cv2.THRESH_BINARY_INV)
            img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
            img = cv2.bitwise_and(image, img_inv)
            img = cv2.bitwise_or(img, img_canvas)

            ret, buffer = cv2.imencode('.jpg', cv2.flip(img, 1))
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
