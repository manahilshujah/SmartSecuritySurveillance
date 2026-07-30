import cv2

camera = cv2.VideoCapture(0)

printed = False

while True:
    success, frame = camera.read()
    frame = cv2.flip(frame, 1)


    if not success:
        print("Unable to access camera.")
        break

    # Print information only once
    if not printed:
        print("Type:", type(frame))
        print("Shape:", frame.shape)
        print("Data Type:", frame.dtype)
        print("Top-left pixel:", frame[0, 0])
        printed = True

    cv2.imshow("Smart Security Surveillance", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()