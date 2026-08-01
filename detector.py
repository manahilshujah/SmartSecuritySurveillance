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
# Open Webcam
# ==========================
camera = cv2.VideoCapture(0)

# ==========================
# Create Required Folders
# ==========================
os.makedirs("screenshots", exist_ok=True)
os.makedirs("logs", exist_ok=True)

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

person_present = False

# ==========================
# Main Loop
# ==========================
while True:

    success, frame = camera.read()

    if not success:
        print("Unable to access camera.")
        break

    frame = cv2.flip(frame, 1)

    # Run YOLO
    results = model(frame, conf=0.6, verbose=False)

    annotated_frame = results[0].plot()

    person_count = 0
    highest_confidence = 0.0

    # ----------------------------------
    # Process detections
    # ----------------------------------
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
    print("============================")

    current_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_clock = datetime.now().strftime("%H:%M:%S")

    # ==========================
    # Person detected
    # ==========================
    if person_count > 0:

        last_person_time = current_time

        if not person_present:

            person_present = True
            last_save_time = current_time

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
                filename
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
                filename
            )

    # ==========================
    # Area cleared
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
                filename
            )

    cv2.imshow("Smart Security Surveillance System", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()