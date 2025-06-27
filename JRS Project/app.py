from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import docx
import http.client
import json


app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
JSEARCH_API_KEY = "01ecd28bdcmshea87ae44c3cc1d0p19dcd9jsn84b2f423a2dc"  # Replace with your actual key
JSEARCH_HOST = "jsearch.p.rapidapi.com"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# JSearch API Headers
headers = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": JSEARCH_HOST
}

# Helper Functions (keep your existing file handling and resume processing functions)

def search_jobs_v2(query, location=None, page=1, num_pages=1, country="us", date_posted="all"):
    """Search jobs using JSearch API with http.client"""
    conn = http.client.HTTPSConnection(JSEARCH_HOST)
    query_params = f"query={query.replace(' ', '%20')}&page={page}&num_pages={num_pages}&country={country}&date_posted={date_posted}"
    if location:
        query_params += f"&location={location.replace(' ', '%20')}"
    
    try:
        conn.request("GET", f"/search?{query_params}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Search Jobs Error: {e}")
        return None
    finally:
        conn.close()

def get_job_details_v2(job_id, country="us"):
    """Get detailed job information using http.client"""
    conn = http.client.HTTPSConnection(JSEARCH_HOST)
    try:
        conn.request("GET", f"/job-details?job_id={job_id}&country={country}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Job Details Error: {e}")
        return None
    finally:
        conn.close()

def get_salary_estimate_v2(job_title, location, location_type="ANY", years_of_experience="ALL"):
    """Get salary estimates using http.client"""
    conn = http.client.HTTPSConnection(JSEARCH_HOST)
    try:
        params = {
            "job_title": job_title.replace(' ', '%20'),
            "location": location.replace(' ', '%20'),
            "location_type": location_type,
            "years_of_experience": years_of_experience
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        conn.request("GET", f"/estimated-salary?{query_string}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Salary Estimate Error: {e}")
        return None
    finally:
        conn.close()

# Update your existing routes to use the new functions:

@app.route('/api/jobs/search')
def job_search():
    query = request.args.get('query', 'developer')
    location = request.args.get('location')
    page = request.args.get('page', 1, type=int)
    
    result = search_jobs_v2(
        query=query,
        location=location,
        page=page
    )
    
    if result is None:
        return jsonify({"error": "Failed to fetch jobs"}), 500
    
    return jsonify(result)

@app.route('/api/jobs/<job_id>')
def job_details(job_id):
    result = get_job_details_v2(job_id=job_id)
    
    if result is None:
        return jsonify({"error": "Failed to fetch job details"}), 500
    
    return jsonify(result)

@app.route('/api/jobs/salary-estimate')
def salary_estimate():
    job_title = request.args.get('job_title', 'developer')
    location = request.args.get('location', 'New York')
    
    result = get_salary_estimate_v2(
        job_title=job_title,
        location=location
    )
    
    if result is None:
        return jsonify({"error": "Failed to fetch salary estimate"}), 500
    
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resume')  # Changed from '/resume'
def upload_resume():
    return render_template('resume.html')  # Make sure this matches your actual template name

# Keep your existing resume upload route (update it to use the new search function if needed)

if __name__ == '__main__':
    app.run(debug=True)