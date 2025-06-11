from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import os
import face_recognition
import cv2
import threading

# Configure Flask for static files and correct static path
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Use absolute path for SQLite DB (one level up from api/)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.root_path, '..', 'faces.db')}"
# Uploads folder inside api/static/uploads
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
db = SQLAlchemy(app)

class Identity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)

with app.app_context():
    db.create_all()

known_faces = []
known_names = []
video_capture = None
lock = threading.Lock()

# Sequential image processing for Vercel compatibility
def process_image(args):
    import face_recognition
    image_path, name = args
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return None
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        return (encodings[0], name) if encodings else None
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def load_known_faces():
    global known_faces, known_names
    print("Optimized loading of known faces...")

    identities = Identity.query.all()
    # Paths are relative to project root (one level up from api/)
    image_paths = [(os.path.join(app.root_path, '..', i.image_path), i.name) for i in identities]

    results = [process_image(path) for path in image_paths]

    known_faces.clear()
    known_names.clear()

    for result in filter(None, results):
        known_faces.append(result[0])
        known_names.append(result[1])

    print(f"Successfully loaded {len(known_faces)} face encodings")

def generate_frames():
    global video_capture
    video_capture = cv2.VideoCapture(0)
    MODEL = "hog"  # Use hog for faster performance in web context
    tolerance = 0.6

    try:
        while True:
            success, frame = video_capture.read()
            if not success:
                break

            # Resize and convert
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Face detection
            face_locations = face_recognition.face_locations(rgb_small_frame, model=MODEL)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Recognition
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance)
                name = "Unknown"

                if True in matches:
                    name = known_names[matches.index(True)]

                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw boxes and labels
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        if video_capture is not None:
            video_capture.release()
            video_capture = None

@app.route('/webcam')
def webcam():
    return render_template('webcam.html')

@app.route('/video_feed')
def video_feed():
    global video_capture
    if video_capture is None:
        load_known_faces()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/', methods=['GET'])
def index():
    identities = db.session.query(Identity.name).distinct()
    images_by_identity = {}
    for identity in identities:
        images = [img.image_path for img in Identity.query.filter_by(name=identity.name).all()]
        images_by_identity[identity.name] = images
    return render_template('index.html', images_by_identity=images_by_identity)

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    files = request.files.getlist('files')
    safe_name = name.replace(' ', '_')
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        if file and file.filename:
            filename = file.filename
            filepath = os.path.join(folder_path, filename)
            file.save(filepath)
            # Store relative path without 'static/' prefix
            rel_path = os.path.join('uploads', safe_name, filename)
            new_identity = Identity(name=name, image_path=rel_path)
            db.session.add(new_identity)
    db.session.commit()
    return redirect(url_for('index'))

# Debug/utility routes and app.run() are intentionally omitted for Vercel deployment.
