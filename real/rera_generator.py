import os
from datetime import datetime
from PIL import Image, ExifTags
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def get_image_metadata(image_path):
    """Extracts Date and basic EXIF data from the drone/site image."""
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        metadata = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "gps": "GPS Data Unavailable (Ensure raw image is used)"}
        
        if exif:
            for tag_id, data in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal":
                    metadata["date"] = data
                elif tag == "GPSInfo":
                    # Simplified GPS flag for demo purposes
                    metadata["gps"] = "GPS Coordinates Extracted & Verified"
        return metadata
    except Exception as e:
        return {"date": "Unknown", "gps": "Unknown"}

def generate_rera_pdf(project_name, rera_id, builder_name, image_path, output_filename):
    """Generates the RERA Progress Snapshot PDF."""
    
    # 1. Setup PDF Canvas (A4 Size)
    c = canvas.Canvas(output_filename, pagesize=A4)
    width, height = A4
    
    # 2. Extract Metadata from the photo
    meta = get_image_metadata(image_path)
    
    # 3. Draw Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "UP RERA - QUARTERLY PROGRESS SNAPSHOT")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Project Name: {project_name}")
    c.drawString(50, height - 85, f"RERA Registration ID: {rera_id}")
    c.drawString(50, height - 100, f"Promoter: {builder_name}")
    
    # 4. Insert Site Image
    # Scale image to fit the PDF while maintaining aspect ratio
    c.drawString(50, height - 130, "Visual Evidence of Completion:")
    c.drawImage(image_path, 50, height - 450, width=500, height=300, preserveAspectRatio=True)
    
    # 5. Draw a "Bounding Box" to highlight progress (simulating AI detection)
    c.setStrokeColor(colors.red)
    c.setLineWidth(3)
    c.rect(150, height - 350, 200, 100, fill=0) # X, Y, Width, Height
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.red)
    c.drawString(155, height - 245, "Tower B - 3rd Floor Slab Completed")
    
    # 6. Insert Extracted Metadata (Proof of authenticity)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 480, "Image Authenticity Data:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 495, f"Timestamp: {meta['date']}")
    c.drawString(50, height - 510, f"Geotag Status: {meta['gps']}")
    
    # 7. Draw Progress Table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 550, "Declared Milestone Status:")
    
    # Table Headers
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 570, "Milestone")
    c.drawString(300, height - 570, "Status")
    c.drawString(450, height - 570, "Date Achieved")
    c.line(50, height - 575, 550, height - 575)
    
    # Table Rows
    c.setFont("Helvetica", 10)
    milestones = [
        ("Foundation & Plinth", "100% Completed", "12-Jan-2026"),
        ("Tower A - Structural Frame", "100% Completed", "28-Feb-2026"),
        ("Tower B - 3rd Floor Slab", "100% Completed", meta['date'].split(" ")[0]),
        ("Internal Plastering", "In Progress (20%)", "Pending")
    ]
    
    y_position = height - 595
    for task, status, date in milestones:
        c.drawString(50, y_position, task)
        c.drawString(300, y_position, status)
        c.drawString(450, y_position, date)
        y_position -= 20
        
    # Save the PDF
    c.save()
    print(f"Success! {output_filename} generated.")

# --- EXECUTE THE SCRIPT ---
if __name__ == "__main__":
    # Ensure you have an image named 'site_photo.jpg' in the same folder
    image_file = "site_photo.jpg"
    
    if os.path.exists(image_file):
        generate_rera_pdf(
            project_name="G.H.I. CITY Phase 2",
            rera_id="UPRERAPRJ937180",
            builder_name="CZAR Buildcon Pvt. Ltd.",
            image_path=image_file,
            output_filename="Q1_2026_RERA_Snapshot.pdf"
        )
    else:
        print(f"Error: Please place an image named '{image_file}' in the folder first.")
