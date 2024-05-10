import cv2 
import os
import pickle
import face_recognition
import numpy as np
import time
import cvzone 
from datetime import datetime
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


# Capture video from webcam (index 0 or 1 for multiple cameras)
cap = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Cannot open webcam. Please check if it's connected.")
    exit()


# Set frame width and height
cam_width = 480
cam_height = 640
cap.set(3, cam_width)
cap.set(4,  cam_height)

# overlay the webcam
imgBackground = cv2.imread('Resources/background.png')

# Import mode images to a list
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))


# Loading the encodingFile
print("Loading Encode File...")
encodeFile = open("EncodeFile.p", 'rb')
encodingListKnownWithIds = pickle.load(encodeFile)
encodeFile.close()
encodeListKnown, studentIds = encodingListKnownWithIds
print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []


while True:
    # Read a frame from the webcam
    success, img = cap.read()

    # scale the image down for minimize the computational power 1/4
    imgSized = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSized = cv2.cvtColor(imgSized, cv2.COLOR_BGR2RGB)

    # Face in the current frame
    faceCurFrame = face_recognition.face_locations(imgSized)
    # Encoding in the current frame -- find the location of the face then we compare the encodings
    encodeCurFrame = face_recognition.face_encodings(imgSized, faceCurFrame)

    # Check if frame is read successfully
    if not success:
        print("Error: Failed to read frame from webcam.")
        break

    imgBackground[180:180 + cam_width, 75:75 + cam_height] = img

    # overlay Modes
    x_offset = 814
    y_offset = 0
    imgBackground[y_offset:y_offset+imgModeList[modeType].shape[0],
                  x_offset:x_offset+imgModeList[modeType].shape[1]] = imgModeList[modeType]


    if faceCurFrame:
    
    # Loop through EncodingsFile -- zip for not 3.running two loops
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            # the less distance the better
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches) #
            # print("face distance", faceDis) #

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex) #

            if matches[matchIndex]:
                # print("Known face Detected")
                # print(studentIds[matchIndex])
                # ##################### rectangle of detection
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 80 + x1, 20 + y2, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                id = studentIds[matchIndex]

                # for view modes
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 480))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)

                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Get the Image from storage
                bucket = storage.bucket()
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update Data of attendance
                dateTimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                "%Y-%m-%d %H:%M:%S")
                secElapsed = (datetime.now()-dateTimeObject).total_seconds()
                print(secElapsed)

                if secElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(
                        studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[y_offset:y_offset+imgModeList[modeType].shape[0],
                        x_offset:x_offset+imgModeList[modeType].shape[1]] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[y_offset:y_offset+imgModeList[modeType].shape[0],
                            x_offset:x_offset+imgModeList[modeType].shape[1]] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['name']),
                                (1003, 555),  # location
                                cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['ID']),
                                (1003, 590),  # location
                                cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']),
                                (930, 180),  # location
                                cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                (255, 255, 255), 1)

                    imgBackground[266:266 + 216, 950:950 + 216] = imgStudent
                    # time.sleep(3)
            counter += 1

            if counter >= 20:
                counter = 0
                # time.sleep(3)
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[y_offset:y_offset+imgModeList[modeType].shape[0],
                            x_offset:x_offset+imgModeList[modeType].shape[1]] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    #     imgBackground[y_offset:y_offset+imgModeList[modeType].shape[0],
    #                         x_offset:x_offset+imgModeList[modeType].shape[1]] = imgModeList[modeType]
    # # Display the webcam view
    # cv2.imshow("WebCam", img)
    # Display the program with our background
    cv2.imshow("Face Attendance", imgBackground)

    # Exit the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam resources
cap.release()



# Close all open windows
cv2.destroyAllWindows()
