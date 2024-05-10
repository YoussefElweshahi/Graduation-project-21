import cv2
import face_recognition
import pickle
import os
# firebase imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-7a66f-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-7a66f.appspot.com"
})



# import the student images
folderPath = 'Images'
imgPathList = os.listdir(folderPath)
print(imgPathList)
imgList = []
studentIds = []
# importing the modes images into a list
for path in imgPathList:  # Iterate over the list of paths
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # for splitting the extension 
    studentIds.append(os.path.splitext(path)[0])
    
    # uploading images to database 
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    
    
print(studentIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # from BGR to RGB           open-cv(BGR)     face_recognition(RBB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList

print("Encoding Started....")
encodeListKnown = findEncodings(imgList)
# print(encodeListKnown)
# we need to save the names(IDs) with the encoding
encodingListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")


# Generate the pickle file
encodeFile = open("EncodeFile.p", 'wb')
pickle.dump(encodingListKnownWithIds, encodeFile)
encodeFile.close()
print("Encoding File Saved")