import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open webcam
camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()
    frame = cv2.flip(frame, 1)


    if not success:
        print("Unable to access camera.")
        break

    # Run YOLO detection
    results = model(frame, conf=0.6)

    # Draw detections
    annotated_frame = results[0].plot()

    # Display
    cv2.imshow("YOLO Object Detection", annotated_frame)

    # Exit on Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()