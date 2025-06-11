```
# Flask Facial Recognition Web App

A web-based facial recognition system built with Python, Flask, OpenCV, and face_recognition. Upload images, manage identities, and perform real-time face recognition using your webcam—all from your browser.

---

## Features

- Upload and manage face images for different identities
- Real-time face recognition using your webcam
- Database-backed image and identity management (SQLite with SQLAlchemy)
- Optimized face encoding for faster recognition
- Easy deployment to Vercel or other cloud platforms

---

## Demo

> **Note:** For privacy and resource reasons, a live demo is not provided.  
> You can run the app locally or deploy to Vercel.

---

## Getting Started

### 1. Clone the Repository

```

git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

```

### 2. Install Dependencies

Create a virtual environment (recommended):

```

python -m venv venv
source venv/bin/activate  \# On Windows: venv\Scripts\activate

```

Install Python dependencies:

```

pip install -r requirements.txt

```

### 3. Project Structure

```

api/
├── index.py          \# Main Flask app
├── static/           \# Uploaded images and static assets
└── templates/        \# HTML templates
requirements.txt
vercel.json

```

### 4. Running Locally

```

cd api
python index.py

```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Deployment

### Deploying to Vercel

1. **Remove** or comment out any `app.run()` lines in your Flask code.
2. Ensure your Flask app is in `api/index.py`.
3. Add a `vercel.json` file at the root:

    ```
    {
      "rewrites": [
        { "source": "/(.*)", "destination": "/api/index" }
      ]
    }
    ```

4. Push your code to GitHub.
5. Connect your repository to Vercel and deploy.

---

## Usage

- **Home Page:** View all uploaded identities and images.
- **Upload Page:** Add new faces by uploading images and specifying a name.
- **Webcam Page:** Start the webcam and perform real-time face recognition.

---

## Prerequisites

- Python 3.7+
- pip
- [face_recognition](https://github.com/ageitgey/face_recognition)
- OpenCV (`opencv-python`)
- Flask
- SQLAlchemy

All dependencies are listed in `requirements.txt`.

---

## Security & Production Notes

- Do **not** use `app.run(debug=True)` in production.
- Use a WSGI server (e.g., Gunicorn) for non-serverless deployments.
- Remove any debug or test routes before deploying.
- For Vercel, do **not** specify host or port in your Flask code.
- Store sensitive configuration in environment variables.

---

## Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition)
- [OpenCV](https://opencv.org/)
- Flask, SQLAlchemy, and the Python community

---



