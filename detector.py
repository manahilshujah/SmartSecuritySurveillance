import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO

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
# Surveillance Settings
# ==========================
SAVE_INTERVAL = 5  # seconds

last_save_time = 0
person_present = False

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

    # Run YOLO
    results = model(frame, conf=0.6)

    # Draw detections
    annotated_frame = results[0].plot()

    # Count people
    person_count = 0

    # --------------------------
    # Process detections
    # --------------------------
    for box in results[0].boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[class_id]

        if class_name == "person":

            person_count += 1

            print("----------------------------")
            print("Object:", class_name)
            print(f"Confidence: {confidence:.2f}")

    print(f"People detected: {person_count}")
    print("============================")

    current_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ============================================================
    # EVENT 1 : Person enters
    # ============================================================
    if person_count > 0 and not person_present:

        person_present = True
        last_save_time = current_time

        filename = f"screenshots/person_{timestamp}.jpg"

        cv2.imwrite(filename, annotated_frame)

        print(f"[EVENT] Person detected")
        print(f"Screenshot saved: {filename}")

        with open("logs/detection_log.txt", "a") as file:
            file.write(f"{datetime.now()} : Person detected\n")

    # ============================================================
    # EVENT 2 : Person still present
    # ============================================================
    elif person_count > 0 and person_present:

        if current_time - last_save_time >= SAVE_INTERVAL:

            last_save_time = current_time

            filename = f"screenshots/person_{timestamp}.jpg"

            cv2.imwrite(filename, annotated_frame)

            print(f"[EVENT] Person still present")
            print(f"Screenshot saved: {filename}")

            with open("logs/detection_log.txt", "a") as file:
                file.write(f"{datetime.now()} : Person still present\n")

    # ============================================================
    # EVENT 3 : Area cleared
    # ============================================================
    elif person_count == 0 and person_present:

        person_present = False

        filename = f"screenshots/area_cleared_{timestamp}.jpg"

        cv2.imwrite(filename, annotated_frame)

        print("[EVENT] Area cleared")
        print(f"Screenshot saved: {filename}")

        with open("logs/detection_log.txt", "a") as file:
            file.write(f"{datetime.now()} : Area cleared\n")

    # Display output
    cv2.imshow("Smart Security Surveillance System", annotated_frame)

    # Exit on Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==========================
# Cleanup
# ==========================
camera.release()
cv2.destroyAllWindows()