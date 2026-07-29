import cv2

# Open the default webcam (0 = built-in camera)
camera = cv2.VideoCapture(0)

while True:
    # Read one frame from the webcam
    success, frame = camera.read()
    frame = cv2.flip(frame, 1)

    # If the camera couldn't provide a frame, stop
    if not success:
        print("Error: Could not read from the camera.")
        break

    # Display the frame
    cv2.imshow("Smart Security Surveillance System", frame)

    # Exit when the user presses the Q key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
camera.release()
cv2.destroyAllWindows()