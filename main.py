import cv2
import threading
from flask import Flask, Response, jsonify
import atexit
import logging
import os
import sys

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Global variables
camera = None
camera_lock = threading.Lock()
current_camera = None
streaming = False
camera_indices = [0, 1]

def find_cameras():
    """Find available camera indices"""
    global camera_indices
    camera_indices = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_indices.append(i)
        cap.release()

def init_camera(cam_id):
    global camera, current_camera
    with camera_lock:
        if camera is not None:
            camera.release()
        camera = cv2.VideoCapture(cam_id)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            current_camera = cam_id
            return True
        return False

def generate_frames():
    global camera, streaming
    while streaming:
        with camera_lock:
            if camera is not None:
                success, frame = camera.read()
                if not success:
                    continue
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def stop_camera():
    global camera, streaming
    streaming = False
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None

# Cleanup on exit
atexit.register(stop_camera)

@app.route('/')
def index():
    return jsonify({
        "status": "Web View Camera Server Running",
        "endpoints": {
            "/start": "Start streaming",
            "/stop": "Stop streaming",
            "/front": "Switch to front camera",
            "/back": "Switch to back camera",
            "/stream": "Video stream"
        }
    })

@app.route('/start')
def start_stream():
    global streaming
    if not streaming:
        streaming = True
        if current_camera is None and camera_indices:
            init_camera(camera_indices[0])
        return jsonify({"status": "success", "message": "Stream started"})
    return jsonify({"status": "info", "message": "Already streaming"})

@app.route('/stop')
def stop_stream():
    stop_camera()
    return jsonify({"status": "success", "message": "Stream stopped"})

@app.route('/front')
def front_camera():
    if len(camera_indices) > 1:
        if init_camera(camera_indices[1]):
            return jsonify({"status": "success", "message": "Switched to front camera"})
    elif len(camera_indices) == 1:
        if init_camera(camera_indices[0]):
            return jsonify({"status": "success", "message": "Using single camera"})
    return jsonify({"status": "error", "message": "Front camera not available"})

@app.route('/back')
def back_camera():
    if camera_indices:
        if init_camera(camera_indices[0]):
            return jsonify({"status": "success", "message": "Switched to back camera"})
    return jsonify({"status": "error", "message": "Back camera not available"})

@app.route('/stream')
def video_feed():
    if not streaming:
        return jsonify({"status": "error", "message": "Stream not started. Use /start endpoint first."})
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    find_cameras()
    if camera_indices:
        init_camera(camera_indices[0])
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)