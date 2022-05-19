import cv2 as cv
import numpy as np
from Robot import Robot
from flask import Flask, request, render_template, Response, make_response
from picamera import PiCamera
from io import BytesIO
import logging

def process(img1):
    img = img1.copy()
    #grayed = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #dst = cv.Canny(grayed, 100, 200, None, 3)
    #blurred = cv.blur(dst, (20, 20))
    height = img.shape[0] - 1
    width = img.shape[1] - 1
    slice_height = height // 20
    midpoints = []
    #return img
    #thresh = 10
    #im_bw = cv.threshold(blurred, thresh, 255, cv.THRESH_BINARY)[1]
    try:
        for j in range(19):
            y = height - j * slice_height
            check1 = False
            check2 = False
            for x in range(width):
                if (img[y, x][2] > 100 and img[y,x][1] < 150):
                    startx = x
                    check1 = True
                    break
            for x in range(width):
                if img[y, width - x][2] > 100 and img[y,x][1] < 150:
                    endx = width - x
                    check2 = True
                    break
            if (check1 and check2 and abs(startx - endx) > 10):
                mid = (startx + endx) // 2
                midpoints.append((mid, y))
            else:
                ending = y
                break
        second_x = midpoints[-1][0]
        slope = (midpoints[-2][0] - midpoints[-1][0])
        #if(y < height/2):
            #Robert.Forward(0.1)
        if (slope < 0):
            #Robert.Turn(False, 0.2)
            slice_width = (width - midpoints[-1][0]) // 16
            for i in range(3, 16):
                x = second_x + slice_width * i
                check1 = False
                check2 = False
                for y in range(height):
                    if (img[y, x][2] > 100 and img[y,x][1] < 150):
                        starty = y
                        check1 = True
                        break
                for y in range(height):
                    if (img[height - y, x][2] > 100 and img[y,x][1] < 150):
                        endy = height - y
                        check2 = True
                        break
                if (check1 and check2 and abs(starty - endy) > 10):
                    mid = (starty + endy) // 2
                    midpoints.append((x, mid))
        else:
            #Robert.Turn(True, 0.2)
            slice_width = midpoints[-1][0] // 16
            for i in range(3, 16):
                x = second_x - slice_width * i
                check1 = False
                check2 = False
                for y in range(height):
                    if (img[y, x][2] > 100 and img[y,x][1] < 150):
                        starty = y
                        check1 = True
                        break
                for y in range(height):
                    if (img[height - y, x][2] > 100 and img[y,x][1] < 150):
                        endy = height - y
                        check2 = True
                        break
                if (check1 and check2 and abs(starty - endy) > 10):
                    mid = (starty + endy) // 2
                    midpoints.append((x, mid))
        for i in range(len(midpoints) - 1):
            cv.arrowedLine(img=img, pt1=midpoints[i], pt2=midpoints[i + 1], thickness=5, color=(0, 255, 0))
    except Exception:
        pass
    #data= cv.cvtColor(img, cv.COLOR_BGR2RGB)
    #return cv.imencode('.jpg', data)[1]
    return img
    #return cv.merge([im_bw, im_bw, im_bw])
def reader():
    retur = ""
    with open("myapp.log", "r") as f:
        listed = f.readlines()
        for i in range(len(listed) - 3, len(listed)):
            retur += listed[i] + "<br>"
        return retur

def livestream(frame):
    decoded = cv.imdecode(np.frombuffer(frame, dtype=np.uint8),cv.IMREAD_COLOR)
    #decoded= cv.cvtColor(decoded, cv.COLOR_RGB2BGR)
    return decoded

def gen():
    my_stream = BytesIO()
    with PiCamera() as camera:
        camera.rotation = 180
        camera.framerate = 20
        camera.start_preview(fullscreen=False, window=(100, 20, 640, 480))
        for frame in camera.capture_continuous(my_stream, 'jpeg', use_video_port=True):
            my_stream.seek(0)
            my_stream.flush()
            frame = my_stream.getvalue()
            frame = cv.imdecode(np.frombuffer(frame,np.uint8), cv.IMREAD_COLOR)
            frame = np.hstack((frame, process(frame)))
            frame = cv.imencode(".jpg", frame)[1] 
            frame = frame.tobytes()
            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'+ frame+ b'\r\n')

app = Flask('__name__')
Robert = Robot()

@app.route('/')
def index():
    return "welcome to the queens"

@app.route('/fwd', methods=['GET'])
def rest_fwd():
    distance = request.args.get('d', default=1.00, type=float)
    print("hi")
    Robert.Forward(distance)
    return "fwd success"

@app.route("/rev", methods=['GET'])
def rest_rev():
    distance = request.args.get("d", default=1.00, type=float)
    Robert.Reverse(distance)
    return "rev success"

@app.route("/image")
def image():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/processed")
#def processed():
    #return Response(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + list(gen())[1] + b'\r\n', mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/left", methods=["GET"])
def rest_turn():
    rotation = request.args.get("d", default=1.00, type=float)
    Robert.Turn(True, rotation)
    return "turn success"

@app.route("/right", methods=["GET"])
def rest_right():
    rotation = request.args.get("d", default=1.00, type=float)
    Robert.Turn(False, rotation)
    return "turn success"

@app.route("/auto")
def Auto_run():
    Robert.AutoRun()
    return "auto success"


@app.route("/ui")
def ui():
    return render_template("ui.html")


@app.route("/term")
def termin():
    return Response(reader())

if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    app.run(host="0.0.0.0", port=5001, debug=True)
