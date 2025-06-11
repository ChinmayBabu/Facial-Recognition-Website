
# Facial Recognition Website

A web-based facial recognition system that detects and recognizes faces in real-time using a webcam. Built with **Python**, **Flask**, and **OpenCV**, this project demonstrates how computer vision can be integrated into a web interface for facial authentication or surveillance purposes.

## 🔍 Features

- Real-time face detection using webcam
- Face recognition from stored dataset
- Option to add new users to dataset
- Organized project structure with Flask backend
- HTML/CSS based frontend (can be upgraded to React)

## 📂 Project Structure

```
Facial-Recognition-Website/
├── static/                 # CSS, JS, and images
├── templates/              # HTML files
├── dataset/                # Stored user images
├── test/                   # Test images for recognition
├── app.py                  # Flask backend
├── camera.py               # Webcam capture logic
├── face_train.py           # Encodes faces in dataset
├── face_recog.py           # Face recognition logic
├── requirements.txt        # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip` for installing dependencies
- Webcam

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ChinmayBabu/Facial-Recognition-Website.git
   cd Facial-Recognition-Website
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare the dataset**
   - Add folders with user images inside `dataset/`, each folder name should be the person's name.

5. **Train the face data**
   ```bash
   python face_train.py
   ```

6. **Run the Flask app**
   ```bash
   python app.py
   ```

7. **Access the website**
   - Go to `http://127.0.0.1:5000` in your browser

## 📸 How It Works

- The webcam captures a frame.
- Face encodings are compared with the pre-trained encodings.
- If a match is found, the name is displayed on the screen.
- Unknown faces can be flagged or ignored based on configuration.

## 🛠️ Technologies Used

- Python
- Flask
- OpenCV
- face_recognition
- HTML, CSS

## 🧠 Future Enhancements

- React frontend for better UI
- Face registration via web UI
- Database integration (e.g., SQLite/PostgreSQL)
- Access logs for recognized faces

## 📝 License

This project is open-source under the MIT License.
