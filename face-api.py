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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตให้ทุก origin เข้าถึงได้
    allow_methods=["*"],  # อนุญาตให้ทุก method ใช้ได้
    allow_headers=["*"],  # อนุญาตให้ทุก headers ใช้ได้
)

UPLOAD_FOLDER = "uploads" 

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

known_face_names = []
known_face_encodings = []

faces_file = 'faces.p'
if os.path.exists(faces_file):
    known_face_names, known_face_encodings = pickle.load(open(faces_file, 'rb'))

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("static/index.html", "r") as f:
        return f.read()

uploaded_images = []

@app.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{image.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    uploaded_images.append(image.filename)

    return JSONResponse(content={"success": True, "image_name": image.filename, "image_url": f"/uploads/{image.filename}"})

@app.get("/get_uploaded_images")
async def get_uploaded_images():
    image_list = [{"name": image, "url": f"/uploads/{image}"} for image in uploaded_images]
    return JSONResponse(content=image_list)

@app.post("/compare_face")
async def compare_face(compare_image: UploadFile = File(...)):
    data = await compare_image.read()
    img = Image.open(io.BytesIO(data))

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
