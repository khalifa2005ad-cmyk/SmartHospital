import cv2

# Open laptop camera
camera = cv2.VideoCapture(0)

# Load face detector
face_detector = cv2.CascadeClassifier()
face_detector.load(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Check camera
if not camera.isOpened():
    print("Camera not found!")
else:
    while True:
        success, frame = camera.read()

        if not success:
            break

        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        # Draw green rectangle
        for (x, y, w, h) in faces:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        # Show camera
        cv2.imshow("Smart Hospital - Face Detection", frame)

        # Press Q to close
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()