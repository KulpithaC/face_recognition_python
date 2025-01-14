from PIL import Image, ImageDraw
import face_recognition
import numpy as np
import pickle

known_faces = [
    ('Lisa', 'lisa.jpg'),
    ('Jennie', 'jennie.jpg'),
    ('Rose', 'rose.jpg'),
    ('Jisoo', 'jisoo.jpg')
]

known_face_names = []
known_face_encodings = []
for face in known_faces:
    known_face_names.append(face[0])
    face_image = face_recognition.load_image_file(face[1])
    face_encoding = face_recognition.face_encodings(face_image)[0]
    known_face_encodings.append(face_encoding)


# print(known_face_names)
# print(known_face_encodings)
 
pickle.dump((known_face_names, known_face_encodings), open('faces.p', 'wb'))
