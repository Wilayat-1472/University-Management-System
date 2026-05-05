"""Quick integration test for Phase 3 Verification Engine."""
import requests
import json

BASE = "http://localhost:8000/api/v1"

def register_and_login(username, email, password, role_id):
    r = requests.post(f"{BASE}/auth/register", json={
        "username": username, "email": email, "password": password, "role_id": role_id
    })
    if r.status_code not in (200, 201):
        print(f"  Register {username}: {r.status_code} - {r.text}")
    r = requests.post(f"{BASE}/auth/login", data={
        "username": username, "password": password
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ---------- Setup ----------
print("=== Setting up users ===")
admin_headers = register_and_login("testadmin", "testadmin@ums.edu", "pass123", 3)
instructor_headers = register_and_login("dr_smith", "smith@ums.edu", "pass123", 2)
student_headers = register_and_login("john_doe", "john@ums.edu", "pass123", 1)

# ---------- Create course with geofencing ----------
print("\n=== Creating course with geo-coordinates ===")
# Coordinates: Islamabad (roughly)
course = requests.post(f"{BASE}/courses/", json={
    "code": "CS301",
    "name": "Software Engineering",
    "latitude": 33.6844,
    "longitude": 73.0479,
    "allowed_radius": 200.0,
}, headers=instructor_headers).json()
print(f"  Course: {course['name']} (id={course['id']}, lat={course.get('latitude')}, lng={course.get('longitude')})")

# ---------- Enroll student ----------
print("\n=== Enrolling student ===")
enrollment = requests.post(f"{BASE}/courses/{course['id']}/enroll", headers=student_headers).json()
print(f"  Enrollment id={enrollment['id']}")

# ---------- Start session ----------
print("\n=== Starting attendance session ===")
session = requests.post(f"{BASE}/attendance/sessions", json={
    "course_id": course['id']
}, headers=instructor_headers).json()
print(f"  Session id={session['id']}, code={session['verification_code']}")

# ---------- Test 1: Mark attendance WITHIN radius ----------
print("\n=== Test 1: Student within radius (should be Present + Verified) ===")
record1 = requests.post(f"{BASE}/attendance/mark", json={
    "session_id": session['id'],
    "verification_code": session['verification_code'],
    "latitude": 33.6845,   # ~10m from course location
    "longitude": 73.0480,
    "is_mock_location": False,
    "device_id": "AA:BB:CC:DD:EE:FF"
}, headers=student_headers).json()
print(f"  Status: {record1['status']}, Verified: {record1['is_verified']}, Distance: {record1.get('distance_from_class')}m")

# ---------- Test 2: Heartbeat within radius ----------
print("\n=== Test 2: Heartbeat within radius ===")
hb = requests.post(f"{BASE}/attendance/heartbeat", json={
    "record_id": record1['id'],
    "latitude": 33.6844,
    "longitude": 73.0479,
}, headers=student_headers).json()
print(f"  Heartbeat id={hb['id']}, within_radius={hb['is_within_radius']}")

# ---------- Test 3: Heartbeat OUTSIDE radius ----------
print("\n=== Test 3: Heartbeat outside radius (should downgrade) ===")
hb2 = requests.post(f"{BASE}/attendance/heartbeat", json={
    "record_id": record1['id'],
    "latitude": 34.0000,   # Way off
    "longitude": 74.0000,
}, headers=student_headers).json()
print(f"  Heartbeat id={hb2['id']}, within_radius={hb2['is_within_radius']}")

# ---------- End session and check records ----------
print("\n=== Ending session and listing records ===")
ended = requests.put(f"{BASE}/attendance/sessions/{session['id']}/end", headers=instructor_headers).json()
print(f"  Session active: {ended['is_active']}")

records = requests.get(f"{BASE}/attendance/sessions/{session['id']}/records", headers=instructor_headers).json()
for r in records:
    print(f"  Record: student_id={r['student_id']}, status={r['status']}, verified={r['is_verified']}, distance={r.get('distance_from_class')}m")

# ---------- New session: Test mock location ----------
print("\n=== Test 4: New student with mock location (should be Absent) ===")
student2_headers = register_and_login("jane_doe", "jane@ums.edu", "pass123", 1)
requests.post(f"{BASE}/courses/{course['id']}/enroll", headers=student2_headers)

session2 = requests.post(f"{BASE}/attendance/sessions", json={
    "course_id": course['id']
}, headers=instructor_headers).json()

record_mock = requests.post(f"{BASE}/attendance/mark", json={
    "session_id": session2['id'],
    "verification_code": session2['verification_code'],
    "latitude": 33.6844,
    "longitude": 73.0479,
    "is_mock_location": True,
    "device_id": "FF:EE:DD:CC:BB:AA"
}, headers=student2_headers).json()
print(f"  Status: {record_mock['status']}, Verified: {record_mock['is_verified']}")

# ---------- Test 5: Outside radius attendance ----------
print("\n=== Test 5: Student outside radius (should be Remote) ===")
student3_headers = register_and_login("bob_jones", "bob@ums.edu", "pass123", 1)
requests.post(f"{BASE}/courses/{course['id']}/enroll", headers=student3_headers)

record_remote = requests.post(f"{BASE}/attendance/mark", json={
    "session_id": session2['id'],
    "verification_code": session2['verification_code'],
    "latitude": 34.0000,   # Far from Islamabad
    "longitude": 74.0000,
    "is_mock_location": False,
}, headers=student3_headers).json()
print(f"  Status: {record_remote['status']}, Verified: {record_remote['is_verified']}, Distance: {record_remote.get('distance_from_class')}m")

print("\n✅ All Phase 3 verification tests completed!")
