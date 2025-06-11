from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import os
import face_recognition
import cv2
import threading
from multiprocessing import Pool  # Added for parallel processing

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///faces.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
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

# New helper function for parallel processing
def process_image(args):
    import face_recognition  # Required for multiprocessing
    image_path, name = args
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        return (encodings[0], name) if encodings else None
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

# Optimized face loading using multiprocessing
def load_known_faces():
    global known_faces, known_names
    print("Optimized loading of known faces...")
    
    # Get all images from database
    identities = Identity.query.all()
    image_paths = [(os.path.join(app.root_path, i.image_path), i.name) 
                   for i in identities]
    
    # Process images in parallel
    with Pool() as pool:
        results = pool.map(process_image, image_paths)
    
    # Clear existing data and update with new results
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
    # Group images by identity name
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
    # Secure the folder name (optional: implement your own sanitization)
    safe_name = name.replace(' ', '_')
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        if file and file.filename:
            filename = file.filename
            filepath = os.path.join(folder_path, filename)
            file.save(filepath)
            # Store the relative path in the database
            rel_path = os.path.join('static', 'uploads', safe_name, filename)
            new_identity = Identity(name=name, image_path=rel_path)
            db.session.add(new_identity)
    db.session.commit()
    return redirect(url_for('index'))

# @app.route('/clear_db')
# def clear_db():
#     num_deleted = Identity.query.delete()
#     db.session.commit()
#     return f"Cleared {num_deleted} records from the database."


# if __name__ == '__main__':
#     app.run(debug=True)
