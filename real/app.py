from flask import Flask, request, render_template, send_file
import os
from rera_generator import generate_rera_pdf
from supabase import create_client, Client

SUPABASE_URL = "https://mhwzuwfksmijharsffax.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1od3p1d2Zrc21pamhhcnNmZmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI5NzMyNjgsImV4cCI6MjA5ODU0OTI2OH0.1vBgkEO5K463Fo0nbLCzYtTpbgQL1rBAtXNB_1ve4s8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    project_name = request.form.get('project_name', 'G.H.I. CITY Phase 2')
    rera_id = request.form.get('rera_id', 'UPRERAPRJ937180')
    builder_name = request.form.get('builder_name', 'CZAR Buildcon Pvt. Ltd.')
    image_file = request.files.get('image')
    
    if not image_file or image_file.filename == '':
        return "No image provided", 400
        
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    image_file.save(image_path)
    
    output_filename = os.path.join(OUTPUT_FOLDER, f"RERA_{rera_id}.pdf")
    
    try:
        generate_rera_pdf(project_name, rera_id, builder_name, image_path, output_filename)
        
        # Supabase Integration
        try:
            # 1. Upload to Storage bucket
            with open(output_filename, 'rb') as f:
                supabase.storage.from_("rera-documents").upload(
                    path=f"RERA_{rera_id}.pdf",
                    file=f,
                    file_options={"content-type": "application/pdf", "x-upsert": "true"}
                )
            
            # 2. Insert to Database table
            supabase.table("rera_submissions").insert({
                "project_name": project_name,
                "rera_id": rera_id,
                "builder_name": builder_name,
                "pdf_url": f"{SUPABASE_URL}/storage/v1/object/public/rera-documents/RERA_{rera_id}.pdf"
            }).execute()
        except Exception as sb_err:
            print(f"Supabase sync warning: {sb_err}")
            
        return send_file(output_filename, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Run Flask server
    app.run(host='127.0.0.1', port=5000, debug=False)
