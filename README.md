# AWS Backup & Disaster Recovery System

A cloud-based backup management application built with a Flask backend and AWS services.

## Architecture

User → S3-hosted/frontend → EC2 Flask backend → Amazon S3 + Amazon RDS → Amazon SNS notifications

## AWS Services

- Amazon S3 - file storage and static website hosting
- Amazon EC2 - backend/application hosting
- Amazon RDS - MySQL database for file metadata
- Amazon SNS - backup notifications

## Technology Stack

- HTML
- CSS
- JavaScript
- Python
- Flask
- MySQL
- Boto3
- AWS

## Features

- Login page
- File upload to S3
- File listing from S3
- Backup operation endpoint
- SNS notification
- RDS metadata storage
- Dashboard statistics
- Health endpoint

## Local Setup

1. Install Python 3.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure your AWS/RDS values.
4. Create the database using `schema.sql`.
5. Run:

```bash
python app.py
```

6. Open:

```text
http://localhost:5000
```

## AWS Deployment Notes

The application can be hosted on an EC2 instance. S3 is used for object storage, RDS for MySQL metadata, and SNS for notifications.

Do not commit AWS credentials, database passwords, or `.env` files to GitHub. Use IAM roles/environment variables instead.

## Project Basis

This implementation follows the architecture and technology stack documented in the project report: HTML/CSS/JavaScript frontend, Python Flask backend, Amazon S3 storage, Amazon EC2 hosting, Amazon RDS database integration, and Amazon SNS notifications.
