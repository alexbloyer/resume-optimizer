from flask import Flask, render_template, request, redirect, url_for, flash
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "263a8233986c09fdda317eba81cd8eba"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle Resume
        resume_text = request.form.get("resume_text", "").strip()
        resume_file = request.files.get("resume_file")
        resume_data = ""

        if resume_file and allowed_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            resume_file.save(file_path)
            resume_data = extract_text_from_pdf(file_path)
            os.remove(file_path)
        elif resume_text:
            resume_data = resume_text

        # Handle Job Description
        job_text = request.form.get("job_text", "").strip()
        job_file = request.files.get("job_file")
        job_data = ""

        if job_file and allowed_file(job_file.filename):
            filename = secure_filename(job_file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            job_file.save(file_path)
            job_data = extract_text_from_pdf(file_path)
            os.remove(file_path)
        elif job_text:
            job_data = job_text

        # Validate on server too
        if not resume_data or not job_data:
            flash("You must provide both a resume and job description (file or text).")
            return redirect(url_for("index"))

        # 🔍 Placeholder for model analysis
        match_score = analyze_resume_job_fit(resume_data, job_data)

        return render_template("result.html", match_score=match_score)

    return render_template("index.html")

def analyze_resume_job_fit(resume, job):
    # Placeholder analysis logic: word match ratio
    resume_words = set(resume.lower().split())
    job_words = set(job.lower().split())
    overlap = resume_words.intersection(job_words)
    score = len(overlap) / len(job_words) * 100 if job_words else 0
    return round(score, 2)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
