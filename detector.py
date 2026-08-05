import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from database import initialize_database, insert_detection

# ==========================
# Load YOLO Model
# ==========================
model = YOLO("yolov8n.pt")

# ==========================
# Load Face Detector (Haar Cascade)
# ==========================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Check if the face detector loaded correctly
if face_cascade.empty():
    print("Error: Face detector could not be loaded!")
    exit()

# ==========================
# Open Webcam
# ==========================
camera = cv2.VideoCapture(0)

# ==========================
# Create Required Folders
# ==========================
os.makedirs("screenshots", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("faces", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# ==========================
# Initialize Database
# ==========================
initialize_database()

# ==========================
# Surveillance Settings
# ==========================
SAVE_INTERVAL = 5          # Save screenshot every 5 seconds
CLEAR_DELAY = 3            # Wait 3 seconds before declaring area cleared

last_save_time = 0
last_person_time = time.time()

# Save face every 2 seconds to avoid thousands of images
FACE_SAVE_INTERVAL = 2
last_face_save = 0

person_present = False

# ==========================
# Video Recording
# ==========================
recording = False
video_writer = None
video_filename = ""

# ==========================
# Main Loop
# ==========================
while True:

    success, frame = camera.read()

    if not success:
        print("Unable to access camera.")
        break

    # Mirror effect
    frame = cv2.flip(frame, 1)

    # ==========================
    # YOLO Person Detection
    # ==========================
    results = model(frame, conf=0.6, verbose=False)

    annotated_frame = results[0].plot()

    # ==========================
    # Face Detection
    # ==========================
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    # Draw face boxes
    for (x, y, w, h) in faces:

        cv2.rectangle(
            annotated_frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Save cropped face every few seconds
        if time.time() - last_face_save >= FACE_SAVE_INTERVAL:

            face = frame[y:y+h, x:x+w]

            face_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            face_filename = f"faces/face_{face_timestamp}.jpg"

            cv2.imwrite(face_filename, face)

            last_face_save = time.time()

            print(f"[FACE] Saved: {face_filename}")

    # ==========================
    # Person Detection
    # ==========================
    person_count = 0
    highest_confidence = 0.0

    for box in results[0].boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[class_id]

        if class_name == "person":

            person_count += 1

            if confidence > highest_confidence:
                highest_confidence = confidence

            print("----------------------------")
            print("Object:", class_name)
            print(f"Confidence: {confidence:.2f}")

    print(f"People detected: {person_count}")
    print(f"Faces detected: {len(faces)}")
    print("============================")

    current_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_clock = datetime.now().strftime("%H:%M:%S")

    # ==========================
    # Person Detected
    # ==========================
    if person_count > 0:

        last_person_time = current_time

        if not person_present:

            person_present = True
            last_save_time = current_time

            # Start video recording
            if not recording:

               video_filename = f"videos/video_{timestamp}.avi"
               fourcc = cv2.VideoWriter_fourcc(*"XVID")
               fps = 20

               height, width = annotated_frame.shape[:2]

               video_writer = cv2.VideoWriter(
                    video_filename,
                    fourcc,
                    fps,
                    (width, height)
                )

               recording = True

               print("[VIDEO] Recording started")

            filename = f"screenshots/person_{timestamp}.jpg"

            cv2.imwrite(filename, annotated_frame)

            print("[EVENT] Person detected")
            print("Screenshot saved:", filename)

            with open("logs/detection_log.txt", "a") as file:
                file.write(
                    f"{datetime.now()} | Person Detected | "
                    f"People: {person_count} | "
                    f"Confidence: {highest_confidence:.2f} | "
                    f"Image: {filename}\n"
                )

            insert_detection(
                current_date,
                current_clock,
                "Person Detected",
                person_count,
                highest_confidence,
                filename,
                video_filename
            )

        elif current_time - last_save_time >= SAVE_INTERVAL:

            last_save_time = current_time

            filename = f"screenshots/person_{timestamp}.jpg"

            cv2.imwrite(filename, annotated_frame)

            print("[EVENT] Person still present")
            print("Screenshot saved:", filename)

            with open("logs/detection_log.txt", "a") as file:
                file.write(
                    f"{datetime.now()} | Person Still Present | "
                    f"People: {person_count} | "
                    f"Confidence: {highest_confidence:.2f} | "
                    f"Image: {filename}\n"
                )

            insert_detection(
                current_date,
                current_clock,
                "Person Still Present",
                person_count,
                highest_confidence,
                filename,
                video_filename
            )

    # ==========================
    # Area Cleared
    # ==========================
    elif person_present:

        if current_time - last_person_time >= CLEAR_DELAY:

            person_present = False

            filename = f"screenshots/area_cleared_{timestamp}.jpg"

            cv2.imwrite(filename, annotated_frame)

            print("[EVENT] Area cleared")
            print("Screenshot saved:", filename)

            with open("logs/detection_log.txt", "a") as file:
                file.write(
                    f"{datetime.now()} | Area Cleared | "
                    f"Image: {filename}\n"
                )

            insert_detection(
                current_date,
                current_clock,
                "Area Cleared",
                0,
                0.0,
                filename,
                video_filename
            )
    if recording:
        video_writer.write(annotated_frame)
        if current_time - last_person_time >= CLEAR_DELAY:
            person_present = False
            if recording:

               recording = False

               video_writer.release()

               video_writer = None

               print("[VIDEO] Recording stopped")
               print("[VIDEO] Saved:", video_filename)
    # ==========================
    # Display Output
    # ==========================
    cv2.imshow("Smart Security Surveillance System", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==========================
# Cleanup
# ==========================
if video_writer is not None:
    video_writer.release()

camera.release()
cv2.destroyAllWindows()