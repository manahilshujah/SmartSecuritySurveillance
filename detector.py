import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open webcam
camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    # Flip the frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)

    if not success:
        print("Unable to access camera.")
        break

    # Run YOLO detection
    results = model(frame, conf=0.6)

    # Count the number of people detected
    person_count = 0

    # Loop through all detected objects
    for box in results[0].boxes:

        # Get class ID
        class_id = int(box.cls[0])

        # Get confidence score
        confidence = float(box.conf[0])

        # Convert class ID to object name
        class_name = model.names[class_id]

        # Print detection information
        print("---------------------------")
        print("Object:", class_name)
        print(f"Confidence: {confidence:.2f}")

        # Count only people
        if class_name == "person":
            person_count += 1

    # Print total number of people detected
    print(f"People detected: {person_count}")
    print("===================================")

    # Draw bounding boxes and labels
    annotated_frame = results[0].plot()

    # Display the webcam feed
    cv2.imshow("YOLO Object Detection", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
camera.release()
cv2.destroyAllWindows()