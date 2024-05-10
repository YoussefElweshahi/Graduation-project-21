import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-7a66f-default-rtdb.firebaseio.com/"
})


ref = db.reference('Students')

data = {
    "90364":
        {
            "name": "Abdelfattah Ashraf",
            "ID": 90364,
            "major": "AI",
            "starting_year" : 2020,
            "total_attendance": 6, 
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2024-3-10  02:53:00"
        },
    "90365":
        {
            "name": "Ebrahim Azzmy",
            "ID":90365,
            "major": "CS",
            "starting_year" : 2020,
            "total_attendance": 6, 
            "standing": "V.G",
            "year": 4,
            "last_attendance_time": "2024-3-10  02:54:05"
        },
    "98048":
        {
            "name": "Youssef Elweshahy",
            "ID":98048,
            "major": "AI",
            "starting_year" : 2020,
            "total_attendance": 6, 
            "standing": "V.G",
            "year": 4,
            "last_attendance_time": "2024-3-10  02:55:10"
        },
    "20001609":
        {
            "name": "Ali Khaled",
            "ID": 20001609,
            "major": "AI",
            "starting_year" : 2020,
            "total_attendance": 6, 
            "standing": "V.G",
            "year": 4,
            "last_attendance_time": "2024-3-10  02:55:10"
        }
}

for key, value in data.items():
    ref.child(key).set(value)