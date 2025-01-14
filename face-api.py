from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import face_recognition
import numpy as np
import pickle
import io
import os
from fastapi.encoders import jsonable_encoder
import shutil

# สร้าง FastAPI app
app = FastAPI()

# ตั้งค่า CORS เพื่อให้สามารถเข้าถึงจากทุกที่
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตให้ทุก origin เข้าถึงได้
    allow_methods=["*"],  # อนุญาตให้ทุก method ใช้ได้
    allow_headers=["*"],  # อนุญาตให้ทุก headers ใช้ได้
)

UPLOAD_FOLDER = "uploads"  # Folder where images will be stored

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# เสิร์ฟไฟล์ static เช่น HTML
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# Set default values for face recognition data if faces.p doesn't exist
known_face_names = []
known_face_encodings = []

# Load face data from pickle if it exists
faces_file = 'faces.p'
if os.path.exists(faces_file):
    known_face_names, known_face_encodings = pickle.load(open(faces_file, 'rb'))

# หน้า UI สำหรับอัปโหลดรูป
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("static/index.html", "r") as f:
        return f.read()

uploaded_images = []

@app.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    # Save uploaded image to the server
    file_location = f"{UPLOAD_FOLDER}/{image.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Add image name to the list of uploaded images
    uploaded_images.append(image.filename)

    return JSONResponse(content={"success": True, "image_name": image.filename, "image_url": f"/uploads/{image.filename}"})

@app.get("/get_uploaded_images")
async def get_uploaded_images():
    # Return the list of uploaded images with names and URLs
    image_list = [{"name": image, "url": f"/uploads/{image}"} for image in uploaded_images]
    return JSONResponse(content=image_list)

# สำหรับการอัปโหลดและเปรียบเทียบใบหน้า
@app.post("/compare_face")
async def compare_face(compare_image: UploadFile = File(...)):
    data = await compare_image.read()
    img = Image.open(io.BytesIO(data))

    # ใช้ face_recognition เพื่อดึงใบหน้า
    face_locations = face_recognition.face_locations(np.array(img))
    face_encodings = face_recognition.face_encodings(np.array(img), face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        else:
            name = "Unknown"
        face_names.append(name)

    return JSONResponse(content={"faces": face_names})

# รันแอป FastAPI ด้วยคำสั่ง: uvicorn <ชื่อไฟล์>:app --reload
