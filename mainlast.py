import cv2 as cv
import numpy as np
from Robot import Robot
from flask import Flask, request, render_template, Response, make_response
from picamera import PiCamera
from io import BytesIO
import logging

moves = [0, [0, 1.1], [0,1.1], [0,1.1], [0,1.1], [1, 0.85], [0,1.1], [0,1.1], [0,1.1], [0,1.1]]
def process(img1, moves):
    try:
        img = img1.copy()
        '''grayed = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        dst = cv.Canny(grayed, 100, 200, None, 3)
        blurred = cv.blur(dst, (20, 20))
        height = img.shape[0] - 1
        width = img.shape[1] - 1
        slice_height = height // 20
        midpoints = []
        thresh = 10
        img_bw = cv.threshold(blurred, thresh, 255, cv.THRESH_BINARY)[1]'''
        height = img.shape[0] - 1
        width = img.shape[1] - 1
        slice_height = height // 10
        slice_width = width // 10
        h_points = []
        v_points = []
        for j in range(10):
            bool1 = False
            bool2 = False
            y = height - slice_height * j
            for x in range(width):
                if ((img[y, x][2] > 100 and img[y,x][0] < 150)):
                    x1 = x
                    bool1 = True
                    break
            for x in range(width):
                if  ((img[y, width - x][2] > 100 and img[y,width -x][0] < 150)):
                    x2 = width - x
                    bool2 = True
                    break
            if (bool1 and bool2):
                mid = (x1 + x2) // 2
                h_points.append((mid, y))
        for j in range(10):
            bool1 = False
            bool2 = False
            x = slice_width * j
            for y in range(height):
                if ((img[y, x][2] > 100 and img[y,x][0] < 150)):
                    y1 = y
                    bool1 = True
                    break
            for y in range(height):
                if (img[height - y, x][2] > 100 and img[height - y,x][0] < 150):
                    y2 = height - y
                    bool2 = True
                    break
            if (bool1 and bool2):
                mid = (y1 + y2) // 2
                v_points.append((x, mid))
        
        slope = (v_points[0][0]-h_points[0][0])

        if slope >0:
            points = h_points + v_points
        elif slope < 0:
            v_points.reverse()
            points = h_points + v_points
        else:
            points = h_points
        for i in range(len(points) - 1):
            cv.arrowedLine(img = img, pt1 = points[i], pt2 = points[i+1], thickness = 5, color = (0,255 ,0))
        if (len(points) > 1):
            step = moves[0]
            if moves[step][0] == 0:
                Robert.Forward(moves[step][1])
            else:
              Robert.Turn(True, moves[step][1])
            moves[0] = moves[0] + 1
    except Exception:
        pass
    return img


def reader():
    retur = ""
    with open("myapp.log", "r") as f:
        listed = f.readlines()
        for i in range(len(listed) - 3, len(listed)):
            retur += listed[i] + "<br>"
        return retur


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
            frame = cv.imdecode(np.frombuffer(frame, np.uint8), cv.IMREAD_COLOR)
            frame = np.hstack((frame, process(frame, moves)))
            frame = cv.imencode(".jpg", frame)[1]
            frame = frame.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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
# def processed():
# return Response(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + list(gen())[1] + b'\r\n', mimetype="multipart/x-mixed-replace; boundary=frame")

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
