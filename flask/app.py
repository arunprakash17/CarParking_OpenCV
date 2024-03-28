
from flask import Flask, render_template, request,Response
import cv2
import pickle
import cvzone
import numpy as np
import mysql.connector
import re




def live_pred():
# Video feed
    cap = cv2.VideoCapture('carParkingInput.mp4')
    with open('parkingSlotPosition', 'rb') as f: 
        posList = pickle.load(f)
    width, height = 107, 48
    def checkParkingSpace (imgPro):
        spaceCounter = 0
        for pos in posList:
            x, y = pos
            imgCrop = imgPro[y:y + height, x:x + width]
            # cv2.imshow(str(x * y), imgCrop)
            count = cv2.countNonZero (imgCrop)
            if count < 900:
                color= (0, 255, 0)
                thickness = 5
                spaceCounter += 1
                
            else:
                color= (0, 0, 255)
                thickness = 2
                
            cv2.rectangle(img,pos,(pos[0]+width,pos[1]+height),color,thickness)
            cvzone.putTextRect(img, f'Free: {spaceCounter}/{len (posList)}' ,(100, 50),scale=3,thickness=5, offset=20, colorR=(0, 200, 0))
        return None
    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT): 
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        Success, img = cap.read()
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2. GaussianBlur (imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur (imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate (imgMedian, kernel, iterations=1)
        checkParkingSpace (imgDilate)
       # cv2.imshow("Image", img)
        # cv2.imshow("ImageBlur", imgBlur)
        # cv2.imshow("ImageThres", imgMedian)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        ret,buffer = cv2.imencode('.jpg',img)
        img = buffer.tobytes()

        yield(b'--frame\r\n'
                    b'Content-Type:image/jpeg\r\n\r\n'+img+b'\r\n')


app = Flask(__name__)
app.secret_key = 'a'

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Prakash@17",
    database = "car"
)
conn = mydb.cursor()
print("connected")


@app.route('/')
def project():
    return render_template('index.html')
@app.route('/hero')
def home():
    return render_template('index.html')
@app.route('/model')
def model():
    return render_template('model.html')
@app.route('/login')
def login():
    return render_template('login.html')



@app.route("/reg", methods=['POST', 'GET'])
def signup():
    msg =""
    if request.method == 'POST':
        name= request.form["name"]
        email = request.form["email"]
        password =request.form["password"]
        sql = "SELECT * FROM DETAILS WHERE password = %s and email = %s"
        val = (email,password) 
        conn.execute(sql,val)
        account = conn.fetchall()
        print (account)
        if account:
            return render_template('login.html', error=True)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = "Invalid Email Address!"
        else:
            insert_sql = "INSERT INTO DETAILS(name,email,password) VALUES(%s,%s,%s)"
            val = (name,email,password)
            conn.execute(insert_sql,val)
            mydb.commit()
            msg = "You have successfully registered !"
    return render_template('login.html', msg=msg)



@app.route("/log",methods=['POST','GET'])
def login1():
    
    if request.method == "POST":
       
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM DETAILS WHERE EMAIL = %s AND PASSWORD = %s"
        val = (email,password)
        conn.execute(sql,val)
        account = conn.fetchall()
        print (account)
        if account:
            return render_template('model.html')
        else:
            msg = "Incorrect Email/password"
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')



@app.route('/predict_live')
def generate():
    return Response(live_pred(),mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__ =="__main__":
    app.run(debug=True)
