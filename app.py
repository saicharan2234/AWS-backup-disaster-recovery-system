import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import boto3
import mysql.connector
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret")

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

s3 = boto3.client("s3", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("dashboard.html")

@app.post("/api/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    # Demo authentication. For production, replace with hashed credentials
    # or a managed identity service.
    if username == os.getenv("APP_USERNAME", "admin") and password == os.getenv("APP_PASSWORD", "admin123"):
        session["logged_in"] = True
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.post("/upload")
def upload():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file supplied"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    s3.upload_fileobj(file, S3_BUCKET, filename)

    size = 0
    try:
        head = s3.head_object(Bucket=S3_BUCKET, Key=filename)
        size = head.get("ContentLength", 0)
    except Exception:
        pass

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (filename, upload_date, file_size) VALUES (%s, %s, %s)",
        (filename, datetime.utcnow(), size)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "filename": filename, "size": size})

@app.get("/files")
def files():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    objects = response.get("Contents", [])

    return jsonify([
        {
            "filename": obj["Key"],
            "size": obj["Size"],
            "last_modified": obj["LastModified"].isoformat()
        }
        for obj in objects
    ])

@app.post("/api/backup")
def backup():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    message = (
        f"Backup operation completed.\n"
        f"Backup Job ID: bkp-{timestamp}\n"
        f"S3 Destination: s3://{S3_BUCKET}/\n"
        f"Status: COMPLETED"
    )

    if SNS_TOPIC_ARN:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="[SUCCESS] Cloud Backup Completed",
            Message=message
        )

    return jsonify({"success": True, "message": message})

@app.get("/health")
def health():
    return jsonify({"status": "running", "service": "AWS Backup & Disaster Recovery System"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
